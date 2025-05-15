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

"""Basic prompt template for single-turn interactions."""

import dataclasses


@dataclasses.dataclass(frozen=True)
class PromptTemplate:
  """A class that contains a simple prompt template."""

  # We do not currently use the stop tokens from the model metadata, so
  # we only extract start tokens and prompt prefix/suffix for now.

  start_token: str | None = None
  start_token_id: int | None = None
  prompt_prefix: str = ""
  prompt_suffix: str = ""
