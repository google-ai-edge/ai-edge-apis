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

"""Classes that can be used to build prompts or create custom prompt builders."""

import copy
from typing import Iterable
from typing import List, Optional
from tool_simulation.core import base_prompt_builder


BaseTurn = base_prompt_builder.BaseTurn
ChunkKind = base_prompt_builder.ChunkKind
BasePromptBuilder = base_prompt_builder.BasePromptBuilder
BaseChunk = base_prompt_builder.BaseChunk


class GemmaChunk(BaseChunk[str]):
  """A chunk of text in a Gemma prompt."""

  def __init__(self, content: str, kind: ChunkKind = ChunkKind.CONTENT):
    super().__init__(content=content, kind=kind)
    if kind == ChunkKind.TOOL_CALL:
      self.preamble = "```tool_code\n"
      self.postamble = "\n```"
    elif kind == ChunkKind.TOOL_RESULT:
      self.preamble = "```tool_outputs\n"
      self.postamble = "\n```"
    else:
      self.preamble = ""
      self.postamble = ""

  def __str__(self) -> str:
    return f"{self.preamble}{self.content}{self.postamble}"


class GemmaTurn(BaseTurn[GemmaChunk]):
  """A turn in a Gemma prompt, with a role and a list of chunks."""

  PREAMBLE = "<start_of_turn>"
  POSTAMBLE = "<end_of_turn>"

  def __init__(self, role: str, content: Optional[List[GemmaChunk]] = None):
    super().__init__(role=role, content=content)

  @property
  def content(self) -> List[GemmaChunk]:
    return list(self._content)

  @content.setter
  def content(self, value: Iterable[GemmaChunk]) -> None:
    self._content = list(value)

  def add_chunk(self, chunk: GemmaChunk) -> None:
    self._content.append(chunk)

  @property
  def inner_content(self) -> str:
    return "\n".join(str(chunk) for chunk in self._content)

  def __str__(self) -> str:
    return f"{GemmaTurn.PREAMBLE}{self.role}\n{self.inner_content}{GemmaTurn.POSTAMBLE}"


class GemmaPromptBuilder(BasePromptBuilder[GemmaChunk, GemmaTurn, str]):
  """A prompt builder for Gemma prompts."""

  _MODEL_ROLE = "model"
  _USER_ROLE = "user"

  def __init__(self):
    super().__init__(turn_class=GemmaTurn, chunk_class=GemmaChunk)

  @property
  def user_role(self) -> str:
    return self._USER_ROLE

  @property
  def model_role(self) -> str:
    return self._MODEL_ROLE

  @property
  def tool_role(self) -> str:
    return self.user_role

  def get_state(self) -> List[GemmaTurn]:
    return copy.deepcopy(self._state)

  def get_state_mutable(self) -> List[GemmaTurn]:
    return self._state

  def get_chunk(
      self, content: str, kind: ChunkKind = ChunkKind.CONTENT
  ) -> GemmaChunk:
    return GemmaChunk(content, kind=kind)

  def append_turns(self, turns: List[GemmaTurn]) -> None:
    if self._current_turn is not None:
      raise ValueError(
          "Cannot append turns while in the middle of building a turn."
      )
    self._state.extend(turns)

  def begin_user_turn(self) -> None:
    self.begin_turn(self.user_role)

  def begin_model_turn(self) -> None:
    self.begin_turn(self.model_role)

  def model_turn(self, text: str, kind: ChunkKind = ChunkKind.CONTENT) -> None:
    self.begin_model_turn()
    self.add_content(GemmaChunk(text, kind=kind))
    self.end_turn()

  def user_turn(self, text: str, kind: ChunkKind = ChunkKind.CONTENT) -> None:
    self.begin_user_turn()
    self.add_content(GemmaChunk(text, kind=kind))
    self.end_turn()

  def get_prompt(self, inference: bool = False) -> str:
    if self._current_turn is not None:
      raise ValueError("Cannot get the prompt while in the middle of a turn.")
    prompt_body = "".join(str(turn) for turn in self._state)
    if inference:
      return prompt_body + self._turn_class.PREAMBLE + self.model_role + "\n"
    else:
      return prompt_body
