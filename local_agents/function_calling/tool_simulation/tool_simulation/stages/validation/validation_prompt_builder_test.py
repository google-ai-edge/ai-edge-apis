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
from tool_simulation.stages.validation import validation_prompt_builder


class PromptBuilderTest(absltest.TestCase):

  def test_user_turn(self):
    builder = validation_prompt_builder.ValidationPromptBuilder()
    builder.user_turn("Hello")
    self.assertEqual(builder.get_prompt(), "[User]\nHello\n")

  def test_model_turn(self):
    builder = validation_prompt_builder.ValidationPromptBuilder()
    builder.assistant_turn("Hello")
    self.assertEqual(builder.get_prompt(), "[Assistant]\nHello\n")

  def test_system_turn(self):
    builder = validation_prompt_builder.ValidationPromptBuilder()
    builder.system_turn("Hello")
    self.assertEqual(builder.get_prompt(), "Instruction\nHello\n")

  def test_tool_turn(self):
    builder = validation_prompt_builder.ValidationPromptBuilder()
    builder.tool_turn("Hello")
    self.assertEqual(builder.get_prompt(), "[Environment]\nHello\n")

  def test_multiple_turns(self):
    builder = validation_prompt_builder.ValidationPromptBuilder()
    builder.user_turn("Hello")
    builder.assistant_turn("Hi")
    self.assertEqual(builder.get_prompt(), "[User]\nHello\n[Assistant]\nHi\n")

  def test_empty_turns(self):
    builder = validation_prompt_builder.ValidationPromptBuilder()
    self.assertEqual(builder.get_prompt(), "")

  def test_begin_get_prompt(self):
    builder = validation_prompt_builder.ValidationPromptBuilder()
    builder.begin_user_turn()
    with self.assertRaises(ValueError):
      builder.get_prompt()

  def test_begin_content_get_prompt(self):
    builder = validation_prompt_builder.ValidationPromptBuilder()
    builder.begin_user_turn()
    builder.add_content(validation_prompt_builder.ValidationChunk("Hello"))
    with self.assertRaises(ValueError):
      builder.get_prompt()

  def test_begin_content_end_get_prompt(self):
    builder = validation_prompt_builder.ValidationPromptBuilder()
    builder.begin_user_turn()
    builder.add_content(validation_prompt_builder.ValidationChunk("Hello"))
    builder.end_turn()
    self.assertEqual(builder.get_prompt(), "[User]\nHello\n")

  def test_begin_end_empty_turn(self):
    builder = validation_prompt_builder.ValidationPromptBuilder()
    builder.begin_user_turn()
    with self.assertRaises(ValueError):
      builder.end_turn()

  def test_double_begin_turn(self):
    builder = validation_prompt_builder.ValidationPromptBuilder()
    builder.begin_user_turn()
    with self.assertRaises(ValueError):
      builder.begin_user_turn()

  def test_double_begin_turn_after_content(self):
    builder = validation_prompt_builder.ValidationPromptBuilder()
    builder.begin_user_turn()
    builder.add_content(validation_prompt_builder.ValidationChunk("Hello"))
    with self.assertRaises(ValueError):
      builder.begin_user_turn()

  def test_double_end_turn(self):
    builder = validation_prompt_builder.ValidationPromptBuilder()
    builder.begin_user_turn()
    builder.add_content(validation_prompt_builder.ValidationChunk("Hello"))
    builder.end_turn()
    with self.assertRaises(ValueError):
      builder.end_turn()

  def test_end_turn_not_started(self):
    builder = validation_prompt_builder.ValidationPromptBuilder()
    with self.assertRaises(ValueError):
      builder.end_turn()

  def test_add_content_to_ended_turn(self):
    builder = validation_prompt_builder.ValidationPromptBuilder()
    builder.begin_user_turn()
    builder.add_content(validation_prompt_builder.ValidationChunk("Hello"))
    builder.end_turn()
    with self.assertRaises(ValueError):
      builder.add_content(validation_prompt_builder.ValidationChunk("Hello"))

  def test_add_content_empty(self):
    builder = validation_prompt_builder.ValidationPromptBuilder()
    with self.assertRaises(ValueError):
      builder.add_content(validation_prompt_builder.ValidationChunk("Hello"))

  def test_get_chunk(self):
    builder = validation_prompt_builder.ValidationPromptBuilder()
    chunk = builder.get_chunk(
        "Test content", kind=validation_prompt_builder.ChunkKind.CONTENT
    )
    self.assertEqual(chunk.content, "Test content")
    self.assertEqual(chunk.kind, validation_prompt_builder.ChunkKind.CONTENT)

  def test_get_promopt_for_inference(self):
    builder = validation_prompt_builder.ValidationPromptBuilder()
    builder.user_turn("Hello")
    self.assertEqual(builder.get_prompt(inference=True), builder.get_prompt())

  def test_get_state(self):
    builder = validation_prompt_builder.ValidationPromptBuilder()
    builder.user_turn("Hello")
    builder.assistant_turn("Hi")
    state = builder.get_state()
    self.assertLen(state, 2)
    self.assertEqual(state[0].role, "[User]")
    self.assertEqual(state[0].content[0].content, "Hello")
    self.assertEqual(state[1].role, "[Assistant]")
    self.assertEqual(state[1].content[0].content, "Hi")

  def test_get_state_mutable(self):
    builder = validation_prompt_builder.ValidationPromptBuilder()
    builder.user_turn("Hello")
    builder.assistant_turn("Hi")
    self.assertLen(builder.get_state_mutable(), len(builder.get_state()))
    builder.get_state_mutable().pop()
    self.assertLen(builder.get_state_mutable(), len(builder.get_state()))


class ValidationTurnTest(absltest.TestCase):

  def test_replier_turn(self):
    turn = validation_prompt_builder.ValidationTurn(
        "instruction", [validation_prompt_builder.ValidationChunk("Hello")]
    )
    self.assertEqual(str(turn), "instruction\nHello\n")

  def test_empty_turn(self):
    turn = validation_prompt_builder.ValidationTurn(
        "user", [validation_prompt_builder.ValidationChunk("")]
    )
    self.assertEqual(str(turn), "user\n\n")

  def test_set_role(self):
    turn = validation_prompt_builder.ValidationTurn(
        "user", [validation_prompt_builder.ValidationChunk("Hello")]
    )
    turn.role = "model"
    self.assertEqual(str(turn), "model\nHello\n")

  def test_set_content(self):
    turn = validation_prompt_builder.ValidationTurn(
        "user", [validation_prompt_builder.ValidationChunk("Hello")]
    )
    turn.content = [validation_prompt_builder.ValidationChunk("Hi")]
    self.assertEqual(str(turn), "user\nHi\n")


if __name__ == "__main__":
  googletest.main()
