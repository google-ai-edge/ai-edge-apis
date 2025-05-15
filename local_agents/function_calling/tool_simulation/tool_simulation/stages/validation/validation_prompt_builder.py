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

"""Prompt builder for the replier model."""

import copy
from typing import Iterable, List, Optional, Union
from tool_simulation.core import base_prompt_builder

BaseTurn = base_prompt_builder.BaseTurn
ChunkKind = base_prompt_builder.ChunkKind
BasePromptBuilder = base_prompt_builder.BasePromptBuilder
BaseChunk = base_prompt_builder.BaseChunk


class ValidationChunk(BaseChunk[str]):
  """Represents a basic chunk of text content for validation prompts."""

  def __init__(self, content: str, kind: ChunkKind = ChunkKind.CONTENT):
    super().__init__(content=content, kind=kind)

  def __str__(self) -> str:
    return self.content


class ValidationTurn(BaseTurn[ValidationChunk]):
  """Represents a turn in the validation prompt format."""

  PREAMBLE = "\n"
  POSTAMBLE = "\n"

  def __init__(
      self,
      role: str,
      content: Optional[Union[List[ValidationChunk], str]] = None,
  ):
    super().__init__(role=role, content=content)

  @property
  def content(self) -> List[ValidationChunk]:
    return list(self._content)

  @content.setter
  def content(self, value: Iterable[ValidationChunk]) -> None:
    self._content = list(value)

  def add_chunk(self, chunk: ValidationChunk) -> None:
    self._content.append(chunk)

  @property
  def inner_content(self) -> str:
    return " ".join(str(chunk) for chunk in self._content)

  def __str__(self) -> str:
    return f"{self.role}{self.PREAMBLE}{self.inner_content}{self.POSTAMBLE}"


class ValidationPromptBuilder(
    BasePromptBuilder[ValidationChunk, ValidationTurn, str]
):
  """A prompt builder for the Replier model."""

  _USER_ROLE = "[User]"
  _ASSISTANT_ROLE = "[Assistant]"
  _ENVIRONMENT_ROLE = "[Environment]"
  _SYSTEM_ROLE = "Instruction"

  def __init__(self):
    super().__init__(turn_class=ValidationTurn, chunk_class=ValidationChunk)

  def get_state(self) -> List[ValidationTurn]:
    return copy.deepcopy(self._state)

  def get_state_mutable(self) -> List[ValidationTurn]:
    return self._state

  @property
  def user_role(self) -> str:
    return self._USER_ROLE

  @property
  def model_role(self) -> str:
    return self._ASSISTANT_ROLE

  @property
  def tool_role(self) -> str:
    return self._ENVIRONMENT_ROLE

  def get_chunk(
      self, content: str, kind: ChunkKind = ChunkKind.CONTENT
  ) -> ValidationChunk:
    return ValidationChunk(content, kind=kind)

  def begin_user_turn(self) -> None:
    self.begin_turn(self.user_role)

  def begin_assistant_turn(self) -> None:
    self.begin_turn(self.model_role)

  def begin_tool_turn(self) -> None:
    self.begin_turn(self.tool_role)

  def begin_system_turn(self) -> None:
    self.begin_turn(self._SYSTEM_ROLE)

  def assistant_turn(
      self, text: str, kind: ChunkKind = ChunkKind.CONTENT
  ) -> None:
    self.begin_assistant_turn()
    self.add_content(ValidationChunk(text, kind=kind))
    self.end_turn()

  def user_turn(self, text: str, kind: ChunkKind = ChunkKind.CONTENT) -> None:
    self.begin_user_turn()
    self.add_content(ValidationChunk(text, kind=kind))
    self.end_turn()

  def system_turn(self, text: str, kind: ChunkKind = ChunkKind.CONTENT) -> None:
    self.begin_system_turn()
    self.add_content(ValidationChunk(text, kind=kind))
    self.end_turn()

  def tool_turn(
      self, text: str, kind: ChunkKind = ChunkKind.TOOL_RESULT
  ) -> None:
    self.begin_tool_turn()
    self.add_content(ValidationChunk(text, kind=kind))
    self.end_turn()

  def get_prompt(self, inference: bool = False) -> str:
    if self._current_turn is not None:
      raise ValueError("Cannot get the prompt while in the middle of a turn.")
    return "".join(str(turn) for turn in self._state)
