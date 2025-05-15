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

import random

from absl.testing import absltest
from absl.testing import parameterized
from google.genai import types
from tool_simulation.core import tool2str


_function_registry = {
    "foo_x_required_x": types.FunctionDeclaration(
        name="foo",
        description="foo_descr",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "x": types.Schema(
                    type=types.Type.STRING,
                    description="arg x",
                ),
            },
            required=["x"],
        ),
    ),
    "bar_y_required_y": types.FunctionDeclaration(
        name="bar",
        description="bar_descr",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "y": types.Schema(
                    type=types.Type.INTEGER,
                    description="arg y",
                ),
            },
            required=["y"],
        ),
    ),
    "foo_multiplearg": types.FunctionDeclaration(
        name="foo",
        description="foo_descr",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "x": types.Schema(
                    type=types.Type.STRING,
                    description="arg x of type string",
                ),
                "y": types.Schema(
                    type=types.Type.INTEGER,
                    description="arg y of type int",
                ),
                "z": types.Schema(
                    type=types.Type.NUMBER,
                    description="arg z of type float",
                ),
                "a": types.Schema(
                    type=types.Type.BOOLEAN,
                    description="arg a of type bool",
                ),
            },
            required=["x", "y", "z", "a"],
        ),
    ),
    "foo_multiplearg_optional": types.FunctionDeclaration(
        name="foo",
        description="foo_descr",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "x": types.Schema(
                    type=types.Type.STRING,
                    description="arg x of type string",
                ),
                "y": types.Schema(
                    type=types.Type.INTEGER,
                    description="arg y of type int",
                ),
                "z": types.Schema(
                    type=types.Type.NUMBER,
                    description="arg z of type float",
                ),
                "a": types.Schema(
                    type=types.Type.BOOLEAN,
                    description="arg a of type bool",
                ),
            },
            required=["x", "y"],
        ),
    ),
    "foo_optional_args": types.FunctionDeclaration(
        name="foo",
        description="foo_descr",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "x": types.Schema(
                    type=types.Type.STRING,
                    description="arg x of type string",
                ),
                "y": types.Schema(
                    type=types.Type.INTEGER,
                    description="arg y of type int",
                ),
            },
            required=["x"],
        ),
    ),
    "foo_array_args": types.FunctionDeclaration(
        name="foo",
        description="foo_descr",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "x": types.Schema(
                    type=types.Type.ARRAY,
                    items=types.Schema(type=types.Type.STRING),
                    description="arg x of type list[str]",
                ),
            },
            required=["x"],
        ),
    ),
    "foo_object_args": types.FunctionDeclaration(
        name="foo",
        description="foo_descr",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "x": types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "a": types.Schema(type=types.Type.STRING),
                        "b": types.Schema(type=types.Type.INTEGER),
                    },
                    required=["a"],
                    description="arg x of type object",
                ),
            },
            required=["x"],
        ),
    ),
}


def _make_tool(args: list[str]) -> types.Tool:
  return types.Tool(
      function_declarations=[_function_registry[func] for func in args],
  )


class Tool2StrTest(parameterized.TestCase):

  @parameterized.named_parameters(
      (
          "single_function",
          _make_tool(["foo_x_required_x"]),
          """\
[
  {
    "name": "foo",
    "description": "foo_descr",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "x": {
          "type": "STRING",
          "description": "arg x"
        }
      },
      "required": [
        "x"
      ]
    }
  }
]""",
      ),
      (
          "multiple_functions",
          _make_tool(["foo_x_required_x", "bar_y_required_y"]),
          """\
[
  {
    "name": "foo",
    "description": "foo_descr",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "x": {
          "type": "STRING",
          "description": "arg x"
        }
      },
      "required": [
        "x"
      ]
    }
  },
  {
    "name": "bar",
    "description": "bar_descr",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "y": {
          "type": "INTEGER",
          "description": "arg y"
        }
      },
      "required": [
        "y"
      ]
    }
  }
]""",
      ),
      (
          "optional_arguments",
          _make_tool(["foo_optional_args"]),
          """\
[
  {
    "name": "foo",
    "description": "foo_descr",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "y": {
          "type": "INTEGER",
          "description": "arg y of type int"
        },
        "x": {
          "type": "STRING",
          "description": "arg x of type string"
        }
      },
      "required": [
        "x"
      ]
    }
  }
]""",
      ),
      (
          "array_arguments",
          _make_tool(["foo_array_args"]),
          """\
[
  {
    "name": "foo",
    "description": "foo_descr",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "x": {
          "type": "ARRAY",
          "description": "arg x of type list[str]",
          "items": {
            "type": "STRING"
          }
        }
      },
      "required": [
        "x"
      ]
    }
  }
]""",
      ),
      (
          "object_arguments",
          _make_tool(["foo_object_args"]),
          """\
[
  {
    "name": "foo",
    "description": "foo_descr",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "x": {
          "type": "OBJECT",
          "description": "arg x of type object",
          "properties": {
            "a": {
              "type": "STRING"
            },
            "b": {
              "type": "INTEGER"
            }
          },
          "required": [
            "a"
          ]
        }
      },
      "required": [
        "x"
      ]
    }
  }
]""",
      ),
  )
  def test_tool2str_e2e_json(self, tool: types.Tool, expected: str):
    self.assertJsonEqual(tool2str.tool2str(tool), expected)

  def test_tool2str_funcs_to_use_json(self):
    self.assertJsonEqual(
        tool2str.tool2str(
            tool=_make_tool(["foo_x_required_x", "bar_y_required_y"]),
            functions_to_use=("foo",),
        ),
        """\
[
  {
    "name": "foo",
    "description": "foo_descr",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "x": {
          "type": "STRING",
          "description": "arg x"
        }
      },
      "required": [
        "x"
      ]
    }
  }
]""",
    )

  @parameterized.named_parameters(
      ("throws_on_empty_funcs", tuple()),
      ("throws_on_missing_func", ("missing_func",)),
      ("throws_on_empty_funcs_json", tuple()),
      ("throws_on_missing_func_json", ("missing_func",)),
  )
  def test_tool2str_throws(
      self,
      functions_to_use: tuple[str, ...] | None,
  ):
    with self.assertRaises(ValueError):
      _ = (
          tool2str.tool2str(
              tool=types.Tool(
                  function_declarations=[
                      types.FunctionDeclaration(
                          name="foo",
                          description="foo_descr",
                          parameters=types.Schema(
                              type=types.Type.OBJECT,
                              properties={
                                  "x": types.Schema(
                                      type=types.Type.STRING,
                                      description="arg x",
                                  ),
                              },
                              required=["x"],
                          ),
                      )
                  ]
              ),
              functions_to_use=functions_to_use,
          ),
      )

  def test_tool2str_shuffle_json(self):
    self.assertJsonEqual(
        tool2str.tool2str(
            types.Tool(
                function_declarations=[
                    types.FunctionDeclaration(
                        name="foo", description="foo_descr"
                    ),
                    types.FunctionDeclaration(
                        name="bar", description="bar_descr"
                    ),
                ]
            ),
            rng=random.Random(123),
        ),
        """\
[
  {
    "name": "bar",
    "description": "bar_descr"
  },
  {
    "name": "foo",
    "description": "foo_descr"
  }
]""",
    )


if __name__ == "__main__":
  googletest.main()
