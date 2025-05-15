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


class LlamaChunk(BaseChunk[str]):
  """A chunk of text in a Llama prompt."""

  preamble: str
  postamble: str

  def __init__(self, content: str, kind: ChunkKind = ChunkKind.CONTENT):
    super().__init__(content=content, kind=kind)

    if kind == ChunkKind.TOOL_CALL:
      self.preamble = "["
      self.postamble = "]"
    else:
      self.preamble = ""
      self.postamble = ""

  def __str__(self) -> str:
    return f"{self.preamble}{self.content}{self.postamble}"


class LlamaTurn(BaseTurn[LlamaChunk]):
  """A turn in a Llama prompt."""

  PREAMBLE = "<|start_header_id|>"
  ROLE_HEADER_END = "<|end_header_id|>"
  POSTAMBLE = "<|eot_id|>"

  def __init__(self, role: str, content: Optional[List[LlamaChunk]] = None):
    super().__init__(role=role, content=content)

  @property
  def content(self) -> List[LlamaChunk]:
    return list(self._content)

  @content.setter
  def content(self, value: Iterable[LlamaChunk]) -> None:
    self._content = list(value)

  def add_chunk(self, chunk: LlamaChunk) -> None:
    if not isinstance(chunk, LlamaChunk):
      raise TypeError(f"Expected a LlamaChunk object, got {type(chunk)}")
    self._content.append(chunk)

  @property
  def inner_content(self) -> str:
    return "\n".join(str(chunk) for chunk in self._content).strip()

  def __str__(self) -> str:
    return f"{self.PREAMBLE}{self.role}{self.ROLE_HEADER_END}{self.inner_content}{self.POSTAMBLE}"


class LlamaPromptBuilder(BasePromptBuilder[LlamaChunk, LlamaTurn, str]):
  """A prompt builder for Llama models."""

  _MODEL_ROLE = "assistant"
  _USER_ROLE = "user"
  _SYSTEM_ROLE = "system"
  _TOOL_ROLE = "tool"

  def __init__(self):
    super().__init__(turn_class=LlamaTurn, chunk_class=LlamaChunk)

  @property
  def user_role(self) -> str:
    return self._USER_ROLE

  @property
  def model_role(self) -> str:
    return self._MODEL_ROLE

  @property
  def tool_role(self) -> str:
    return self._TOOL_ROLE

  def get_state(self) -> List[LlamaTurn]:
    return copy.deepcopy(self._state)

  def get_state_mutable(self) -> List[LlamaTurn]:
    return self._state

  def get_chunk(
      self, content: str, kind: ChunkKind = ChunkKind.CONTENT
  ) -> LlamaChunk:
    return LlamaChunk(content, kind=kind)

  def append_turns(self, turns: List[LlamaTurn]) -> None:
    if self._current_turn is not None:
      raise ValueError(
          "Cannot append turns while in the middle of building a turn."
      )
    self._state.extend(turns)

  def begin_user_turn(self) -> None:
    self.begin_turn(self.user_role)

  def begin_model_turn(self) -> None:
    self.begin_turn(self.model_role)

  def begin_system_turn(self) -> None:
    self.begin_turn(self._SYSTEM_ROLE)

  def begin_tool_turn(self) -> None:
    self.begin_turn(self._TOOL_ROLE)

  def model_turn(self, text: str, kind: ChunkKind = ChunkKind.CONTENT) -> None:
    self.begin_model_turn()
    self.add_content(LlamaChunk(text, kind=kind))
    self.end_turn()

  def user_turn(self, text: str, kind: ChunkKind = ChunkKind.CONTENT) -> None:
    if kind == ChunkKind.TOOL_RESULT:
      self.tool_turn(text)
    else:
      self.begin_user_turn()
      self.add_content(LlamaChunk(text, kind=kind))
      self.end_turn()

  def tool_turn(self, text: str) -> None:
    self.begin_tool_turn()
    self.add_content(LlamaChunk(text, kind=ChunkKind.TOOL_RESULT))
    self.end_turn()

  def system_turn(self, text: str) -> None:
    self.begin_system_turn()
    self.add_content(LlamaChunk(text, kind=ChunkKind.CONTENT))
    self.end_turn()

  def get_prompt(self, inference: bool = False) -> str:
    if self._current_turn is not None:
      raise ValueError("Cannot get the prompt while in the middle of a turn.")
    prompt_body = "".join(str(turn) for turn in self._state)
    if inference:
      return (
          prompt_body
          + self._turn_class.PREAMBLE
          + self.model_role
          + self._turn_class.ROLE_HEADER_END
      )
    else:
      return prompt_body
