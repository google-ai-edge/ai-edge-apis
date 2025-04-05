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

"""Model downloader base class and implementations."""

import abc
import logging
import os

import huggingface_hub


class ModelDownloader(abc.ABC):
  """Base class for model downloader."""

  _DEFAULT_CACHE_DIR = os.path.join(
      os.environ["HOME"], ".cache", "litertlm_tools"
  )

  def __init__(
      self,
      cache_dir: str = _DEFAULT_CACHE_DIR,
  ):
    self.cache_dir = cache_dir
    os.makedirs(self.cache_dir, exist_ok=True)

  def download_file(self, repo_id: str, filename: str):
    raise NotImplementedError


class HuggingFaceDownloader(ModelDownloader):
  """HuggingFace model downloader."""

  def __init__(self, cache_dir: str = ModelDownloader._DEFAULT_CACHE_DIR):
    super().__init__(cache_dir)

  def download_file(self, repo_id: str, filename: str) -> str | None:
    local_file_path = os.path.join(self.cache_dir, repo_id, filename)
    if os.path.exists(local_file_path):
      logging.info(
          "File %s/%s is already downloaded to %s",
          repo_id,
          filename,
          local_file_path,
      )
      return local_file_path
    try:
      file_path = huggingface_hub.hf_hub_download(
          repo_id, filename, cache_dir=self.cache_dir, local_dir=self.cache_dir
      )
      logging.info(
          "%s/%s downloaded and saved to %s", repo_id, filename, file_path
      )
      return file_path
    except huggingface_hub.utils.HfHubHTTPError as e:
      logging.exception("Error downloading file from HuggingFace: %s", e)
      raise
    except Exception as e:  # pylint: disable=broad-exception-caught
      logging.exception("An unexpected error occurred: %s", e)
      raise
