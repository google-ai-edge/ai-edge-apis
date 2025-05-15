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

"""Abstractions for working with tool structures.

This contains data types and classes that are used to represent
tools/function/arguments.
"""

import dataclasses
from typing import Protocol


class ToolType(Protocol):
  """A protocol class for tool types.

  This is used to represent different datatypes in a tool.

  Attributes:
    typename: The typename.
  """

  typename: str


@dataclasses.dataclass(frozen=True)
class String(ToolType):
  typename: str = "str"


@dataclasses.dataclass(frozen=True)
class Float(ToolType):
  typename: str = "float"


@dataclasses.dataclass(frozen=True)
class Bool(ToolType):
  typename: str = "bool"


@dataclasses.dataclass(frozen=True)
class Int(ToolType):
  typename: str = "int"


@dataclasses.dataclass(frozen=True)
class NoneType(ToolType):
  typename: str = "None"


# This is used to represent an undefined type. It is different from None which
# represents a None value.
@dataclasses.dataclass(frozen=True)
class _UndefinedType(ToolType):
  typename: str = "undefined"


@dataclasses.dataclass
class Array(ToolType):
  """An list type.

  Attributes:
    typename: The typename.
    inner_type: The type of the elements in the list.
  """

  typename: str = "list"
  inner_type: ToolType = dataclasses.field(default_factory=_UndefinedType)

  def __eq__(self, other: ToolType) -> bool:
    if not isinstance(other, Array):
      return False
    # If inner_type is undefined, we have an empty list. When checking
    # it against another list, we want to return True since an empty list is a
    # legal value
    if isinstance(self.inner_type, _UndefinedType) or isinstance(
        other.inner_type, _UndefinedType
    ):
      return True
    return self.inner_type == other.inner_type


@dataclasses.dataclass
class Dict(ToolType):
  """A dictionary type.

  Used as default type for return values.
  """

  typename: str = "dict"
  inner_key_type: ToolType = dataclasses.field(default_factory=String)
  inner_value_type: ToolType = dataclasses.field(default_factory=NoneType)


@dataclasses.dataclass
class Object(ToolType):
  typename: str
  fields: dict[str, ToolType] = dataclasses.field(default_factory=dict)
  required_fields: set[str] = dataclasses.field(default_factory=set)


@dataclasses.dataclass
class ReturnedValueDefinition:
  """Definition of the return value of a function.

  Attributes:
    description: A description of what is returned.
    dtype: The type of the returned value.
  """

  description: str
  dtype: ToolType

  def __init__(self, dtype: ToolType = Dict(), description: str = ""):
    self.dtype = dtype
    self.description = description


@dataclasses.dataclass
class ArgumentDefinition:
  """An argument definition. This is a structured representation of an argument.

  Attributes:
    name: The name of the argument.
    description: A description of the argument.
    dtype: The type of the argument.
    required: Whether the argument is required.
  """

  name: str
  description: str
  dtype: ToolType
  required: bool = False


@dataclasses.dataclass
class FunctionDefinition:
  """A function definition. This is a structured representation of a function.

  Attributes:
    name: The name of the function.
    description: A description of the function.
    args: A dictionary of argument definitions (i.e argument name to argument
      definition mapping).
  """

  name: str
  description: str
  args: dict[str, ArgumentDefinition]


@dataclasses.dataclass
class ToolDefinition:
  """A tool definition. This is a structured representation of a tool.

  Attributes:
    name: The name of the tool.
    functions: A dictionary of function definitions (i.e function name to
      function definition mapping).
  """

  name: str | None
  functions: dict[str, FunctionDefinition]
