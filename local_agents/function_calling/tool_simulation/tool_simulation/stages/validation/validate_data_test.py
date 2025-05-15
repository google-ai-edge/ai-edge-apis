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
from tool_simulation.core import base_prompt_builder
from tool_simulation.stages.testing_utils import testing_commons
from tool_simulation.stages.validation import validate_data
from tool_simulation.stages.validation import validation_prompt_builder


class ValidateDataTest(absltest.TestCase):

  def test_empty_state(self):
    source_builder = testing_commons.TestPromptBuilder()
    validation_builder = validation_prompt_builder.ValidationPromptBuilder()
    self.assertEqual(
        validate_data.populate_validation_builder(
            validation_builder, source_builder
        ).get_prompt(),
        "",
    )

  def test_skips_system_turns(self):
    source_builder = testing_commons.TestPromptBuilder()
    # create artificial system turn
    source_builder.begin_turn("system")
    source_builder.add_content(
        testing_commons.TestChunk(
            "Hello", kind=base_prompt_builder.ChunkKind.CONTENT
        )
    )
    source_builder.end_turn()
    validation_builder = validation_prompt_builder.ValidationPromptBuilder()
    self.assertEqual(
        validate_data.populate_validation_builder(
            validation_builder, source_builder
        ).get_prompt(),
        "",
    )

  def test_user_turn_text(self):
    source_builder = testing_commons.TestPromptBuilder()
    source_builder.begin_turn(source_builder.user_role)
    source_builder.add_content(testing_commons.TestChunk("Hello"))
    source_builder.end_turn()
    validation_builder = validation_prompt_builder.ValidationPromptBuilder()
    self.assertEqual(
        validate_data.populate_validation_builder(
            validation_builder, source_builder
        ).get_prompt(),
        "[User]\nHello\n",
    )

  def test_user_turn_function_reply(self):
    source_builder = testing_commons.TestPromptBuilder()
    source_builder.begin_turn(source_builder.user_role)
    source_builder.add_content(
        testing_commons.TestChunk(
            "Hello", kind=base_prompt_builder.ChunkKind.TOOL_RESULT
        )
    )
    source_builder.end_turn()
    validation_builder = validation_prompt_builder.ValidationPromptBuilder()
    self.assertEqual(
        validate_data.populate_validation_builder(
            validation_builder, source_builder
        ).get_prompt(),
        "[Environment]\nHello\n",
    )

  def test_tool_turn_function_reply(self):
    source_builder = testing_commons.TestPromptBuilder()
    source_builder.begin_turn(source_builder.tool_role)
    source_builder.add_content(
        testing_commons.TestChunk(
            "Hello", kind=base_prompt_builder.ChunkKind.TOOL_RESULT
        )
    )
    source_builder.end_turn()
    validation_builder = validation_prompt_builder.ValidationPromptBuilder()
    self.assertEqual(
        validate_data.populate_validation_builder(
            validation_builder, source_builder
        ).get_prompt(),
        "[Environment]\nHello\n",
    )

  def test_model_multiple_turns(self):
    source_builder = testing_commons.TestPromptBuilder()
    source_builder.begin_turn(source_builder.model_role)
    source_builder.add_content(
        testing_commons.TestChunk(
            "Hello", kind=base_prompt_builder.ChunkKind.CONTENT
        )
    )
    source_builder.add_content(
        testing_commons.TestChunk(
            "ToolCall", kind=base_prompt_builder.ChunkKind.TOOL_CALL
        )
    )
    source_builder.end_turn()
    validation_builder = validation_prompt_builder.ValidationPromptBuilder()
    self.assertEqual(
        validate_data.populate_validation_builder(
            validation_builder, source_builder
        ).get_prompt(),
        "[Assistant]\nHello\n[Assistant]\nToolCall\n",
    )

  def test_model_turn_tool_call(self):
    source_builder = testing_commons.TestPromptBuilder()
    source_builder.begin_turn(source_builder.model_role)
    source_builder.add_content(
        testing_commons.TestChunk(
            "ToolCall", kind=base_prompt_builder.ChunkKind.TOOL_CALL
        )
    )
    source_builder.end_turn()
    validation_builder = validation_prompt_builder.ValidationPromptBuilder()
    self.assertEqual(
        validate_data.populate_validation_builder(
            validation_builder, source_builder
        ).get_prompt(),
        "[Assistant]\nToolCall\n",
    )

  def test_multiple_turns_with_instruction(self):
    source_builder = testing_commons.TestPromptBuilder()
    source_builder.begin_turn(source_builder.user_role)
    source_builder.add_content(
        testing_commons.TestChunk(
            "Hello", kind=base_prompt_builder.ChunkKind.CONTENT
        )
    )
    source_builder.end_turn()

    source_builder.begin_turn(source_builder.model_role)
    source_builder.add_content(
        testing_commons.TestChunk(
            "Hi", kind=base_prompt_builder.ChunkKind.CONTENT
        )
    )
    source_builder.add_content(
        testing_commons.TestChunk(
            "bye", kind=base_prompt_builder.ChunkKind.TOOL_CALL
        )
    )
    source_builder.end_turn()

    source_builder.begin_turn(source_builder.tool_role)
    source_builder.add_content(
        testing_commons.TestChunk(
            "Hello2", kind=base_prompt_builder.ChunkKind.TOOL_RESULT
        )
    )
    source_builder.end_turn()

    validation_builder = validation_prompt_builder.ValidationPromptBuilder()
    validation_builder.system_turn("Hello")
    self.assertEqual(
        validate_data.populate_validation_builder(
            validation_builder, source_builder
        ).get_prompt(),
        (
            "Instruction\nHello\n"
            "[User]\nHello\n"
            "[Assistant]\nHi\n[Assistant]\nbye\n"
            "[Environment]\nHello2\n"
        ),
    )

  def test_throws_illegal_user_roles(self):
    source_builder = testing_commons.TestPromptBuilder()
    source_builder.begin_turn(source_builder.user_role)
    source_builder.add_content(
        testing_commons.TestChunk(
            "Hello", kind=base_prompt_builder.ChunkKind.TOOL_CALL
        )
    )
    source_builder.end_turn()
    validation_builder = validation_prompt_builder.ValidationPromptBuilder()
    with self.assertRaises(ValueError):
      validate_data.populate_validation_builder(
          validation_builder, source_builder
      )

  def test_throws_illegal_model_roles(self):
    source_builder = testing_commons.TestPromptBuilder()
    source_builder.begin_turn(source_builder.model_role)
    source_builder.add_content(
        testing_commons.TestChunk(
            "Hello", kind=base_prompt_builder.ChunkKind.TOOL_RESULT
        )
    )
    source_builder.end_turn()
    validation_builder = validation_prompt_builder.ValidationPromptBuilder()
    with self.assertRaises(ValueError):
      validate_data.populate_validation_builder(
          validation_builder, source_builder
      )

  def test_throws_illegal_tool_roles_content(self):
    source_builder = testing_commons.TestPromptBuilder()
    source_builder.begin_turn(source_builder.tool_role)
    source_builder.add_content(
        testing_commons.TestChunk(
            "Hello", kind=base_prompt_builder.ChunkKind.CONTENT
        )
    )
    source_builder.end_turn()
    validation_builder = validation_prompt_builder.ValidationPromptBuilder()
    with self.assertRaises(ValueError):
      validate_data.populate_validation_builder(
          validation_builder, source_builder
      )

  def test_throws_illegal_tool_roles_tool_call(self):
    source_builder = testing_commons.TestPromptBuilder()
    source_builder.begin_turn(source_builder.tool_role)
    source_builder.add_content(
        testing_commons.TestChunk(
            "Hello", kind=base_prompt_builder.ChunkKind.TOOL_CALL
        )
    )
    source_builder.end_turn()
    validation_builder = validation_prompt_builder.ValidationPromptBuilder()
    with self.assertRaises(ValueError):
      validate_data.populate_validation_builder(
          validation_builder, source_builder
      )

  def test_query_validation_model_yes(self):
    self.assertTrue(
        validate_data.query_validation_model(
            validation_prompt_builder.ValidationPromptBuilder(),
            testing_commons.TestModelInstance(replies=["YES"]),
        )
    )

  def test_query_validation_model_no(self):
    self.assertFalse(
        validate_data.query_validation_model(
            validation_prompt_builder.ValidationPromptBuilder(),
            testing_commons.TestModelInstance(replies=["NO"]),
        )
    )

  def test_query_validation_model_invalid_output_raises(self):
    with self.assertRaises(ValueError):
      _ = validate_data.query_validation_model(
          validation_prompt_builder.ValidationPromptBuilder(),
          testing_commons.TestModelInstance(replies=["DUMMY REPLY"]),
      )

  def test_query_validation_model_none_raises(self):
    with self.assertRaises(ValueError):
      _ = validate_data.query_validation_model(
          validation_prompt_builder.ValidationPromptBuilder(),
          testing_commons.TestModelInstance(replies=[None]),
      )


if __name__ == "__main__":
  googletest.main()
