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

from absl.testing import absltest
from absl.testing import parameterized
from google.genai import types
from tool_simulation.core import str2call
from tool_simulation.core import tool_types
from tool_simulation.stages.validation import validate_function_call


def _get_function_declaration(
    function_declaration: types.FunctionDeclaration,
) -> types.Tool:
  return types.Tool(function_declarations=[function_declaration])


def _get_function_call(
    name: str, args: dict[str, str2call.FunctionArgument]
) -> str2call.FunctionCall:
  return str2call.FunctionCall(name=name, args=args)


class ValidateFunctionCallTest(parameterized.TestCase):

  @parameterized.named_parameters(
      (
          "matching_function_call",
          _get_function_call(name="f", args={}),
          _get_function_declaration(
              types.FunctionDeclaration(
                  name="f",
              )
          ),
      ),
      (
          "matching_function_call_with_args",
          _get_function_call(
              name="f",
              args={
                  "arg1": str2call.FunctionArgument(
                      value=str2call.Container(typename="constant", fields=1),
                      dtype=tool_types.Int(),
                  )
              },
          ),
          _get_function_declaration(
              types.FunctionDeclaration(
                  name="f",
                  parameters=types.Schema(
                      type=types.Type.OBJECT,
                      properties={
                          "arg1": types.Schema(type=types.Type.INTEGER)
                      },
                  ),
              )
          ),
      ),
      (
          "matching_function_call_with_required_args",
          _get_function_call(
              name="f",
              args={
                  "arg1": str2call.FunctionArgument(
                      value=str2call.Container(typename="constant", fields=1),
                      dtype=tool_types.Int(),
                  ),
              },
          ),
          _get_function_declaration(
              types.FunctionDeclaration(
                  name="f",
                  parameters=types.Schema(
                      type=types.Type.OBJECT,
                      properties={
                          "arg1": types.Schema(
                              type=types.Type.INTEGER,
                          ),
                          "arg2": types.Schema(
                              type=types.Type.INTEGER,
                          ),
                      },
                      required=["arg1"],
                  ),
              )
          ),
      ),
      (
          "matching_function_call_with_optional_args_set_to_none",
          _get_function_call(
              name="f",
              args={
                  "arg1": str2call.FunctionArgument(
                      value=str2call.Container(
                          typename="constant", fields=None
                      ),
                      dtype=tool_types.NoneType(),
                  ),
                  "arg2": str2call.FunctionArgument(
                      value=str2call.Container(typename="constant", fields=1),
                      dtype=tool_types.Int(),
                  ),
              },
          ),
          _get_function_declaration(
              types.FunctionDeclaration(
                  name="f",
                  parameters=types.Schema(
                      type=types.Type.OBJECT,
                      properties={
                          "arg1": types.Schema(
                              type=types.Type.INTEGER,
                          ),
                          "arg2": types.Schema(
                              type=types.Type.INTEGER,
                          ),
                      },
                      required=["arg2"],
                  ),
              )
          ),
      ),
      (
          "matching_function_call_with_array_of_objects",
          _get_function_call(
              name="f",
              args={
                  "arg1": str2call.FunctionArgument(
                      value=str2call.Container(typename="list", fields=[1.2]),
                      dtype=tool_types.Array(
                          typename="list",
                          inner_type=tool_types.Object(
                              typename="arg1",
                              fields={"arg1": tool_types.Float()},
                          ),
                      ),
                  )
              },
          ),
          _get_function_declaration(
              types.FunctionDeclaration(
                  name="f",
                  parameters=types.Schema(
                      type=types.Type.OBJECT,
                      properties={
                          "arg1": types.Schema(
                              type=types.Type.ARRAY,
                              items=types.Schema(
                                  type=types.Type.OBJECT,
                                  properties={
                                      "arg1": types.Schema(
                                          type=types.Type.NUMBER,
                                      )
                                  },
                              ),
                          )
                      },
                  ),
              )
          ),
      ),
      (
          "matching_function_call_with_objects_with_required_fields",
          _get_function_call(
              name="f",
              args={
                  "arg1": str2call.FunctionArgument(
                      value=str2call.Container(
                          typename="arg1", fields={"objarg1": 1.2}
                      ),
                      dtype=tool_types.Object(
                          typename="arg1",
                          fields={
                              "objarg1": tool_types.Float(),
                          },
                          required_fields={"objarg1"},
                      ),
                  )
              },
          ),
          _get_function_declaration(
              types.FunctionDeclaration(
                  name="f",
                  parameters=types.Schema(
                      type=types.Type.OBJECT,
                      properties={
                          "arg1": types.Schema(
                              type=types.Type.OBJECT,
                              properties={
                                  "objarg1": types.Schema(
                                      type=types.Type.NUMBER,
                                  ),
                                  "objarg2": types.Schema(
                                      type=types.Type.NUMBER,
                                  ),
                              },
                              required=["objarg1"],
                          )
                      },
                  ),
              )
          ),
      ),
      (
          "matching_function_call_with_objects_with_optional_fields_set_to_none",
          _get_function_call(
              name="f",
              args={
                  "arg1": str2call.FunctionArgument(
                      value=str2call.Container(
                          typename="arg1",
                          fields={"objarg1": 1.2, "objarg2": None},
                      ),
                      dtype=tool_types.Object(
                          typename="arg1",
                          fields={
                              "objarg1": tool_types.Float(),
                              "objarg2": tool_types.NoneType(),
                          },
                          required_fields={"objarg1"},
                      ),
                  )
              },
          ),
          _get_function_declaration(
              types.FunctionDeclaration(
                  name="f",
                  parameters=types.Schema(
                      type=types.Type.OBJECT,
                      properties={
                          "arg1": types.Schema(
                              type=types.Type.OBJECT,
                              properties={
                                  "objarg1": types.Schema(
                                      type=types.Type.NUMBER,
                                  ),
                                  "objarg2": types.Schema(
                                      type=types.Type.NUMBER,
                                  ),
                              },
                              required=["objarg1"],
                          )
                      },
                  ),
              )
          ),
      ),
      (
          "matching_function_call_with_objects_with_optional_fields_missing",
          _get_function_call(
              name="f",
              args={
                  "arg1": str2call.FunctionArgument(
                      value=str2call.Container(
                          typename="arg1", fields={"objarg1": 1.2}
                      ),
                      dtype=tool_types.Object(
                          typename="arg1",
                          fields={
                              "objarg1": tool_types.Float(),
                          },
                          required_fields={"objarg1"},
                      ),
                  )
              },
          ),
          _get_function_declaration(
              types.FunctionDeclaration(
                  name="f",
                  parameters=types.Schema(
                      type=types.Type.OBJECT,
                      properties={
                          "arg1": types.Schema(
                              type=types.Type.OBJECT,
                              properties={
                                  "objarg1": types.Schema(
                                      type=types.Type.NUMBER,
                                  ),
                                  "objarg2": types.Schema(
                                      type=types.Type.NUMBER,
                                  ),
                              },
                              required=["objarg1"],
                          )
                      },
                  ),
              )
          ),
      ),
  )
  def test_validates_matching_function_call(
      self, function_call: str2call.FunctionCall, tool: types.Tool
  ):
    self.assertTrue(
        validate_function_call.validate_function_call(function_call, tool)
    )

  @parameterized.named_parameters(
      (
          "wrong_function_name",
          _get_function_call(name="f", args={}),
          _get_function_declaration(
              types.FunctionDeclaration(
                  name="g",
              )
          ),
      ),
      (
          "missing_required_argument",
          _get_function_call(
              name="f",
              args={
                  "arg2": str2call.FunctionArgument(
                      value=str2call.Container(typename="constant", fields=1),
                      dtype=tool_types.Int(),
                  ),
              },
          ),
          _get_function_declaration(
              types.FunctionDeclaration(
                  name="f",
                  parameters=types.Schema(
                      type=types.Type.OBJECT,
                      properties={
                          "arg1": types.Schema(
                              type=types.Type.INTEGER,
                          ),
                          "arg2": types.Schema(
                              type=types.Type.INTEGER,
                          ),
                      },
                      required=["arg1"],
                  ),
              )
          ),
      ),
      (
          "bogus_argument",
          _get_function_call(
              name="f",
              args={
                  "arg1": str2call.FunctionArgument(
                      value=str2call.Container(typename="constant", fields=1),
                      dtype=tool_types.Int(),
                  ),
                  "arg2": str2call.FunctionArgument(
                      value=str2call.Container(typename="constant", fields=1),
                      dtype=tool_types.Int(),
                  ),
                  "bogus_arg": str2call.FunctionArgument(
                      value=str2call.Container(typename="constant", fields=1),
                      dtype=tool_types.Int(),
                  ),
              },
          ),
          _get_function_declaration(
              types.FunctionDeclaration(
                  name="f",
                  parameters=types.Schema(
                      type=types.Type.OBJECT,
                      properties={
                          "arg1": types.Schema(
                              type=types.Type.INTEGER,
                          ),
                          "arg2": types.Schema(
                              type=types.Type.INTEGER,
                          ),
                      },
                  ),
              )
          ),
      ),
      (
          "object_arg_with_missing_required_field",
          _get_function_call(
              name="f",
              args={
                  "arg1": str2call.FunctionArgument(
                      value=str2call.Container(
                          typename="arg1", fields={"objarg2": 1.2}
                      ),
                      dtype=tool_types.Object(
                          typename="arg1",
                          fields={
                              "objarg2": tool_types.Float(),
                          },
                          required_fields={"objarg1"},
                      ),
                  )
              },
          ),
          _get_function_declaration(
              types.FunctionDeclaration(
                  name="f",
                  parameters=types.Schema(
                      type=types.Type.OBJECT,
                      properties={
                          "arg1": types.Schema(
                              type=types.Type.OBJECT,
                              properties={
                                  "objarg1": types.Schema(
                                      type=types.Type.NUMBER,
                                  ),
                                  "objarg2": types.Schema(
                                      type=types.Type.NUMBER,
                                  ),
                              },
                              required=["objarg1"],
                          )
                      },
                  ),
              )
          ),
      ),
      (
          "object_arg_bogus_field",
          _get_function_call(
              name="f",
              args={
                  "arg1": str2call.FunctionArgument(
                      value=str2call.Container(
                          typename="arg1",
                          fields={"objarg1": 1.2, "bogus_field": 1.2},
                      ),
                      dtype=tool_types.Object(
                          typename="arg1",
                          fields={
                              "objarg1": tool_types.Float(),
                              "bogus_field": tool_types.Float(),
                          },
                          required_fields={"objarg1"},
                      ),
                  )
              },
          ),
          _get_function_declaration(
              types.FunctionDeclaration(
                  name="f",
                  parameters=types.Schema(
                      type=types.Type.OBJECT,
                      properties={
                          "arg1": types.Schema(
                              type=types.Type.OBJECT,
                              properties={
                                  "objarg1": types.Schema(
                                      type=types.Type.NUMBER,
                                  ),
                                  "objarg2": types.Schema(
                                      type=types.Type.NUMBER,
                                  ),
                              },
                              required=["objarg1"],
                          )
                      },
                  ),
              )
          ),
      ),
      (
          "function_with_wrong_type",
          _get_function_call(
              name="f",
              args={
                  "arg1": str2call.FunctionArgument(
                      value=str2call.Container(typename="constant", fields=1),
                      dtype=tool_types.Int(),
                  ),
              },
          ),
          _get_function_declaration(
              types.FunctionDeclaration(
                  name="f",
                  parameters=types.Schema(
                      type=types.Type.OBJECT,
                      properties={
                          "arg1": types.Schema(
                              type=types.Type.STRING,
                          ),
                      },
                  ),
              )
          ),
      ),
      (
          "obj_arg_with_wrong_type",
          _get_function_call(
              name="f",
              args={
                  "arg1": str2call.FunctionArgument(
                      value=str2call.Container(
                          typename="arg1", fields={"objarg1": 1.2}
                      ),
                      dtype=tool_types.Object(
                          typename="arg1",
                          fields={
                              "objarg1": tool_types.Float(),
                          },
                          required_fields={"objarg1"},
                      ),
                  )
              },
          ),
          _get_function_declaration(
              types.FunctionDeclaration(
                  name="f",
                  parameters=types.Schema(
                      type=types.Type.OBJECT,
                      properties={
                          "arg1": types.Schema(
                              type=types.Type.INTEGER,
                              properties={
                                  "objarg1": types.Schema(
                                      type=types.Type.NUMBER,
                                  ),
                              },
                              required=["objarg1"],
                          )
                      },
                  ),
              )
          ),
      ),
      (
          "list_arg_with_wrong_type",
          _get_function_call(
              name="f",
              args={
                  "arg1": str2call.FunctionArgument(
                      value=str2call.Container(typename="list", fields=[1.2]),
                      dtype=tool_types.Array(
                          typename="list",
                          inner_type=tool_types.Object(
                              typename="arg1",
                              fields={"arg1": tool_types.Float()},
                          ),
                      ),
                  )
              },
          ),
          _get_function_declaration(
              types.FunctionDeclaration(
                  name="f",
                  parameters=types.Schema(
                      type=types.Type.OBJECT,
                      properties={
                          "arg1": types.Schema(
                              type=types.Type.ARRAY,
                              items=types.Schema(
                                  type=types.Type.INTEGER,
                              ),
                          )
                      },
                  ),
              )
          ),
      ),
  )
  def test_validates_non_matching_function_call(
      self, function_call: str2call.FunctionCall, tool: types.Tool
  ):
    self.assertFalse(
        validate_function_call.validate_function_call(function_call, tool)
    )

  def test_validates_raw_string_function_call(self):
    function_call = _get_function_call(name="f", args={})
    function_call.raw_string = "f(a=1)"
    tool = _get_function_declaration(
        types.FunctionDeclaration(
            name="f",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "arg1": types.Schema(
                        type=types.Type.INTEGER,
                    ),
                },
            ),
        )
    )
    self.assertTrue(
        validate_function_call.validate_function_call(function_call, tool)
    )

  def test_validates_raw_string_function_call_with_skip_on_raw_string(self):
    raw_string = "blabla"
    function_call = _get_function_call(
        name="f",
        args={
            "a": str2call.FunctionArgument(
                value=str2call.Container(typename="constant", fields=1),
                dtype=tool_types.Int(),
            )
        },
    )
    function_call.raw_string = raw_string
    tool = _get_function_declaration(
        types.FunctionDeclaration(
            name="f",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "a": types.Schema(
                        type=types.Type.INTEGER,
                    ),
                },
            ),
        )
    )
    self.assertTrue(
        validate_function_call.validate_function_call(
            function_call, tool, skip_on_raw_string=False
        )
    )
    self.assertEqual(str(function_call), raw_string)


if __name__ == "__main__":
  googletest.main()
