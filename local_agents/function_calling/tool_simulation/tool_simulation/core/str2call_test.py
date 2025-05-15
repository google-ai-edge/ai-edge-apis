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
from tool_simulation.core import str2call
from tool_simulation.core import tool_types


class Str2callTestTypeDetection(parameterized.TestCase):

  @parameterized.named_parameters(
      (
          "single_arg_int",
          "f(a=1)",
          str2call.Container(typename="constant", fields=1),
          tool_types.Int(),
      ),
      (
          "single_arg_unary_op_int",
          "f(a = -1)",
          str2call.Container(typename="constant", fields=-1),
          tool_types.Int(),
      ),
      (
          "single_arg_unary_op_float",
          "f(a = -.1)",
          str2call.Container(typename="constant", fields=-0.1),
          tool_types.Float(),
      ),
      (
          "single_arg_bool",
          "f(a=True)",
          str2call.Container(typename="constant", fields=True),
          tool_types.Bool(),
      ),
      (
          "single_arg_string",
          "f(a='hello')",
          str2call.Container(typename="constant", fields="hello"),
          tool_types.String(),
      ),
      (
          "single_arg_float",
          "f(a=1.0)",
          str2call.Container(typename="constant", fields=1.0),
          tool_types.Float(),
      ),
      (
          "single_arg_list",
          "f(a=[1, 2, 3])",
          str2call.Container(
              typename="list",
              fields=[
                  str2call.Container(typename="constant", fields=1),
                  str2call.Container(typename="constant", fields=2),
                  str2call.Container(typename="constant", fields=3),
              ],
          ),
          tool_types.Array(inner_type=tool_types.Int()),
      ),
      (
          "single_arg_list_of_object",
          "f(a=[Obj(a=1)])",
          str2call.Container(
              typename="list",
              fields=[
                  str2call.Container(
                      typename="Obj",
                      fields={
                          "a": str2call.Container(
                              typename="constant", fields=1
                          ),
                      },
                  ),
              ],
          ),
          tool_types.Array(
              inner_type=tool_types.Object(
                  typename="Obj",
                  fields={"a": tool_types.Int()},
              )
          ),
      ),
      (
          "single_arg_list_of_list_of_object",
          "f(a=[[O()]])",
          str2call.Container(
              typename="list",
              fields=[
                  str2call.Container(
                      typename="list",
                      fields=[
                          str2call.Container(
                              typename="O",
                              fields={},
                          ),
                      ],
                  ),
              ],
          ),
          tool_types.Array(
              inner_type=tool_types.Array(
                  inner_type=tool_types.Object(
                      typename="O",
                      fields={},
                  )
              )
          ),
      ),
      (
          "single_arg_dict",
          "f(a={'a': 1, 'b': 2})",
          str2call.Container(
              typename="dict",
              fields={
                  "a": str2call.Container(typename="constant", fields=1),
                  "b": str2call.Container(typename="constant", fields=2),
              },
          ),
          tool_types.Dict(
              inner_key_type=tool_types.String(),
              inner_value_type=tool_types.Int(),
          ),
      ),
      (
          "single_arg_dict_int_key",
          "f(a={1 : 1, 2 : 2})",
          str2call.Container(
              typename="dict",
              fields={
                  1: str2call.Container(typename="constant", fields=1),
                  2: str2call.Container(typename="constant", fields=2),
              },
          ),
          tool_types.Dict(
              inner_key_type=tool_types.Int(),
              inner_value_type=tool_types.Int(),
          ),
      ),
      (
          "single_arg_dict_list",
          "f(a={'x': [1, 2, 3]})",
          str2call.Container(
              typename="dict",
              fields={
                  "x": str2call.Container(
                      typename="list",
                      fields=[
                          str2call.Container(typename="constant", fields=1),
                          str2call.Container(typename="constant", fields=2),
                          str2call.Container(typename="constant", fields=3),
                      ],
                  ),
              },
          ),
          tool_types.Dict(
              inner_key_type=tool_types.String(),
              inner_value_type=tool_types.Array(inner_type=tool_types.Int()),
          ),
      ),
      (
          "single_arg_dict_of_dict",
          "f(a={'a': {'a': 1, 'b': 2}})",
          str2call.Container(
              typename="dict",
              fields={
                  "a": str2call.Container(
                      typename="dict",
                      fields={
                          "a": str2call.Container(
                              typename="constant", fields=1
                          ),
                          "b": str2call.Container(
                              typename="constant", fields=2
                          ),
                      },
                  ),
              },
          ),
          tool_types.Dict(
              inner_key_type=tool_types.String(),
              inner_value_type=tool_types.Dict(
                  inner_key_type=tool_types.String(),
                  inner_value_type=tool_types.Int(),
              ),
          ),
      ),
      (
          "object_with_dict",
          "f(a=O(xx = {'x':1}))",
          str2call.Container(
              typename="O",
              fields={
                  "xx": str2call.Container(
                      typename="dict",
                      fields={
                          "x": str2call.Container(
                              typename="constant", fields=1
                          ),
                      },
                  ),
              },
          ),
          tool_types.Object(
              typename="O",
              fields={
                  "xx": tool_types.Dict(
                      inner_key_type=tool_types.String(),
                      inner_value_type=tool_types.Int(),
                  )
              },
          ),
      ),
      (
          "single_arg_list_dict",
          "f(a=[{'x':1}])",
          str2call.Container(
              typename="list",
              fields=[
                  str2call.Container(
                      typename="dict",
                      fields={
                          "x": str2call.Container(
                              typename="constant", fields=1
                          ),
                      },
                  ),
              ],
          ),
          tool_types.Array(
              inner_type=tool_types.Dict(
                  inner_key_type=tool_types.String(),
                  inner_value_type=tool_types.Int(),
              )
          ),
      ),
      (
          "single_arg_list_list_int",
          "f(a=[[1], [2], [3]])",
          str2call.Container(
              typename="list",
              fields=[
                  str2call.Container(
                      typename="list",
                      fields=[
                          str2call.Container(typename="constant", fields=1),
                      ],
                  ),
                  str2call.Container(
                      typename="list",
                      fields=[
                          str2call.Container(typename="constant", fields=2),
                      ],
                  ),
                  str2call.Container(
                      typename="list",
                      fields=[
                          str2call.Container(typename="constant", fields=3),
                      ],
                  ),
              ],
          ),
          tool_types.Array(
              inner_type=tool_types.Array(inner_type=tool_types.Int())
          ),
      ),
      (
          "single_arg_empty_list",
          "f(a=[])",
          str2call.Container(typename="list", fields=[]),
          tool_types.Array(),
      ),
      (
          "single_arg_empty_list_of_int",
          "f(a=[])",
          str2call.Container(typename="list", fields=[]),
          tool_types.Array(inner_type=tool_types.Int()),
      ),
      (
          "object_with_no_args",
          "f(a=O())",
          str2call.Container(typename="O", fields={}),
          tool_types.Object(typename="O", fields={}),
      ),
      (
          "object_with_const",
          "f(a=O(a=1))",
          str2call.Container(
              typename="O",
              fields={
                  "a": str2call.Container(typename="constant", fields=1),
              },
          ),
          tool_types.Object(typename="O", fields={"a": tool_types.Int()}),
      ),
      (
          "object_of_object_of_list_of_const",
          "f(a=O(a=O(b=O(c=[1, 2, 3]))))",
          str2call.Container(
              typename="O",
              fields={
                  "a": str2call.Container(
                      typename="O",
                      fields={
                          "b": str2call.Container(
                              typename="O",
                              fields={
                                  "c": str2call.Container(
                                      typename="list",
                                      fields=[
                                          str2call.Container(
                                              typename="constant", fields=1
                                          ),
                                          str2call.Container(
                                              typename="constant", fields=2
                                          ),
                                          str2call.Container(
                                              typename="constant", fields=3
                                          ),
                                      ],
                                  ),
                              },
                          )
                      },
                  )
              },
          ),
          tool_types.Object(
              typename="O",
              fields={
                  "a": tool_types.Object(
                      typename="O",
                      fields={
                          "b": tool_types.Object(
                              typename="O",
                              fields={
                                  "c": tool_types.Array(
                                      inner_type=tool_types.Int()
                                  )
                              },
                          )
                      },
                  )
              },
          ),
      ),
      (
          "object_of_object_empty_list",
          "f(a=O(a=O(b=O(c=[]))))",
          str2call.Container(
              typename="O",
              fields={
                  "a": str2call.Container(
                      typename="O",
                      fields={
                          "b": str2call.Container(
                              typename="O",
                              fields={
                                  "c": str2call.Container(
                                      typename="list",
                                      fields=[],
                                  ),
                              },
                          )
                      },
                  )
              },
          ),
          tool_types.Object(
              typename="O",
              fields={
                  "a": tool_types.Object(
                      typename="O",
                      fields={
                          "b": tool_types.Object(
                              typename="O",
                              fields={"c": tool_types.Array()},
                          )
                      },
                  )
              },
          ),
      ),
  )
  def test_converts_single_arg(
      self, input_expression, expected_value, expected_type
  ):
    self.assertEqual(
        str2call.parse_function_call_expression(input_expression),
        str2call.FunctionCall(
            "f", {"a": str2call.FunctionArgument(expected_value, expected_type)}
        ),
    )

  @parameterized.named_parameters(
      (
          "args_not_constant_and_not_list",
          "f(a=dadssadasd)",
          ValueError,
          "Unsupported argument type.*",
      ),
      (
          "args_not_function_call",
          "f",
          ValueError,
          "Unsupported expression.",
      ),
      (
          "no_keyword_args",
          "f(None, b=1)",
          ValueError,
          "Positional arguments are not supported.",
      ),
      (
          "wrong_syntax",
          "f)",
          ValueError,
          "Malformed expression:.",
      ),
      (
          "args_repeated",
          "f(aa=1, aa=2)",
          ValueError,
          "Repeated argument.*",
      ),
      (
          "args_unary_obj",
          "f(aa=-A())",
          ValueError,
          "Unsupported type for unary operator.*",
      ),
      (
          "fails_on_unrecognized_type",
          "f(a=2*2)",
          ValueError,
          "Unsupported AST type.*",
      ),
      (
          "fails_on_dict_wrong_key_type",
          "f(a={1.2 : 1})",
          ValueError,
          "Unsupported type for dictionary key.*",
      ),
  )
  def test_fails_on_expression(
      self, input_expression, expected_error_type, expected_error_regex
  ):
    with self.assertRaisesRegex(expected_error_type, expected_error_regex):
      _ = str2call.parse_function_call_expression(input_expression)

  @parameterized.named_parameters(
      (
          "multi_arg",
          "f(a=1, b='hello', c=True, d=1.0, e = O(x=1, z = OO()), f=-1.2)",
          str2call.FunctionCall(
              "f",
              {
                  "a": str2call.FunctionArgument(
                      str2call.Container(typename="constant", fields=1),
                      tool_types.Int(),
                  ),
                  "b": str2call.FunctionArgument(
                      str2call.Container(typename="constant", fields="hello"),
                      tool_types.String(),
                  ),
                  "c": str2call.FunctionArgument(
                      str2call.Container(typename="constant", fields=True),
                      tool_types.Bool(),
                  ),
                  "d": str2call.FunctionArgument(
                      str2call.Container(typename="constant", fields=1.0),
                      tool_types.Float(),
                  ),
                  "e": str2call.FunctionArgument(
                      str2call.Container(
                          typename="O",
                          fields={
                              "x": str2call.Container(
                                  typename="constant", fields=1
                              ),
                              "z": str2call.Container(typename="OO", fields={}),
                          },
                      ),
                      tool_types.Object(
                          typename="O",
                          fields={
                              "x": tool_types.Int(),
                              "z": tool_types.Object(typename="OO", fields={}),
                          },
                      ),
                  ),
                  "f": str2call.FunctionArgument(
                      str2call.Container(typename="constant", fields=-1.2),
                      tool_types.Float(),
                  ),
              },
          ),
      ),
      (
          "none_arg",
          "f(a =None)",
          str2call.FunctionCall(
              "f",
              {
                  "a": str2call.FunctionArgument(
                      str2call.Container(typename="constant", fields=None),
                      tool_types.NoneType(),
                  ),
              },
          ),
      ),
      ("no_args", "f()", str2call.FunctionCall("f", {})),
  )
  def test_converts_edge_cases(self, expression, expected_function_call):
    self.assertEqual(
        str2call.parse_function_call_expression(expression),
        expected_function_call,
    )

  @parameterized.named_parameters(
      (
          "single_arg_int",
          "f(a=1)",
      ),
      (
          "single_arg_bool",
          "f(a=True)",
      ),
      (
          "single_arg_string",
          "f(a='hello')",
      ),
      (
          "single_arg_float",
          "f(a=1.0)",
      ),
      (
          "single_arg_list",
          "f(a=[1, 2, 3])",
      ),
      (
          "single_arg_list_list_int",
          "f(a=[[1], [2], [3]])",
      ),
      (
          "single_arg_empty_list",
          "f(a=[])",
      ),
      (
          "multi_arg",
          "f(a=1, b='hello', c=True, d=1.0)",
      ),
      (
          "none_arg",
          "f(a=None)",
      ),
      (
          "object_arg",
          "f(a=O())",
      ),
      (
          "object_arg_with_args",
          "f(a=O(a=1, b=OO()))",
      ),
      (
          "dict_args",
          "f(a={'a': 1, 'b': 2}, b={1: 1, 2: 2})",
      ),
      (
          "unary_op_arg",
          "f(a=O(aa=-1))",
      ),
      ("no_args", "f()"),
  )
  def test_ast_str(self, expression):
    function_call = str2call.parse_function_call_expression(expression)
    self.assertEqual(str(function_call), expression)

  @parameterized.named_parameters(
      (
          "single_arg_int",
          "f(a=1)",
      ),
      (
          "single_arg_bool",
          "f(a=True)",
      ),
      (
          "single_arg_string",
          "f(a='hello')",
      ),
      (
          "single_arg_float",
          "f(a=1.0)",
      ),
      (
          "single_arg_list",
          "f(a=[1, 2, 3])",
      ),
      (
          "single_arg_list_list_int",
          "f(a=[[1], [2], [3]])",
      ),
      (
          "single_arg_empty_list",
          "f(a=[])",
      ),
      (
          "multi_arg",
          "f(a=1, b='hello', c=True, d=1.0)",
      ),
      (
          "none_arg",
          "f(a=None)",
      ),
      (
          "object_arg",
          "f(a=O())",
      ),
      (
          "object_arg_with_args",
          "f(a=O(a=1, b=OO()))",
      ),
      (
          "dict_args",
          "f(a={'a': 1, 'b': 2}, b={1: 1, 2: 2})",
      ),
      (
          "unary_op_arg",
          "f(a=O(aa=-1))",
      ),
      ("no_args", "f()"),
  )
  def test_raw_str(self, expression):
    function_call = str2call.FunctionCall("f", {}, raw_string=expression)
    self.assertEqual(str(function_call), expression)

  def test_ast_str_fails_on_empty_ast_and_empty_raw_string(self):
    with self.assertRaisesRegex(ValueError, "AST is not initialized."):
      _ = str(str2call.FunctionCall("f", {}))

  def test_raw_string_priority_over_ast(self):
    function_call = str2call.parse_function_call_expression("f(a=1)")
    function_call.raw_string = "f(a=2)"
    self.assertEqual(str(function_call), "f(a=2)")


if __name__ == "__main__":
  googletest.main()
