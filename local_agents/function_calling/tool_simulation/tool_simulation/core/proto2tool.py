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

"""Functions to convert a types.Tool object to a ToolDefinition."""

from typing import cast
from google.genai import types
from tool_simulation.core import tool_types


def _match_item(
    item: tuple[str, types.Schema],
) -> tool_types.ToolType | None:
  """Matches a parameter property schema to a tool type.

  Args:
    item: tuple of parameter name and schema

  Returns:
    Type of the parameter given in the schema, or None in case the schema has an
    unsupported/unknown type.
  """
  name, schema = item
  _fail_if(
      schema.type == types.Type.TYPE_UNSPECIFIED or not schema.type,
      "Unsupported argument type in function",
  )
  if schema.type == types.Type.STRING:
    return tool_types.String()
  elif schema.type == types.Type.NUMBER:
    return tool_types.Float()
  elif schema.type == types.Type.INTEGER:
    return tool_types.Int()
  elif schema.type == types.Type.BOOLEAN:
    return tool_types.Bool()
  elif schema.type == types.Type.ARRAY:
    _fail_if(
        not schema.items,
        "Unsupported array type without items",
    )
    inner_type = _match_item((name, schema.items))
    # If the inner type is None, fall through
    if inner_type:
      return tool_types.Array(inner_type=inner_type)
  elif schema.type == types.Type.OBJECT:
    _fail_if(
        not schema.properties,
        "Unsupported object type without properties",
    )
    items = cast(dict[str, types.Schema], schema.properties).items()
    fields = {
        item_name: _match_item((item_name, item))
        for item_name, item in sorted(items)
    }
    required_fields = schema.required if schema.required else []
    for field_name in required_fields:
      if field_name not in fields:
        return None
    # If any of the fields is None, the whole object is None.
    if all(fields.values()):
      return tool_types.Object(
          typename=name,
          fields=fields,
          required_fields=set(required_fields),
      )
  return None


def _schema_to_argument(
    item: tuple[str, types.Schema],
) -> tuple[str, tool_types.ArgumentDefinition] | None:
  """Converts types.Schema to an argument name -> ArgumentDefinition mapping.

  Args:
    item: tuple of parameter name and schema

  Returns:
    A dict of argument name to ArgumentDefinition, or None in case the
    schema has an unsupported/unknown type.
  """
  dtype = _match_item(item)
  if dtype:
    name, schema = item
    return (
        name,
        tool_types.ArgumentDefinition(
            name=name,
            description=schema.description,
            dtype=dtype,
        ),
    )
  else:
    return None


def _fail_if(expr: bool, error_message: str):
  if expr:
    raise ValueError(error_message)


def proto2tool(
    tool: types.Tool, tool_name: str | None = None
) -> tool_types.ToolDefinition:
  """Converts a types.Tool object to a ToolDefinition.

  Args:
    tool: The types.Tool proto to convert.
    tool_name: name of the tool (optional, can be used for multi-tool tasks)

  Returns:
    A ToolDefinition object representing the tool defined in the proto.

  Raises:
    ValueError: if the tool duplicate function names.
    ValueError: if a function contains duplicate argument names.
    ValueError: if the tool contains an argument with an unsupported type.
  """
  function_definitions = {}
  if tool.function_declarations:
    for declaration in tool.function_declarations:
      _fail_if(
          not declaration.name,
          "Function name is required in tool",
      )
      declaration_name = declaration.name
      _fail_if(
          declaration_name in function_definitions,
          f"Duplicate function {declaration_name} in tool {tool_name}",
      )
      declaration_description = (
          declaration.description if declaration.description else ""
      )
      args = {}
      if declaration.parameters:
        _fail_if(
            declaration.parameters.type != types.Type.OBJECT
            or not declaration.parameters.type,
            f"Unsupported argument type in function {declaration_name}",
        )
        _fail_if(
            not declaration.parameters.properties,
            f"Missing properties in function {declaration_name}",
        )
        items = cast(
            dict[str, types.Schema], declaration.parameters.properties
        ).items()
        for item in items:
          matched_arg_definition = _schema_to_argument(item)
          if matched_arg_definition:
            arg_name, arg_definition = matched_arg_definition
            args.update({arg_name: arg_definition})
          else:
            raise ValueError(
                f"Unsupported argument type in function {declaration_name}"
            )
        required_args = (
            declaration.parameters.required
            if declaration.parameters.required
            else []
        )
        for arg_name in required_args:
          _fail_if(
              arg_name not in args,
              f"Missing required {arg_name} in function {declaration_name}",
          )
          args[arg_name].required = True
      function_definitions[declaration_name] = tool_types.FunctionDefinition(
          declaration_name, declaration_description, args
      )
  return tool_types.ToolDefinition(
      name=tool_name, functions=function_definitions
  )
