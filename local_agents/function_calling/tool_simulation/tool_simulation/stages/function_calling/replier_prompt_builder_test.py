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
from tool_simulation.stages.function_calling import replier_prompt_builder


class PromptBuilderTest(absltest.TestCase):

  def test_user_turn(self):
    builder = replier_prompt_builder.ReplierPromptBuilder()
    builder.user_turn("Hello")
    self.assertEqual(builder.get_prompt(), "User: Hello\n")

  def test_model_turn(self):
    builder = replier_prompt_builder.ReplierPromptBuilder()
    builder.model_turn("Hello")
    self.assertEqual(builder.get_prompt(), "Assistant: Hello\n")

  def test_tool_role(self):
    builder = replier_prompt_builder.ReplierPromptBuilder()
    with self.assertRaises(NotImplementedError):
      _ = builder.tool_role

  def test_system_turn(self):
    builder = replier_prompt_builder.ReplierPromptBuilder()
    builder.system_turn("Hello")
    self.assertEqual(builder.get_prompt(), "Instruction: Hello\n")

  def test_multiple_turns(self):
    builder = replier_prompt_builder.ReplierPromptBuilder()
    builder.user_turn("Hello")
    builder.model_turn("Hi")
    self.assertEqual(builder.get_prompt(), "User: Hello\n" + "Assistant: Hi\n")

  def test_empty_turns(self):
    builder = replier_prompt_builder.ReplierPromptBuilder()
    self.assertEqual(builder.get_prompt(), "")

  def test_begin_get_prompt(self):
    builder = replier_prompt_builder.ReplierPromptBuilder()
    builder.begin_user_turn()
    with self.assertRaises(ValueError):
      builder.get_prompt()

  def test_begin_content_get_prompt(self):
    builder = replier_prompt_builder.ReplierPromptBuilder()
    builder.begin_user_turn()
    builder.add_content(replier_prompt_builder.ReplierChunk("Hello"))
    with self.assertRaises(ValueError):
      builder.get_prompt()

  def test_begin_content_end_get_prompt(self):
    builder = replier_prompt_builder.ReplierPromptBuilder()
    builder.begin_user_turn()
    builder.add_content(replier_prompt_builder.ReplierChunk("Hello"))
    builder.end_turn()
    self.assertEqual(builder.get_prompt(), "User: Hello\n")

  def test_begin_end_get_prompt(self):
    builder = replier_prompt_builder.ReplierPromptBuilder()
    builder.begin_user_turn()
    with self.assertRaises(ValueError):
      builder.end_turn()

  def test_double_begin_turn(self):
    builder = replier_prompt_builder.ReplierPromptBuilder()
    builder.begin_user_turn()
    with self.assertRaises(ValueError):
      builder.begin_user_turn()

  def test_double_begin_turn_after_content(self):
    builder = replier_prompt_builder.ReplierPromptBuilder()
    builder.begin_user_turn()
    builder.add_content(replier_prompt_builder.ReplierChunk("Hello"))
    with self.assertRaises(ValueError):
      builder.begin_user_turn()

  def test_double_end_turn(self):
    builder = replier_prompt_builder.ReplierPromptBuilder()
    builder.begin_user_turn()
    builder.add_content(replier_prompt_builder.ReplierChunk("Hello"))
    builder.end_turn()
    with self.assertRaises(ValueError):
      builder.end_turn()

  def test_end_turn_not_started(self):
    builder = replier_prompt_builder.ReplierPromptBuilder()
    with self.assertRaises(ValueError):
      builder.end_turn()

  def test_add_content_to_ended_turn(self):
    builder = replier_prompt_builder.ReplierPromptBuilder()
    builder.begin_user_turn()
    builder.add_content(replier_prompt_builder.ReplierChunk("Hello"))
    builder.end_turn()
    with self.assertRaises(ValueError):
      builder.add_content(replier_prompt_builder.ReplierChunk("Hello"))

  def test_add_content_empty(self):
    builder = replier_prompt_builder.ReplierPromptBuilder()
    with self.assertRaises(ValueError):
      builder.add_content(replier_prompt_builder.ReplierChunk(""))

  def test_get_chunk(self):
    builder = replier_prompt_builder.ReplierPromptBuilder()
    chunk = builder.get_chunk(
        "Test content", kind=replier_prompt_builder.ChunkKind.CONTENT
    )
    self.assertEqual(chunk.content, "Test content")
    self.assertEqual(chunk.kind, replier_prompt_builder.ChunkKind.CONTENT)

  def test_get_prompt_for_inference(self):
    builder = replier_prompt_builder.ReplierPromptBuilder()
    builder.user_turn("Hello")
    self.assertEqual(builder.get_prompt(inference=True), builder.get_prompt())

  def test_get_state(self):
    builder = replier_prompt_builder.ReplierPromptBuilder()
    builder.user_turn("Hello")
    builder.model_turn("Hi")
    state = builder.get_state()
    self.assertLen(state, 2)
    self.assertEqual(state[0].role, "User")
    self.assertEqual(state[0].content[0].content, "Hello")
    self.assertEqual(state[1].role, "Assistant")
    self.assertEqual(state[1].content[0].content, "Hi")

  def test_get_state_mutable(self):
    builder = replier_prompt_builder.ReplierPromptBuilder()
    builder.user_turn("Hello")
    builder.model_turn("Hi")
    self.assertLen(builder.get_state_mutable(), len(builder.get_state()))
    builder.get_state_mutable().pop()
    self.assertLen(builder.get_state_mutable(), len(builder.get_state()))


class ReplierTurnTest(absltest.TestCase):

  def test_replier_turn(self):
    turn = replier_prompt_builder.ReplierTurn("instruction", "Hello")
    self.assertEqual(str(turn), "instruction: Hello\n")

  def test_empty_turn(self):
    turn = replier_prompt_builder.ReplierTurn("user", "")
    self.assertEqual(str(turn), "user: \n")

  def test_set_role(self):
    turn = replier_prompt_builder.ReplierTurn("user", "Hello")
    turn.role = "model"
    self.assertEqual(str(turn), "model: Hello\n")

  def test_set_content(self):
    turn = replier_prompt_builder.ReplierTurn("user", "Hello")
    turn.content = "Hi"
    self.assertEqual(str(turn), "user: Hi\n")


if __name__ == "__main__":
  googletest.main()
