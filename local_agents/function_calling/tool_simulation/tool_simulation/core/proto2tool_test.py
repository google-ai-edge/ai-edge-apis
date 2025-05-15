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
from tool_simulation.core import proto2tool
from tool_simulation.core import tool_types


_TOOL_NAME = 'test'
_FUNC_NAME = 'myfunc'
_FUNC_DESC = 'myfunc description'
_ARG_DESCRIPTION = 'arg explanation'


def _get_tool_proto(properties: list[dict[str, types.Schema]]) -> types.Tool:
  function_declarations = []
  for index, prop in enumerate(properties):
    function_declarations.append(
        types.FunctionDeclaration(
            name=_FUNC_NAME + str(index),
            description=_FUNC_DESC,
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties=prop,
            ),
        )
    )
  return types.Tool(function_declarations=function_declarations)


def _get_tool_def(
    properties: list[dict[str, tool_types.ArgumentDefinition]],
) -> tool_types.ToolDefinition:
  functions = {}
  for index, prop in enumerate(properties):
    functions[_FUNC_NAME + str(index)] = tool_types.FunctionDefinition(
        _FUNC_NAME + str(index),
        _FUNC_DESC,
        prop,
    )
  return tool_types.ToolDefinition(_TOOL_NAME, functions)


class Proto2ToolTestTypeDetection(parameterized.TestCase):

  @parameterized.named_parameters(
      ('bool', {'type': types.Type.BOOLEAN}, {'dtype': tool_types.Bool()}),
      ('string', {'type': types.Type.STRING}, {'dtype': tool_types.String()}),
      ('float', {'type': types.Type.NUMBER}, {'dtype': tool_types.Float()}),
      ('int', {'type': types.Type.INTEGER}, {'dtype': tool_types.Int()}),
      (
          'array',
          {
              'type': types.Type.ARRAY,
              'items': types.Schema(type=types.Type.NUMBER),
          },
          {'dtype': tool_types.Array(inner_type=tool_types.Float())},
      ),
      (
          'object',
          {
              'type': types.Type.OBJECT,
              'properties': {'arg1': types.Schema(type=types.Type.NUMBER)},
          },
          {
              'dtype': tool_types.Object(
                  typename='arg1', fields={'arg1': tool_types.Float()}
              )
          },
      ),
  )
  def test_single_arg(self, proto_schema_args, expected_tool_args):
    self.assertEqual(
        proto2tool.proto2tool(
            tool_name=_TOOL_NAME,
            tool=_get_tool_proto([{
                'arg1': types.Schema(
                    description=_ARG_DESCRIPTION,
                    **proto_schema_args,
                )
            }]),
        ),
        _get_tool_def([{
            'arg1': tool_types.ArgumentDefinition(
                'arg1', _ARG_DESCRIPTION, **expected_tool_args
            )
        }]),
    )

  @parameterized.named_parameters(
      (
          'unspecified_type',
          [{
              'arg1': types.Schema(
                  type=types.Type.TYPE_UNSPECIFIED,
                  description=_ARG_DESCRIPTION,
              )
          }],
      ),
      (
          'unspecified_type_in_object',
          [{
              'arg1': types.Schema(
                  type=types.Type.OBJECT,
                  description=_ARG_DESCRIPTION,
                  properties={
                      'prop1': types.Schema(
                          type=types.Type.TYPE_UNSPECIFIED,
                      ),
                  },
              )
          }],
      ),
      (
          'unspecified_type_in_array',
          [{
              'arg1': types.Schema(
                  type=types.Type.ARRAY,
                  description=_ARG_DESCRIPTION,
                  items=types.Schema(
                      type=types.Type.TYPE_UNSPECIFIED,
                  ),
              )
          }],
      ),
  )
  def test_unspecified_type(self, proto_properties):
    with self.assertRaisesRegex(
        ValueError, 'Unsupported argument type in function'
    ):
      _ = proto2tool.proto2tool(
          tool_name=_TOOL_NAME,
          tool=_get_tool_proto(properties=proto_properties),
      )


class Proto2ToolTest(absltest.TestCase):

  def test_multi_arg(self):
    self.assertEqual(
        proto2tool.proto2tool(
            tool_name=_TOOL_NAME,
            tool=_get_tool_proto(
                properties=[{
                    'arg1': types.Schema(
                        type=types.Type.STRING,
                        description=_ARG_DESCRIPTION,
                    ),
                    'arg2': types.Schema(
                        type=types.Type.INTEGER,
                        description=_ARG_DESCRIPTION,
                    ),
                }]
            ),
        ),
        _get_tool_def(
            properties=[{
                'arg1': tool_types.ArgumentDefinition(
                    'arg1', _ARG_DESCRIPTION, tool_types.String()
                ),
                'arg2': tool_types.ArgumentDefinition(
                    'arg2', _ARG_DESCRIPTION, tool_types.Int()
                ),
            }]
        ),
    )

  def test_multi_func(self):
    self.assertEqual(
        proto2tool.proto2tool(
            tool_name=_TOOL_NAME,
            tool=_get_tool_proto(
                properties=[
                    {
                        'arg1': types.Schema(
                            type=types.Type.STRING,
                            description=_ARG_DESCRIPTION,
                        ),
                        'arg2': types.Schema(
                            type=types.Type.NUMBER,
                            description=_ARG_DESCRIPTION,
                        ),
                    },
                    {
                        'arg1': types.Schema(
                            type=types.Type.STRING,
                            description=_ARG_DESCRIPTION,
                        ),
                        'arg2': types.Schema(
                            type=types.Type.INTEGER,
                            description=_ARG_DESCRIPTION,
                        ),
                    },
                ]
            ),
        ),
        _get_tool_def(
            properties=[
                {
                    'arg1': tool_types.ArgumentDefinition(
                        'arg1', _ARG_DESCRIPTION, tool_types.String()
                    ),
                    'arg2': tool_types.ArgumentDefinition(
                        'arg2', _ARG_DESCRIPTION, tool_types.Float()
                    ),
                },
                {
                    'arg1': tool_types.ArgumentDefinition(
                        'arg1', _ARG_DESCRIPTION, tool_types.String()
                    ),
                    'arg2': tool_types.ArgumentDefinition(
                        'arg2', _ARG_DESCRIPTION, tool_types.Int()
                    ),
                },
            ]
        ),
    )

  def test_empty_tool(self):
    self.assertEqual(
        proto2tool.proto2tool(
            tool_name=_TOOL_NAME,
            tool=types.Tool(function_declarations=[]),
        ),
        tool_types.ToolDefinition(_TOOL_NAME, {}),
    )

  def test_duplicate_functions(self):
    with self.assertRaisesRegex(ValueError, 'Duplicate function'):
      _ = proto2tool.proto2tool(
          tool_name=_TOOL_NAME,
          tool=types.Tool(
              function_declarations=[
                  types.FunctionDeclaration(name='func'),
                  types.FunctionDeclaration(name='func'),
              ]
          ),
      )

  def test_array_in_object(self):
    self.assertEqual(
        proto2tool.proto2tool(
            tool_name=_TOOL_NAME,
            tool=_get_tool_proto(
                properties=[{
                    'arg1': types.Schema(
                        type=types.Type.OBJECT,
                        description=_ARG_DESCRIPTION,
                        properties={
                            'arr': types.Schema(
                                type=types.Type.ARRAY,
                                items=types.Schema(type=types.Type.NUMBER),
                            )
                        },
                    )
                }]
            ),
        ),
        _get_tool_def(
            properties=[{
                'arg1': tool_types.ArgumentDefinition(
                    'arg1',
                    _ARG_DESCRIPTION,
                    tool_types.Object(
                        typename='arg1',
                        fields={
                            'arr': tool_types.Array(
                                inner_type=tool_types.Float()
                            )
                        },
                    ),
                ),
            }]
        ),
    )

  def test_object_in_array(self):
    self.assertEqual(
        proto2tool.proto2tool(
            tool_name=_TOOL_NAME,
            tool=_get_tool_proto(
                properties=[{
                    'arg1': types.Schema(
                        type=types.Type.ARRAY,
                        description=_ARG_DESCRIPTION,
                        items=types.Schema(
                            type=types.Type.OBJECT,
                            properties={
                                'obj': types.Schema(type=types.Type.NUMBER),
                            },
                        ),
                    )
                }]
            ),
        ),
        _get_tool_def(
            properties=[{
                'arg1': tool_types.ArgumentDefinition(
                    'arg1',
                    _ARG_DESCRIPTION,
                    tool_types.Array(
                        inner_type=tool_types.Object(
                            typename='arg1',
                            fields={'obj': tool_types.Float()},
                        )
                    ),
                ),
            }]
        ),
    )

  def test_required_field_not_found(self):
    with self.assertRaisesRegex(ValueError, 'Missing required'):
      proto2tool.proto2tool(
          tool_name=_TOOL_NAME,
          tool=types.Tool(
              function_declarations=[
                  types.FunctionDeclaration(
                      name=_FUNC_NAME,
                      description=_FUNC_DESC,
                      parameters=types.Schema(
                          type=types.Type.OBJECT,
                          properties={
                              'arg1': types.Schema(
                                  type=types.Type.INTEGER,
                              ),
                          },
                          required=['arg1', 'arg2'],
                      ),
                  )
              ]
          ),
      )

  def test_required_field_not_found_in_object(self):
    with self.assertRaisesRegex(
        ValueError, 'Unsupported argument type in function'
    ):
      proto2tool.proto2tool(
          tool_name=_TOOL_NAME,
          tool=_get_tool_proto(
              properties=[{
                  'arg1': types.Schema(
                      type=types.Type.OBJECT,
                      description=_ARG_DESCRIPTION,
                      properties={
                          'prop1': types.Schema(
                              type=types.Type.INTEGER,
                          ),
                      },
                      required=['prop1', 'prop2'],
                  )
              }]
          ),
      )

  def test_object_with_required_fields(self):
    self.assertEqual(
        proto2tool.proto2tool(
            tool_name=_TOOL_NAME,
            tool=_get_tool_proto(
                properties=[{
                    'arg1': types.Schema(
                        type=types.Type.OBJECT,
                        description=_ARG_DESCRIPTION,
                        properties={
                            'prop1': types.Schema(
                                type=types.Type.INTEGER,
                            ),
                            'prop2': types.Schema(
                                type=types.Type.INTEGER,
                            ),
                        },
                        required=['prop1'],
                    )
                }]
            ),
        ),
        _get_tool_def(
            properties=[{
                'arg1': tool_types.ArgumentDefinition(
                    'arg1',
                    _ARG_DESCRIPTION,
                    tool_types.Object(
                        typename='arg1',
                        fields={
                            'prop1': tool_types.Int(),
                            'prop2': tool_types.Int(),
                        },
                        required_fields={'prop1'},
                    ),
                ),
            }]
        ),
    )

  def test_with_required_args(self):
    self.assertEqual(
        proto2tool.proto2tool(
            tool_name=_TOOL_NAME,
            tool=types.Tool(
                function_declarations=[
                    types.FunctionDeclaration(
                        name=_FUNC_NAME + '0',
                        description=_FUNC_DESC,
                        parameters=types.Schema(
                            type=types.Type.OBJECT,
                            properties={
                                'arg1': types.Schema(
                                    type=types.Type.INTEGER,
                                    description=_ARG_DESCRIPTION,
                                ),
                                'arg2': types.Schema(
                                    type=types.Type.INTEGER,
                                    description=_ARG_DESCRIPTION,
                                ),
                            },
                            required=['arg1'],
                        ),
                    )
                ]
            ),
        ),
        _get_tool_def(
            properties=[{
                'arg1': tool_types.ArgumentDefinition(
                    'arg1',
                    _ARG_DESCRIPTION,
                    tool_types.Int(),
                    required=True,
                ),
                'arg2': tool_types.ArgumentDefinition(
                    'arg2',
                    _ARG_DESCRIPTION,
                    tool_types.Int(),
                    required=False,
                ),
            }]
        ),
    )

  def test_required_arg_not_in_properties(self):
    with self.assertRaisesRegex(ValueError, 'Missing required'):
      _ = proto2tool.proto2tool(
          tool_name=_TOOL_NAME,
          tool=types.Tool(
              function_declarations=[
                  types.FunctionDeclaration(
                      name=_FUNC_NAME + '0',
                      description=_FUNC_DESC,
                      parameters=types.Schema(
                          type=types.Type.OBJECT,
                          properties={
                              'arg1': types.Schema(
                                  type=types.Type.INTEGER,
                                  description=_ARG_DESCRIPTION,
                              ),
                              'arg2': types.Schema(
                                  type=types.Type.INTEGER,
                                  description=_ARG_DESCRIPTION,
                              ),
                          },
                          required=['bogus'],
                      ),
                  )
              ]
          ),
      )

  def test_required_arg_not_in_properties_in_object(self):
    with self.assertRaisesRegex(ValueError, 'Unsupported argument type'):
      _ = proto2tool.proto2tool(
          tool_name=_TOOL_NAME,
          tool=_get_tool_proto(
              properties=[{
                  'arg1': types.Schema(
                      type=types.Type.OBJECT,
                      description=_ARG_DESCRIPTION,
                      properties={
                          'prop1': types.Schema(
                              type=types.Type.INTEGER,
                              description=_ARG_DESCRIPTION,
                          ),
                          'prop2': types.Schema(
                              type=types.Type.INTEGER,
                              description=_ARG_DESCRIPTION,
                          ),
                      },
                      required=['bogus'],
                  )
              }]
          ),
      )


if __name__ == '__main__':
  googletest.main()
