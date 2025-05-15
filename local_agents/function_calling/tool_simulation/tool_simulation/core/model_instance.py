# Copyright 2025 The Google AI Edge Authors.
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

"""Interface for a model instance."""

import abc
from typing import Protocol
from tool_simulation.core import base_prompt_builder


class ModelInstance(Protocol):

  @abc.abstractmethod
  def query_model(
      self, prompt: str | base_prompt_builder.BasePromptBuilder
  ) -> str | None:
    pass
