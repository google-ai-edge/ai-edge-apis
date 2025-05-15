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

"""Testing utilities for prompt builders."""

import copy
from typing import Iterable
from typing import List
from tool_simulation.core import base_prompt_builder


BaseChunk = base_prompt_builder.BaseChunk
BaseTurn = base_prompt_builder.BaseTurn
ChunkKind = base_prompt_builder.ChunkKind
BasePromptBuilder = base_prompt_builder.BasePromptBuilder


# pylint: disable=useless-parent-delegation
class TestChunk(BaseChunk[str]):
  """A test implementation of BaseChunk."""

  __test__ = False
  prefix = "<chunk_start>"
  suffix = "<chunk_end>"

  def __init__(self, content: str, kind: ChunkKind = ChunkKind.CONTENT):
    super().__init__(content, kind)

  def __str__(self) -> str:
    if self.kind == ChunkKind.TOOL_CALL:
      kind = "tool_call"
    elif self.kind == ChunkKind.TOOL_RESULT:
      kind = "tool_result"
    elif self.kind == ChunkKind.CONTENT:
      kind = "content"
    else:
      raise ValueError(f"Unknown chunk kind: {self.kind}")
    return f"{TestChunk.prefix}[{kind}]{self.content}{TestChunk.suffix}"


class TestTurn(BaseTurn[TestChunk]):
  """A test implementation of BaseTurn."""

  __test__ = False
  prefix = "<turn_start>"
  suffix = "<turn_end>"

  def __init__(self, role: str, content: Iterable[TestChunk] | None = None):
    super().__init__(role, content)

  @property
  def content(self) -> List[TestChunk]:
    return self._content

  @content.setter
  def content(self, value: Iterable[TestChunk]) -> None:
    self._content = [chunk for chunk in value]

  def add_chunk(self, chunk: TestChunk) -> None:
    self._content.append(chunk)

  @property
  def inner_content(self) -> str:
    return "\n".join([str(c) for c in self._content])

  def __str__(self) -> str:
    return (
        f"{TestTurn.prefix}{self.role}\n{self.inner_content}{TestTurn.suffix}"
    )


class TestPromptBuilder(BasePromptBuilder[TestChunk, TestTurn, str]):
  """A test implementation of BasePromptBuilder."""

  __test__ = False
  _user_role: str = "user"
  _model_role: str = "model"
  _tool_role: str = "tool"

  def __init__(self, **kwargs):
    super().__init__(TestTurn, TestChunk, **kwargs)

  @property
  def user_role(self) -> str:
    return self._user_role

  @property
  def model_role(self) -> str:
    return self._model_role

  @property
  def tool_role(self) -> str:
    return self._tool_role

  def get_state(self) -> List[TestTurn]:
    return copy.deepcopy(self._state)

  def get_state_mutable(self) -> List[TestTurn]:
    return self._state

  def get_chunk(
      self, content: str, kind: ChunkKind = ChunkKind.CONTENT
  ) -> TestChunk:
    return TestChunk(content, kind)

  def get_prompt(self, inference: bool = False) -> str:
    if self._current_turn is not None:
      raise ValueError("Cannot get the prompt while in the middle of a turn.")
    prompt_body = "".join(str(turn) for turn in self._state)
    if inference:
      return prompt_body + self._turn_class.prefix + self.model_role + "\n"
    return prompt_body


# pylint: enable=useless-parent-delegation
