# Copyright 2025 The LiteRT LM Tools Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

"""The LLM pipeline based on LiteRT."""

import abc
import logging
import sys
import os
from typing import Optional, Sequence
from ai_edge_litert import interpreter as interpreter_lib
from litert_tools.pipeline import model_downloader as model_downloader_lib
from litert_tools.pipeline import task_file_processor as task_file_processor_lib
from litert_tools.pipeline import tokenizer as tokenizer_lib
import numpy as np
import sentencepiece as sp
import transformers


# The external entry point for preparing the ready-to-use LLM Pipeline.
def load(
    repo_id: str, model_name: str, tokenizer_location: Optional[str] = None
):
  """Loads the LLM pipeline.

  Args:
    repo_id: The repository ID.
    model_name: The name of the model.
    tokenizer_location: The path to the tokenizer.

  Returns:
    The loaded LLM pipeline or None if the model is not supported.
  """
  hf_model_downloader = model_downloader_lib.HuggingFaceDownloader()
  pipeline_loader = LiteRTLlmPipelineLoader(hf_model_downloader)
  return pipeline_loader.load(repo_id, model_name, tokenizer_location)


def local_load(
     file_path: str, tokenizer_location: Optional[str] = None
):
    """Loads the LLM pipeline from a local .task file.

    Args:
      file_path: The path to the .task file.
      tokenizer_location: The path to the tokenizer.

    Returns:
      The loaded LLM pipeline.
    """
    pipeline_loader = LiteRTLlmPipelineLoader()
    return pipeline_loader.local_load(file_path, tokenizer_location)


class LlmPipeline(abc.ABC):
  """Base class for LLM pipeline."""

  @abc.abstractmethod
  def generate(
      self, prompt: str, max_decode_steps: int | None = None, **kwargs
  ) -> str:
    """Generates text from the given prompt.

    Args:
      prompt: The input prompt.
      max_decode_steps: The maximum number of decode steps.
      **kwargs: The keyword arguments passed to the implementation class.

    Returns:
      The generated text.
    """
    raise NotImplementedError


# TODO: b/408003054 - Consolidate Python LiteRT LLM pipeline and eval pipeline.
class LiteRTLlmPipeline(LlmPipeline):
  """LiteRT LLM pipeline."""

  def __init__(
      self,
      interpreter: interpreter_lib.InterpreterWithCustomOps,
      tokenizer: tokenizer_lib.Tokenizer,
  ):
    """Initializes the pipeline.

    Args:
      interpreter: The TFLite interpreter.
      tokenizer: The tokenizer.
    """
    self._interpreter = interpreter
    self._tokenizer = tokenizer

    self._prefill_runner = None
    self._decode_runner = self._interpreter.get_signature_runner("decode")

  def _get_mask(self, shape: Sequence[int], k: int):
    """Gets the mask for the input to the model.

    Args:
      shape: The shape of the mask input to the model.
      k: All elements below the k-th diagonal are set to 0.

    Returns:
      The mask for the input to the model. All the elements in the mask are set
      to -inf except that all the elements below the k-th diagonal are set to 0.
    """
    mask = np.ones(shape, dtype=np.float32) * float("-inf")
    mask = np.triu(mask, k=k)
    return mask

  def _init_prefill_runner(self, num_input_tokens: int):
    """Initializes all the variables related to the prefill runner.

    This method initializes the following variables:
      - self._prefill_runner: The prefill runner based on the input size.
      - self._max_seq_len: The maximum sequence length supported by the model.

    Args:
      num_input_tokens: The number of input tokens.
    """
    if not self._interpreter:
      raise ValueError("Interpreter is not initialized.")

    self._prefill_runner = self._get_prefill_runner(num_input_tokens)
    # input_token_shape has shape (batch, max_seq_len)
    input_token_shape = self._prefill_runner.get_input_details()["tokens"][
        "shape"
    ]

    # TODO: b/395659171 - Remove this once the bug is fixed.
    if len(input_token_shape) == 1:
      self._max_seq_len = input_token_shape[0]
    else:
      self._max_seq_len = input_token_shape[1]

    # kv cache input has shape [batch=1, num_kv_heads, cache_size, head_dim].
    # There are two types of kv cache shapes:
    # 1. kv has the same shape as [batch=1, num_kv_heads, head_dim, cache_size]
    # 2. kv has different shape from where,
    #    - k has shape [batch=1, num_kv_heads, cache_size, head_dim]
    #    - v has shape [batch=1, num_kv_heads, head_dim, cache_size]
    # The first type is for models optimized for XNNPACK CPU, and the second
    # type is for unified models supported on CPU/GPU.
    #
    # Since the v cache shape is the same for both types, we can use it to
    # determine the max kv cache sequence length.
    v_cache_shape = self._prefill_runner.get_input_details()["kv_cache_v_0"][
        "shape"
    ]
    self._max_kv_cache_seq_len = v_cache_shape[3]

  def _init_kv_cache(self) -> dict[str, np.ndarray]:
    """Initializes the KV cache.

    Returns:
      A dictionary of KV cache tensors.
    """
    if self._prefill_runner is None:
      raise ValueError("Prefill runner is not initialized.")
    kv_cache = {}
    for input_key in self._prefill_runner.get_input_details().keys():
      if "kv_cache" in input_key:
        kv_cache[input_key] = np.zeros(
            self._prefill_runner.get_input_details()[input_key]["shape"],
            dtype=np.float32,
        )
        kv_cache[input_key] = np.zeros(
            self._prefill_runner.get_input_details()[input_key]["shape"],
            dtype=np.float32,
        )
    return kv_cache

  def _get_prefill_runner(self, num_input_tokens: int):
    """Gets the prefill runner with the best suitable input size.

    Args:
      num_input_tokens: The number of input tokens.

    Returns:
      The prefill runner with the smallest input size.
    """
    best_signature = None
    delta = sys.maxsize
    max_prefill_len = -1
    for key in self._interpreter.get_signature_list().keys():
      if "prefill" not in key:
        continue
      input_pos = self._interpreter.get_signature_runner(
          key
      ).get_input_details()["input_pos"]
      # input_pos["shape"] has shape (max_seq_len, )
      seq_size = input_pos["shape"][0]
      max_prefill_len = max(max_prefill_len, seq_size)
      if num_input_tokens <= seq_size and seq_size - num_input_tokens < delta:
        delta = seq_size - num_input_tokens
        best_signature = key
    if best_signature is None:
      raise ValueError(
          "The largest prefill length supported is %d, but we have %d number of"
          " input tokens" % (max_prefill_len, num_input_tokens)
      )
    return self._interpreter.get_signature_runner(best_signature)

  def _run_prefill(
      self,
      prefill_token_ids: Sequence[int],
  ) -> dict[str, np.ndarray]:
    """Runs prefill and returns the kv cache.

    Args:
      prefill_token_ids: The token IDs of the prefill input.

    Returns:
      The updated KV cache.
    """
    if not self._prefill_runner:
      raise ValueError("Prefill runner is not initialized.")
    prefill_token_length = len(prefill_token_ids)
    if prefill_token_length == 0:
      return self._init_kv_cache()

    # Prepare the input to be [1, max_seq_len].
    input_token_ids = [0] * self._max_seq_len
    input_token_ids[:prefill_token_length] = prefill_token_ids
    input_token_ids = np.asarray(input_token_ids, dtype=np.int32)
    input_token_ids = np.expand_dims(input_token_ids, axis=0)

    # Prepare the input position to be [max_seq_len].
    input_pos = [0] * self._max_seq_len
    input_pos[:prefill_token_length] = range(prefill_token_length)
    input_pos = np.asarray(input_pos, dtype=np.int32)

    # Initialize kv cache.
    prefill_inputs = self._init_kv_cache()
    # Prepare the tokens and input position inputs.
    prefill_inputs.update({
        "tokens": input_token_ids,
        "input_pos": input_pos,
    })
    if "mask" in self._prefill_runner.get_input_details().keys():
      # For prefill, mask has shape [batch=1, 1, seq_len, kv_cache_size].
      # We want mask[0, 0, i, j] = 0 for j<=i and -inf otherwise.
      prefill_inputs["mask"] = self._get_mask(
          shape=self._prefill_runner.get_input_details()["mask"]["shape"],
          k=1,
      )
    prefill_outputs = self._prefill_runner(**prefill_inputs)
    if "logits" in prefill_outputs:
      # Prefill outputs includes logits and kv cache. We only output kv cache.
      prefill_outputs.pop("logits")

    return prefill_outputs

  def _greedy_sampler(self, logits: np.ndarray) -> int:
    """Samples the next token using greedy sampling.

    Args:
      logits: The logits from the decoder.

    Returns:
      The next token ID.
    """
    return int(np.argmax(logits))

  def _run_decode(
      self,
      start_pos: int,
      start_token_id: int,
      kv_cache: dict[str, np.ndarray],
      max_decode_steps: int,
      print_text: bool = False,
  ) -> str:
    """Runs decode and outputs the token IDs from greedy sampler.

    Args:
      start_pos: The position of the first token of the decode input.
      start_token_id: The token ID of the first token of the decode input.
      kv_cache: The KV cache from the prefill.
      max_decode_steps: The maximum decode steps.
      print_text: Whether to print the decoded text to the console.

    Returns:
      The token IDs from the greedy sampler.
    """
    next_pos = start_pos
    next_token = start_token_id
    decode_text = []
    decode_inputs = kv_cache

    for i in range(max_decode_steps):
      # Check if the *previous* step generated an end token before decoding
      if i > 0 and self._tokenizer.is_end_token(next_token):
        break

      decode_inputs.update({
          "tokens": np.array([[next_token]], dtype=np.int32),
          "input_pos": np.array([next_pos], dtype=np.int32),
      })
      if "mask" in self._decode_runner.get_input_details().keys():
        # For decode, mask has shape [batch=1, 1, 1, kv_cache_size].
        # We want mask[0, 0, 0, j] = 0 for j<=next_pos and -inf otherwise.
        decode_inputs["mask"] = self._get_mask(
            shape=self._decode_runner.get_input_details()["mask"]["shape"],
            k=next_pos + 1,
        )
      decode_outputs = self._decode_runner(**decode_inputs)
      # Output logits has shape (batch=1, 1, vocab_size). We only take the first
      # element.
      logits = decode_outputs.pop("logits")[0][0]
      next_token = self._greedy_sampler(logits)

      # Decode the *current* next_token
      # Check for end token *after* sampling, before decoding/printing
      if self._tokenizer.is_end_token(next_token):
        break

      decoded_piece = self._tokenizer.decode_single_token(next_token)
      decode_text.append(decoded_piece)

      if print_text and decoded_piece:
        print(decoded_piece, end="", flush=True)

      # Decode outputs includes logits and kv cache. We already popped out
      # logits, so the rest is kv cache. We pass the updated kv cache as input
      # to the next decode step.
      decode_inputs = decode_outputs
      next_pos += 1

      # Check sequence length limits
      if next_pos >= self._max_kv_cache_seq_len:
        logging.warning("Maximum KV cache sequence length reached.")
        break

    if print_text:
      print(flush=True)  # print a new line at the end.
    return "".join(decode_text)

  def generate(
      self, prompt: str, max_decode_steps: int | None = None, **kwargs
  ) -> str:
    """Generates text from the given prompt.

    Args:
      prompt: The input prompt.
      max_decode_steps: The maximum number of decode steps.
      **kwargs: The keyword arguments. - print_text: Whether to print the
        decoded text to the console.

    Returns:
      The generated text.
    """
    token_ids = self._tokenizer.encode_with_prompt_template(prompt)
    print_text = kwargs.get("print_text", True)

    num_input_tokens = len(token_ids)

    # Initialize the prefill runner with the suitable input size.
    try:
      self._init_prefill_runner(num_input_tokens)
    except ValueError as e:
      logging.error("Failed to initialize prefill runner: %s", e)
      return f"Error: {e}"  # Or raise the exception

    if num_input_tokens > self._max_seq_len:
      logging.warning(
          "Input prompt length (%d) exceeds model's max prefill sequence length"
          " (%d). Truncating.",
          num_input_tokens,
          self._max_seq_len,
      )
      # Truncate from the left, keeping the end of the prompt which is usually
      # more important
      token_ids = token_ids[num_input_tokens - self._max_seq_len :]
      num_input_tokens = len(token_ids)
      # Re-initialize prefill runner in case truncation changed the required
      # size (though unlikely if it already failed the first check)
      self._init_prefill_runner(num_input_tokens)

    # Run prefill.
    # Prefill up to the second to the last token of the prompt, because the last
    # token of the prompt will be used to bootstrap decode.
    prefill_token_length = len(token_ids) - 1
    logging.info("Running prefill")
    kv_cache = self._run_prefill(token_ids[:prefill_token_length])

    # Run decode.
    logging.info("Running decode")
    max_possible_decode_steps = (
        self._max_kv_cache_seq_len - prefill_token_length - 1
    )
    if max_possible_decode_steps <= 0:
      logging.warning(
          "Maximum possible decode steps is zero. Returning empty string."
      )
      return ""

    actual_max_decode_steps = max_possible_decode_steps
    if max_decode_steps is not None:
      if max_decode_steps <= 0:
        logging.warning("max_decode_steps must be positive. Using default.")
      else:
        actual_max_decode_steps = min(
            max_possible_decode_steps, max_decode_steps
        )

    decode_text = self._run_decode(
        prefill_token_length,
        token_ids[prefill_token_length],
        kv_cache,
        actual_max_decode_steps,
        print_text=print_text,
    )
    return decode_text


class LlmPipelineLoader:
  """Base class for LLM pipeline loader."""

  def __init__(self, model_downloader: Optional[model_downloader_lib.ModelDownloader] = None):
    """Initializes the base class.

    Args:
      model_downloader: The model downloader.
    """
    # Store the downloader if needed by subclasses, otherwise this can be empty
    self.model_downloader = model_downloader

  def load(self, repo_id: str, filename: str, tokenizer_location: str):
    """Loads the LLM pipeline.

    Args:
      repo_id: The repository ID for the model.
      filename: The filename of the model within the repo.
      tokenizer_location: The path or repo ID for the tokenizer.
    """
    # Base class load method can be empty or raise NotImplementedError
    raise NotImplementedError
  
  def local_load(self, file_path: str, tokenizer_location: Optional[str] = None):
    """Loads the LiteRT LLM pipeline from a local .task file.

    Args:
        file_path: The path to the .task file.
        tokenizer_location: The path to the tokenizer.

    Returns:
        The LiteRT LLM pipeline.
    """
    # Base class load method can be empty or raise NotImplementedError
    raise NotImplementedError


class LiteRTLlmPipelineLoader(LlmPipelineLoader):
  """LiteRT LLM pipeline loader."""

  def _uses_hugging_face(self) -> bool:
    """Checks if the model is from Hugging Face."""
    return isinstance(
        self.model_downloader, model_downloader_lib.HuggingFaceDownloader
    )

  def load(
      self,
      repo_id: str,
      filename: str,
      tokenizer_location: Optional[str] = None,
  ) -> LiteRTLlmPipeline:
    """Loads the LiteRT LLM pipeline.

    Args:
      repo_id: The repository ID.
      filename: The filename of the model.
      tokenizer_location: The path to the tokenizer.

    Returns:
      The LiteRT LLM pipeline.
    """
    try:
      model_path = self.model_downloader.download_file(repo_id, filename)
    except Exception as e:
      logging.error(
          "Failed to download the model from %s/%s: %s",
          repo_id,
          filename,
          e,
      )
      raise

    try:
      if model_path and model_path.endswith(".task"):
        # Extract tflite, tokenizer and metadata from .task bundle
        file_processor = task_file_processor_lib.TaskFileProcessor(
            model_path, cache_dir=self.model_downloader.get_cache_dir()
        )
        model_path = file_processor.get_tflite_file_path()

        tokenizer_path = file_processor.get_tokenizer_file_path()
        raw_tokenizer = sp.SentencePieceProcessor()
        raw_tokenizer.Load(tokenizer_path)

        prompt_template = file_processor.get_prompt_template()
      elif tokenizer_location and self._uses_hugging_face():
        raw_tokenizer = transformers.AutoTokenizer.from_pretrained(
            tokenizer_location
        )
        prompt_template = None
    except Exception as e:
      logging.error(
          "Failed to obtain tokenizer from %s: %s",
          tokenizer_location,
          e,
      )
      raise

    # Wrap the loaded tokenizer
    tokenizer = tokenizer_lib.Tokenizer(raw_tokenizer, prompt_template)

    # Load the interpreter
    logging.info("Loading TFLite model from: %s", model_path)
    try:
      interpreter = interpreter_lib.InterpreterWithCustomOps(
          custom_op_registerers=["pywrap_genai_ops.GenAIOpsRegisterer"],
          model_path=model_path,
          num_threads=2,  # Consider making num_threads configurable
          experimental_default_delegate_latest_features=True,
      )
    except Exception as e:
      logging.error(
          "Failed to load TFLite interpreter from %s: %s", model_path, e
      )
      raise

    # Create and return the pipeline with the wrapped tokenizer
    pipeline = LiteRTLlmPipeline(interpreter, tokenizer)
    logging.info("LiteRTLlmPipeline loaded successfully.")
    return pipeline

  def local_load(self,
        file_path: str,
        tokenizer_location: Optional[str] = None,
    ) -> LiteRTLlmPipeline :
        """Loads the LiteRT LLM pipeline from a local .task file.

        Args:
            file_path: The path to the .task file.
            tokenizer_location: The path to the tokenizer.

        Returns:
            The LiteRT LLM pipeline.
        """
        logging.info("Loading LiteRTLlmPipeline from: %s", file_path)

        try:
            file_path = os.path.abspath(file_path)
            if file_path and file_path.endswith(".task"):
                file_processor = task_file_processor_lib.TaskFileProcessor(file_path=file_path, cache_dir=os.path.dirname(file_path))
                model_path = file_processor.get_tflite_file_path()

                tokenizer_path = file_processor.get_tokenizer_file_path()
                raw_tokenizer = sp.SentencePieceProcessor()
                raw_tokenizer.Load(tokenizer_path)

                prompt_template = file_processor.get_prompt_template()
                
            elif tokenizer_location:
                
                raw_tokenizer = transformers.AutoTokenizer.from_pretrained(
                    tokenizer_location
                )
                prompt_template = None
                model_path = file_path
        except Exception as e:
            logging.error(
                "Failed to obtain tokenizer from %s: %s",
                tokenizer_location,
                e,
            )
            raise


        # Wrap the loaded tokenizer
        tokenizer = tokenizer_lib.Tokenizer(raw_tokenizer, prompt_template)

        # Load the interpreter
        logging.info("Loading TFLite model from: %s", model_path)
        try:
            interpreter = interpreter_lib.InterpreterWithCustomOps(
                custom_op_registerers=["pywrap_genai_ops.GenAIOpsRegisterer"],
                model_path=model_path,
                num_threads=2,  # Consider making num_threads configurable
                experimental_default_delegate_latest_features=True,
        )
        except Exception as e:
            logging.error(
                "Failed to load TFLite interpreter from %s: %s", model_path, e
            )
            raise

        # Create and return the pipeline with the wrapped tokenizer
        pipeline = LiteRTLlmPipeline(interpreter, tokenizer)
        logging.info("LiteRTLlmPipeline loaded successfully.")
        return pipeline