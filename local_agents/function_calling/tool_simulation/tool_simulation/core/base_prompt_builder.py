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

"""Base PromptBuilder and Turn classes.

These classes can be used to create custom prompt builders. The `PromptBuilder`
class represents a container of turns. A `Turn` represents a single turn in the
conversation. Different Turn/PromptBuilder classes can be composed together.
"""
import abc
import enum
from typing import Generic, List, Optional, Type, TypeVar
from typing import Iterable


class ChunkKind(enum.Enum):
  CONTENT = "content"
  TOOL_CALL = "tool_call"
  TOOL_RESULT = "tool_result"


ContentType = TypeVar("ContentType")
ChunkType = TypeVar("ChunkType", bound="BaseChunk")
TurnType = TypeVar("TurnType", bound="BaseTurn")


class BaseChunk(Generic[ContentType], abc.ABC):
  """Base class for a chunk of content."""

  content: ContentType
  kind: ChunkKind

  @abc.abstractmethod
  def __init__(
      self, content: ContentType, kind: ChunkKind = ChunkKind.CONTENT, **kwargs
  ):
    self.content = content
    self.kind = kind

  @abc.abstractmethod
  def __str__(self) -> str:
    raise NotImplementedError


class BaseTurn(Generic[ChunkType], abc.ABC):
  """Base class for a turn in a conversation."""

  _role: str
  _content: List[ChunkType]

  @abc.abstractmethod
  def __init__(
      self, role: str, content: Optional[List[ChunkType]] = None, **kwargs
  ):
    self._role = role
    self._content = content if content else []

  @property
  def role(self) -> str:
    return self._role

  @role.setter
  def role(self, value: str) -> None:
    self._role = value

  @property
  @abc.abstractmethod
  def content(self) -> List[ChunkType]:
    raise NotImplementedError

  @content.setter
  @abc.abstractmethod
  def content(self, value: Iterable[ChunkType]) -> None:
    raise NotImplementedError

  @abc.abstractmethod
  def add_chunk(self, chunk: ChunkType) -> None:
    raise NotImplementedError

  @property
  @abc.abstractmethod
  def inner_content(self) -> str:
    raise NotImplementedError

  @abc.abstractmethod
  def __str__(self) -> str:
    raise NotImplementedError


class BasePromptBuilder(Generic[ChunkType, TurnType, ContentType], abc.ABC):
  """Base class for a prompt builder."""

  _state: List[TurnType]
  _current_turn: Optional[TurnType]
  _turn_class: Type[TurnType]
  _chunk_class: Type[ChunkType]

  def __init__(self, turn_class: Type[TurnType], chunk_class: Type[ChunkType]):
    self._turn_class = turn_class
    self._chunk_class = chunk_class
    self._state = []
    self._current_turn = None

  # TODO(b/405415695): Make checks when calling this while a turn hasn't ended.
  @abc.abstractmethod
  def get_state(self) -> List[TurnType]:
    pass

  @abc.abstractmethod
  def get_state_mutable(self) -> List[TurnType]:
    pass

  @property
  @abc.abstractmethod
  def user_role(self) -> str:
    pass

  @property
  @abc.abstractmethod
  def model_role(self) -> str:
    pass

  @property
  @abc.abstractmethod
  def tool_role(self) -> str:
    pass

  @abc.abstractmethod
  def get_prompt(self, inference: bool = False) -> str:
    pass

  @abc.abstractmethod
  def get_chunk(
      self, content: ContentType, kind: ChunkKind = ChunkKind.CONTENT
  ) -> ChunkType:
    pass

  def begin_turn(self, role: str) -> None:
    if self._current_turn is not None:
      raise ValueError("Cannot begin a new turn while in the middle of one.")
    self._current_turn = self._turn_class(role=role)

  def end_turn(self) -> None:
    if self._current_turn is None:
      raise ValueError("Cannot end a turn that has not been started.")
    if not self._current_turn.content:
      raise ValueError("Cannot end a turn that has no content.")
    self._state.append(self._current_turn)
    self._current_turn = None

  def add_content(self, content: ChunkType) -> None:
    """Adds content to the current turn.

    Args:
      content: The content to add. Can be a string or a chunk object.

    Raises:
      ValueError: If no turn has been started.
      TypeError: If content is not a string or a chunk object.
    """
    if not self._current_turn:
      raise ValueError("Cannot add content - no turn has been started.")
    self._current_turn.add_chunk(content)
