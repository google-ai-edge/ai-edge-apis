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

"""A generic Tokenizer interface for the LLM pipeline."""

import logging
from typing import Any, Sequence, Union
import sentencepiece as sp


class Tokenizer:
  """A generic Tokenizer interface for the LLM pipeline.

  It hides the internal tokenizer, which can be either SentencePieceProcessor or
  transformers.AutoTokenizer.
  """

  def __init__(
      self, tokenizer: Union[sp.SentencePieceProcessor, Any]
  ):  # Use Any for AutoTokenizer
    self._tokenizer = tokenizer
    self._is_sentencepiece = isinstance(tokenizer, sp.SentencePieceProcessor)

    # Precompute end tokens for efficiency
    self._end_token_ids = self._compute_end_token_ids()

  def _compute_end_token_ids(self) -> set[int]:
    """Computes the set of end token IDs."""
    end_tokens = set()
    if self._is_sentencepiece:
      # Add common end tokens for SentencePiece
      end_tokens.add(self._tokenizer.PieceToId("<end_of_turn>"))
      end_tokens.add(self._tokenizer.PieceToId("<bos>"))
      if self._tokenizer.eos_id() != -1:  # Check if eos_id is valid
        end_tokens.add(self._tokenizer.eos_id())
    elif hasattr(self._tokenizer, "eos_token_id"):
      # Add EOS token for Transformers tokenizers
      if self._tokenizer.eos_token_id is not None:
        end_tokens.add(self._tokenizer.eos_token_id)
      # Add other potential end tokens if needed based on specific models
      # e.g., some models might use specific stop tokens in their
      # generation config
    return end_tokens

  def _apply_gemma3_chat_template(self, prompt: str) -> Sequence[int]:
    """Applies the Gemma3 chat template to the prompt."""
    token_ids = []
    # Add start token if specified. Start token needs to use `PieceToId` to
    # avoid tokenization issues. For example, '<bos>' can be wrongly tokenized
    # as ['<', 'bos', '>'] using `EncodeAsIds`.
    token_ids.append(self._tokenizer.PieceToId("<bos>"))
    token_ids.append(self._tokenizer.PieceToId("<start_of_turn>"))
    token_ids.extend(self._tokenizer.EncodeAsIds("user"))
    token_ids.append(self._tokenizer.PieceToId("\n"))
    # Add the prompt itself.
    token_ids.extend(self._tokenizer.EncodeAsIds(prompt))
    token_ids.append(self._tokenizer.PieceToId("<end_of_turn>"))
    token_ids.append(self._tokenizer.PieceToId("\n"))
    # Add model prefix
    token_ids.append(self._tokenizer.PieceToId("<start_of_turn>"))
    token_ids.extend(self._tokenizer.EncodeAsIds("model"))
    token_ids.append(self._tokenizer.PieceToId("\n"))
    return token_ids

  def encode_with_prompt_template(self, prompt: str) -> Sequence[int]:
    """Encodes the prompt with the appropriate chat/prompt template."""
    if self._is_sentencepiece:
      # TODO: b/401263824 - apply chat template from the litert-llm format
      # Here only use Gemma3 chat template (example)
      return self._apply_gemma3_chat_template(prompt)
    elif hasattr(self._tokenizer, "apply_chat_template"):
      # Use HuggingFace's chat template application
      messages = [{"role": "user", "content": prompt}]
      # Ensure add_generation_prompt=True to get the right format for inference
      return self._tokenizer.apply_chat_template(
          messages, tokenize=True, add_generation_prompt=True
      )
    elif hasattr(self._tokenizer, "encode"):
      # Fallback to basic encoding if no chat template method exists
      logging.warning(
          "Tokenizer does not have apply_chat_template. Using basic encode."
      )
      return self._tokenizer.encode(prompt)
    else:
      raise ValueError(
          "Unsupported tokenizer type for encoding with template: %s"
          % type(self._tokenizer).__name__
      )

  def decode_single_token(self, token_id: int) -> str:
    """Decodes a single token ID into a string."""
    if self.is_end_token(token_id):  # Avoid decoding special end tokens
      return ""
    if self._is_sentencepiece:
      return self._tokenizer.DecodeIds([token_id])
    elif hasattr(self._tokenizer, "decode"):
      # skip_special_tokens=True is important for incremental decoding
      return self._tokenizer.decode(token_id, skip_special_tokens=True)
    else:
      raise ValueError(
          "Unsupported tokenizer type for decoding: %s"
          % type(self._tokenizer).__name__
      )

  def is_end_token(self, token_id: int) -> bool:
    """Checks if the given token ID is an end token."""
    return token_id in self._end_token_ids
