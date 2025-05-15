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

"""Util to validate a function call against a schema."""

from typing import cast
from absl import logging
from google.genai import types
from tool_simulation.core import proto2tool
from tool_simulation.core import str2call
from tool_simulation.core import tool_types


_ContainerTypes = tool_types.Array | tool_types.Object


def _validate_types(
    schema_type: tool_types.ToolType, call_type: tool_types.ToolType
) -> bool:
  """Validates if two types are compatible.

  Args:
    schema_type: The schema type.
    call_type: The call type.

  Returns:
    True if the types are compatible, False otherwise.
  """
  if not isinstance(schema_type, type(call_type)):
    return False
  if isinstance(schema_type, tool_types.Array):
    call_type = cast(tool_types.Array, call_type)
    if isinstance(schema_type.inner_type, _ContainerTypes) and isinstance(
        call_type.inner_type, _ContainerTypes
    ):
      return _validate_types(schema_type.inner_type, call_type.inner_type)
    else:
      return schema_type == call_type
  elif isinstance(schema_type, tool_types.Object):
    call_type = cast(tool_types.Object, call_type)
    if schema_type.typename != call_type.typename:
      return False
    # Check all required fields are present
    for arg_name in schema_type.required_fields:
      if arg_name not in call_type.fields:
        return False
    # Check no bogus fields
    for arg_name in call_type.fields:
      if arg_name not in schema_type.fields:
        return False

    # Check all fields have correct types
    for arg_name in call_type.fields:
      # A non-required field set to None is valid.
      if (
          arg_name not in schema_type.required_fields
          and call_type.fields[arg_name] == tool_types.NoneType()
      ):
        continue
      if not _validate_types(
          schema_type.fields[arg_name], call_type.fields[arg_name]
      ):
        return False
    return True
  else:
    return schema_type == call_type


def validate_function_call(
    function_call: str2call.FunctionCall,
    tool: types.Tool,
    skip_on_raw_string: bool = True,
) -> bool:
  """Validates a function call against a schema.

  Args:
    function_call: The function call to validate.
    tool: The tool that the function call belongs to.
    skip_on_raw_string: If True, skip validation if the function call has a
      raw_string. Otherwise, always validate.

  Returns:
    True if the function call is valid, False otherwise.
  """
  if function_call.raw_string is not None and skip_on_raw_string:
    # TODO(b/412697872): Setting raw_string is usually done to bypass the AST
    # parsing/validation. Usually this happens when (1) the user is using a
    # different format (e.g json) or (2) the user interfaces with an external
    # API (which ususally do validation). We assume case (2) so the below will
    # skip validation if raw_string is set. To allow for an escape hatch in case
    # (1), `skip_on_raw_string` can be set to False which will re-enable
    # validation.
    # In future releases we should provide a broader support for more formats,
    # and make the validator handle them by default.
    logging.warning(
        "Validating function call with raw string: %s", function_call.raw_string
    )
    return True
  try:
    tool_definition = proto2tool.proto2tool(tool)
  except ValueError as e:
    raise ValueError(f"Failed to convert tool to tool definition: {e}") from e
  function_definition = tool_definition.functions.get(function_call.name, None)
  if not function_definition:
    return False
  # Check if all required arguments are present in the function call
  for (
      schema_arg_name,
      schema_arg_definition,
  ) in function_definition.args.items():
    if (
        schema_arg_definition.required
        and schema_arg_name not in function_call.args
    ):
      return False
  # Check if function call has bogus arguments
  for function_arg_name in function_call.args:
    if function_arg_name not in function_definition.args:
      return False
  # Check if function call has correct argument types
  for function_arg_name, function_arg in function_call.args.items():
    schema_arg_definition = function_definition.args[function_arg_name]
    # A non-required argument set to None is valid.
    if (
        not schema_arg_definition.required
        and function_arg.dtype == tool_types.NoneType()
    ):
      continue
    if not _validate_types(schema_arg_definition.dtype, function_arg.dtype):
      return False
  return True
