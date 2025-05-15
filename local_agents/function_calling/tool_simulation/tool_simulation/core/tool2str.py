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

"""Converts a Gemini Tool to a string representation."""

import json
import random
from typing import Callable
from typing import Optional
from google.genai import types


FormatterType = Callable[
    [types.Tool, Optional[tuple[str, ...]], Optional[random.Random]], str
]


def _transform_json(
    tool: types.Tool,
    functions_to_use: tuple[str, ...] | None = None,
    rng: random.Random | None = None,
) -> str:
  """Converts a Gemini Tool to a JSON string representation."""
  if isinstance(functions_to_use, tuple) and not functions_to_use:
    raise ValueError("functions_to_use must be a non-empty tuple of strings")
  tool_json = tool.to_json_dict()
  if "function_declarations" not in tool_json:
    raise ValueError("Tool does not have function_declarations")
  tool_obj = tool_json["function_declarations"]

  filtered_tool_obj = tool_obj
  if functions_to_use:
    available_function_names = set(
        [function_declaration["name"] for function_declaration in tool_obj]
    )
    for name in functions_to_use:
      if name not in available_function_names:
        raise ValueError(f"Function {name} not found in tool")
    filtered_tool_obj = list(
        filter(lambda x: x["name"] in functions_to_use, tool_obj)
    )
  if rng:
    rng.shuffle(filtered_tool_obj)
  return json.dumps(filtered_tool_obj, indent=2)


# TODO(b/405415695): Add a base class for the formatters instead of relying on
# a plain callable.
def tool2str(
    tool: types.Tool,
    functions_to_use: Optional[tuple[str, ...]] = None,
    rng: Optional[random.Random] = None,
    overload_formatter: Optional[FormatterType] = None,
    **kwargs,
) -> str:
  """Converts a Gemini Tool to a string representation.

  Args:
    tool: The Gemini Tool to convert.
    functions_to_use: A list of function names from the tool that should be
      used. If None, all functions are used.
    rng: Random number generator to use for shuffling.
    overload_formatter: A custom formatter that overlaods the default JSON
      formatter.
    **kwargs: Additional arguments to pass to the overload_formatter.

  Returns:
    A string representation of the Tool in the form of JSON.

  Raises:
    ValueError: If functions_to_use is an empty list or if a function
    name in functions_to_use is not found in the tool.
  """
  if overload_formatter:
    return overload_formatter(tool, functions_to_use, rng, **kwargs)
  return _transform_json(tool, functions_to_use, rng)
