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

"""Module to parse function call expressions into FunctionCall objects."""

import _ast
import ast
import collections
import dataclasses
from typing import Any, Dict, cast

from tool_simulation.core import tool_types


# pylint: disable=invalid-name
_SupportedTypes = ast.Constant | ast.List | ast.Call | ast.Dict


class _TypeCheckVisitor(ast.NodeVisitor):
  """Visitor class to enforce a list of supported types on the AST."""

  def visit_Name(self, node: ast.Name):
    pass

  def visit_Load(self, node: ast.Load):
    pass

  def visit_keyword(self, node: _ast.keyword):
    if not isinstance(node.arg, str):
      raise ValueError(f"Unsupported type for keyword: {type(node.arg)}")
    super().generic_visit(node)

  def generic_visit(self, node: ast.AST):
    if not isinstance(node, _SupportedTypes):
      raise ValueError(f"Unsupported type. {type(node)}")
    super().generic_visit(node)


class _UnaryOpEvaluator(ast.NodeTransformer):
  """Transformer class to convert UnaryOp nodes to Constant nodes."""

  def visit_UnaryOp(self, node: ast.UnaryOp) -> ast.Constant:
    """Replaces a unary operation with a Constant node."""
    if isinstance(node.operand, ast.Constant):
      try:
        return ast.Constant(value=ast.literal_eval(node))
      except Exception as e:
        raise ValueError(f"Failed to evaluate unary operation: {e}") from e
    else:
      raise ValueError("Unsupported type for unary operator.")


Container = collections.namedtuple("Container", ["typename", "fields"])


class _ObjectVisitor(ast.NodeVisitor):
  """Visitor class to extract values from an AST."""

  def __init__(self):
    self._objects: Dict[int, Container] = {}

  def visit_Call(self, node: ast.Call) -> Container:
    """Visits a Call node and extracts the function name and arguments."""
    if id(node) in self._objects:
      return self._objects[id(node)]
    if not isinstance(node.func, ast.Name):
      raise ValueError("Unsupported type for function name.")
    typename = node.func.id
    fields = {}
    for keyword in node.keywords:
      fields[keyword.arg] = self._extract_value(keyword.value)

    if typename == "list" or typename == "dict":
      raise ValueError(f"Unsupported type for object: {typename}")
    self._objects[id(node)] = Container(typename, fields)
    return self._objects[id(node)]

  def visit_List(self, node: ast.List) -> Container:
    """Visits a List node and extracts the elements."""
    if id(node) in self._objects:
      return self._objects[id(node)]
    fields = []
    for elt in node.elts:
      fields.append(self._extract_value(elt))
    self._objects[id(node)] = Container("list", fields)
    return self._objects[id(node)]

  def visit_Dict(self, node: ast.Dict) -> Container:
    """Visits a Dict node and extracts the keys and values."""
    if id(node) in self._objects:
      return self._objects[id(node)]
    fields = {}
    for key, value in zip(node.keys, node.values):
      if isinstance(key, ast.Constant):
        key = key.value
      else:
        raise ValueError("Unsupported type for dict key.")
      fields[key] = self._extract_value(value)
    self._objects[id(node)] = Container("dict", fields)
    return self._objects[id(node)]

  def visit_Constant(self, node: ast.Constant) -> Container:
    """Visits a Constant node and extracts the value."""
    if id(node) in self._objects:
      return self._objects[id(node)]
    self._objects[id(node)] = Container("constant", node.value)
    return self._objects[id(node)]

  def _extract_value(self, node: ast.AST) -> Any:
    if isinstance(node, ast.Constant):
      return Container("constant", node.value)
    elif isinstance(node, (ast.Call, ast.List, ast.Dict)):
      return self.visit(node)
    else:
      raise ValueError(
          f"Unsupported node type: {type(node)}, ast dump: {ast.dump(node)}"
      )

  def get_objects(self) -> Dict[int, Container]:
    return self._objects


# pylint: enable=invalid-name


@dataclasses.dataclass
class FunctionArgument:
  value: Container
  dtype: tool_types.ToolType


@dataclasses.dataclass
class FunctionCall:
  """Represents a function call expression.

  Attributes:
    name: The name of the function being called.
    args: A dictionary of keyword arguments passed to the function.
    ast: The AST representation of the function call expression.
    raw_string: The raw string representation of the function call expression.
      To override the default string representation (which is derived from the
      AST), set this attribute to a non-None value. This lets you emit a string
      representation that is different from the original string (if for example
      you are using a different format or an API that already does
      verification).
  """

  name: str
  args: dict[str, FunctionArgument]
  # This is ast.AST but pytype throws an error.
  ast: Any | None = None
  raw_string: str | None = None

  def __eq__(self, other: "FunctionCall") -> bool:
    return self.name == other.name and self.args == other.args

  def __str__(self):
    if self.raw_string is not None:
      return self.raw_string
    if self.ast is None:
      raise ValueError("AST is not initialized.")
    return ast.unparse(self.ast)


def _determine_type(
    node: _SupportedTypes,
) -> tool_types.ToolType | None:
  """Detect the type of a node in an AST.

  Args:
    node: an ast node (either Const/List) to determine the type of.

  Returns:
    ToolType instance with the type of the node, or None if the type
    is not supported.

  Raises:
    ValueError: if the node is not a supported type. For a composite type (e.g.
     list, object), the inner type should be one of the supported types.
  """
  if isinstance(node, ast.Constant):
    if isinstance(node.value, bool):
      return tool_types.Bool()
    elif isinstance(node.value, float):
      return tool_types.Float()
    elif isinstance(node.value, str):
      return tool_types.String()
    elif isinstance(node.value, int):
      return tool_types.Int()
    elif not node.value:
      return tool_types.NoneType()
  elif isinstance(node, ast.List):
    # If the list has elements, use first element to determine type.
    if node.elts:
      # TODO(b/351703073): Check for lists containing multiple types.
      if isinstance(node.elts[0], (_SupportedTypes)):
        return tool_types.Array(inner_type=_determine_type(node.elts[0]))
      else:
        raise ValueError("Unsupported type for list.")
    return tool_types.Array()
  elif isinstance(node, ast.Call):
    node.func = cast(ast.Name, node.func)
    return tool_types.Object(
        typename=node.func.id,
        fields={
            arg.arg: _determine_type(cast(_SupportedTypes, arg.value))
            for arg in node.keywords
        },
    )
  elif isinstance(node, ast.Dict):
    inner_key_type = _determine_type(cast(_SupportedTypes, node.keys[0]))
    if not isinstance(inner_key_type, (tool_types.String, tool_types.Int)):
      raise ValueError("Unsupported type for dictionary key.")
    inner_value_type = _determine_type(cast(_SupportedTypes, node.values[0]))
    return tool_types.Dict(
        inner_key_type=inner_key_type, inner_value_type=inner_value_type
    )
  else:
    raise ValueError("Unsupported type.")


def parse_function_call_expression(expression: str) -> FunctionCall:
  """Parses a function call expression into a FunctionCall object.

  The function call expression should be of the form:
  <function_name>(<keyword_args>).

  Args:
    expression: expression to parse.

  Returns:
    A FunctionCall object representing the parsed expression.

  Raises:
    ValueError: if the expression is not a valid function call expression.
    ValueError: if the expression contains positional arguments.
    ValueError: if the expression contains unsupported argument types.
    ValueError: if the expression contains repeated arguments.
  """
  try:
    tree = ast.parse(expression)
  except Exception as e:
    # This is raised when an invalid expression syntax is passed.
    raise ValueError(f"Malformed expression: {e}") from e

  # Evaluate unary operations before parsing
  unary_op_transformer = _UnaryOpEvaluator()
  tree = unary_op_transformer.visit(tree)

  # Ensure expression is of the form <function_name>(<keyword_args>)
  if not (
      len(tree.body) == 1
      and isinstance(tree.body[0], ast.Expr)
      and isinstance(tree.body[0].value, ast.Call)
  ):
    raise ValueError(f"Unsupported expression {expression}.")
  call_node = tree.body[0].value
  try:
    _TypeCheckVisitor().visit(call_node)
  except ValueError as e:
    raise ValueError(f"Unsupported AST type: {e}") from e

  if call_node.args:
    raise ValueError("Positional arguments are not supported.")

  # Parse the keyword of the expression.
  args: dict[str, FunctionArgument] = {}
  object_visitor = _ObjectVisitor()
  for keyword in call_node.keywords:
    # Allowed types as per the function calling schema are literals, lists, and
    # objects.
    if not isinstance(keyword.value, _SupportedTypes):
      raise ValueError(f"Unsupported argument type: {type(keyword.value)}")
    arg_name = keyword.arg
    object_visitor.visit(keyword.value)
    objects = object_visitor.get_objects()
    if id(keyword.value) in objects:
      value = objects[id(keyword.value)]
    else:
      raise ValueError(f"Unsupported type for keyword {arg_name}.")
    dtype = _determine_type(keyword.value)
    if dtype is None:
      raise ValueError(f"Unsupported type for keyword {arg_name}.")
    if arg_name in args:
      raise ValueError(f"Repeated argument {arg_name}.")
    args[arg_name] = FunctionArgument(value, dtype)

  return FunctionCall(name=call_node.func.id, args=args, ast=tree)
