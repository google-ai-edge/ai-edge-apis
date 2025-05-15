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


class ReplierChunk(BaseChunk[str]):

  def __init__(self, content: str, kind: ChunkKind = ChunkKind.CONTENT):
    super().__init__(content=content, kind=kind)

  def __str__(self) -> str:
    return self.content


class ReplierTurn(BaseTurn[ReplierChunk]):
  """Represents a turn in the conversation with the replier model."""

  def __init__(
      self, role: str, content: Optional[Union[List[ReplierChunk], str]] = None
  ):
    super().__init__(role=role, content=content)

  @property
  def content(self) -> List[ReplierChunk]:
    return list(self._content)

  @content.setter
  def content(self, value: Iterable[ReplierChunk]) -> None:
    self._content = list(value)

  def add_chunk(self, chunk: ReplierChunk) -> None:
    self._content.append(chunk)

  @property
  def inner_content(self) -> str:
    return "".join(str(chunk) for chunk in self._content)

  def __str__(self) -> str:
    return f"{self.role}: {self.inner_content}\n"


class ReplierPromptBuilder(BasePromptBuilder[ReplierChunk, ReplierTurn, str]):
  """Prompt builder for the replier model."""

  _ASSISTANT_ROLE = "Assistant"
  _USER_ROLE = "User"
  _SYSTEM_ROLE = "Instruction"

  def __init__(self):
    super().__init__(turn_class=ReplierTurn, chunk_class=ReplierChunk)

  def get_state(self) -> List[ReplierTurn]:
    return copy.deepcopy(self._state)

  def get_state_mutable(self) -> List[ReplierTurn]:
    return self._state

  @property
  def user_role(self) -> str:
    return self._USER_ROLE

  @property
  def model_role(self) -> str:
    return self._ASSISTANT_ROLE

  @property
  def tool_role(self) -> str:
    raise NotImplementedError("Tool role is not supported by the replier.")

  def get_chunk(
      self, content: str, kind: ChunkKind = ChunkKind.CONTENT
  ) -> ReplierChunk:
    return ReplierChunk(content, kind=kind)

  def _sanitize(self, input_string: str):
    return (
        input_string.replace(self.user_role, "")
        .replace(self.model_role, "")
        .replace(self._SYSTEM_ROLE, "")
        .strip()
    )

  def begin_user_turn(self) -> None:
    self.begin_turn(self.user_role)

  def begin_model_turn(self) -> None:
    self.begin_turn(self.model_role)

  def begin_system_turn(self) -> None:
    self.begin_turn(self._SYSTEM_ROLE)

  def model_turn(self, text: str) -> None:
    self.begin_model_turn()
    self.add_content(ReplierChunk(text, kind=ChunkKind.CONTENT))
    self.end_turn()

  def user_turn(self, text: str) -> None:
    self.begin_user_turn()
    self.add_content(ReplierChunk(text, kind=ChunkKind.CONTENT))
    self.end_turn()

  def system_turn(self, text: str) -> None:
    self.begin_system_turn()
    self.add_content(ReplierChunk(text, kind=ChunkKind.CONTENT))
    self.end_turn()

  def get_prompt(self, inference: bool = False) -> str:
    if self._current_turn is not None:
      raise ValueError("Cannot get the prompt while in the middle of a turn.")
    return "".join(str(turn) for turn in self._state)
