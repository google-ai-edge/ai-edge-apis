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

"""A processor for *.task files."""

import logging
import os
import zipfile

from litert_tools.pipeline import llm_parameters_pb2
from litert_tools.pipeline import prompt_template


class TaskFileProcessor:
  """A class that processes a *.task file and extracts its components."""

  def __init__(self, file_path: str, cache_dir: str):
    """Initializes the TaskFileProcessor with the path to the .task file.

    Args:
      file_path: The path to the *.task file.
      cache_dir: The directory to extract the task file.
    """
    self.file_path = file_path
    self.cache_dir = cache_dir
    self.extracted = False

  def _unzip_task_files(self):
    """Unzips the task files and extracts them to the cache directory."""
    if self.extracted:
      # Already extracted.
      return

    if not os.path.exists(self.file_path):
      raise ValueError(f"Error: The file '{self.file_path}' does not exist.")

    if not zipfile.is_zipfile(self.file_path):
      raise ValueError(f"Error: '{self.file_path}' is not a valid zip file.")

    logging.info("Extracting task file %s:", self.file_path)
    with zipfile.ZipFile(self.file_path, "r") as zip_ref:
      zip_ref.extractall(self.cache_dir)
    self.extracted = True

  def get_tflite_file_path(self) -> str:
    """Returns the path to the tflite file."""
    self._unzip_task_files()
    return os.path.join(self.cache_dir, "TF_LITE_PREFILL_DECODE")

  def get_tokenizer_file_path(self) -> str:
    """Returns the path to the tokenizer file."""
    self._unzip_task_files()
    return os.path.join(self.cache_dir, "TOKENIZER_MODEL")

  def get_prompt_template(self) -> prompt_template.PromptTemplate:
    """Returns the prompt template."""
    metadata_path = os.path.join(self.cache_dir, "METADATA")
    with open(metadata_path, "rb") as f:
      metadata_bytes = f.read()

    # Parse the metadata file and extract the prompt template.
    llm_parameters = llm_parameters_pb2.LlmParameters()
    llm_parameters.ParseFromString(metadata_bytes)

    if llm_parameters.HasField("prompt_templates"):
      return prompt_template.PromptTemplate(
          start_token=llm_parameters.start_token,
          start_token_id=llm_parameters.start_token_id,
          prompt_prefix=llm_parameters.prompt_templates.user_template.prompt_prefix,
          prompt_suffix=llm_parameters.prompt_templates.user_template.prompt_suffix,
      )
    elif llm_parameters.HasField("prompt_template"):
      return prompt_template.PromptTemplate(
          start_token=llm_parameters.start_token,
          start_token_id=llm_parameters.start_token_id,
          prompt_prefix=llm_parameters.prompt_template.prompt_prefix,
          prompt_suffix=llm_parameters.prompt_template.prompt_suffix,
      )
    else:
      return prompt_template.PromptTemplate(
          start_token=llm_parameters.start_token,
          start_token_id=llm_parameters.start_token_id,
      )
