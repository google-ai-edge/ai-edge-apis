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

"""Prompt builder for AI Studio."""

import copy
import json
from typing import Any, Iterable, List, Optional

from google.genai import types
from tool_simulation.core import base_prompt_builder

ChunkKind = base_prompt_builder.ChunkKind
BaseChunk = base_prompt_builder.BaseChunk
BaseTurn = base_prompt_builder.BaseTurn
BasePromptBuilder = base_prompt_builder.BasePromptBuilder
InnerType = types.Part


def _fail_if(condition: bool, message: str) -> None:
  if condition:
    raise ValueError(message)


def _str_to_part(content: str, kind: ChunkKind) -> InnerType:
  """Converts a string to a google.genai.types.Part.

  Args:
    content: The string to convert.
    kind: The kind of the chunk.

  Returns:
    A google.genai.types.Part.

  Raises:
    ValueError: If the content is not valid for the given kind.
  """
  if kind == ChunkKind.CONTENT:
    return types.Part(text=content)
  elif kind == ChunkKind.TOOL_CALL:
    data = json.loads(content)
    _fail_if("name" not in data, "Function call must have an name.")
    _fail_if("args" not in data, "Function call must have args.")
    return types.Part(
        function_call=types.FunctionCall(name=data["name"], args=data["args"])
    )
  else:
    data = json.loads(content)
    _fail_if("name" not in data, "Function response must have an name.")
    _fail_if("response" not in data, "Function response must have response.")
    return types.Part(
        function_response=types.FunctionResponse(
            name=data["name"], response=data["response"]
        )
    )


class AIStudioChunk(BaseChunk[InnerType]):
  """Represents a chunk in a conversation for AI Studio."""

  def __init__(self, content: InnerType, kind: ChunkKind = ChunkKind.CONTENT):
    super().__init__(content=content, kind=kind)

  def to_dict(self) -> dict[str, Any]:
    """Converts the chunk to a dict."""
    return self.content.to_json_dict()

  def __str__(self) -> str:
    return json.dumps(self.to_dict())


class AIStudioTurn(BaseTurn[AIStudioChunk]):
  """Represents a turn in a conversation for AI Studio."""

  def __init__(self, role: str, content: Optional[List[AIStudioChunk]] = None):
    super().__init__(role=role, content=content if content else [])

  @property
  def content(self) -> List[AIStudioChunk]:
    return list(self._content)

  @content.setter
  def content(self, value: Iterable[AIStudioChunk]) -> None:
    self._content = list(value)

  def add_chunk(self, chunk: AIStudioChunk) -> None:
    self._content.append(chunk)

  @property
  def inner_content(self) -> str:
    return str(self)

  def __str__(self) -> str:
    return json.dumps(self.to_dict())

  def to_dict(self) -> dict[str, Any]:
    return types.Content(
        role=self.role, parts=[chunk.content for chunk in self._content]
    ).to_json_dict()


class AIStudioPromptBuilder(
    BasePromptBuilder[AIStudioChunk, AIStudioTurn, InnerType]
):
  """Builds prompts for AIStudioModel using google.genai.types."""

  _MODEL_ROLE = "model"
  _USER_ROLE = "user"
  _TOOL_ROLE = "user"

  def __init__(self):
    super().__init__(turn_class=AIStudioTurn, chunk_class=AIStudioChunk)

  @property
  def user_role(self) -> str:
    return self._USER_ROLE

  @property
  def model_role(self) -> str:
    return self._MODEL_ROLE

  @property
  def tool_role(self) -> str:
    return self._TOOL_ROLE

  def get_chunk(
      self, content: str | InnerType, kind: ChunkKind = ChunkKind.CONTENT
  ) -> AIStudioChunk:
    if isinstance(content, str):
      content = _str_to_part(content, kind)
    if kind == ChunkKind.CONTENT and not content.text:
      raise ValueError("Text field must be set.")
    if kind == ChunkKind.TOOL_CALL and not content.function_call:
      raise ValueError("Function call field must be set.")
    if kind == ChunkKind.TOOL_RESULT and not content.function_response:
      raise ValueError("Function response field must be set.")
    return AIStudioChunk(content, kind=kind)

  def get_state(self) -> List[AIStudioTurn]:
    """Returns the conversation history as a list of ContentDicts."""
    if self._current_turn is not None:
      raise ValueError(
          "Cannot get state while in the middle of building a turn."
      )
    return copy.deepcopy(self._state)

  def get_state_mutable(self) -> List[AIStudioTurn]:
    if self._current_turn is not None:
      raise ValueError(
          "Cannot get state while in the middle of building a turn."
      )
    return self._state

  def get_prompt(self, inference: bool = False) -> str:
    if self._current_turn is not None:
      raise ValueError(
          "Cannot get prompt while in the middle of building a turn."
      )
    return json.dumps([turn.to_dict() for turn in self._state])

  def begin_user_turn(self) -> None:
    self.begin_turn(self.user_role)

  def begin_model_turn(self) -> None:
    self.begin_turn(self.model_role)

  def begin_tool_turn(self) -> None:
    self.begin_turn(self.tool_role)

  def model_turn(
      self, content: str | InnerType, kind: ChunkKind = ChunkKind.CONTENT
  ) -> None:
    chunk = self.get_chunk(content, kind)
    self.begin_model_turn()
    self.add_content(chunk)
    self.end_turn()

  def user_turn(
      self, content: str | InnerType, kind: ChunkKind = ChunkKind.CONTENT
  ) -> None:
    chunk = self.get_chunk(content, kind)
    self.begin_user_turn()
    self.add_content(chunk)
    self.end_turn()

  def tool_turn(
      self, content: str | InnerType, kind: ChunkKind = ChunkKind.TOOL_RESULT
  ) -> None:
    chunk = self.get_chunk(content, kind)
    self.begin_tool_turn()
    self.add_content(chunk)
    self.end_turn()
