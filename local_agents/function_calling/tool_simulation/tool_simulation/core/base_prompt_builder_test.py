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

from typing import cast
from absl.testing import absltest
from tool_simulation.core import base_prompt_builder
from tool_simulation.core import testing_utils

BaseChunk = base_prompt_builder.BaseChunk
BaseTurn = base_prompt_builder.BaseTurn
ChunkKind = base_prompt_builder.ChunkKind
BasePromptBuilder = base_prompt_builder.BasePromptBuilder
TestChunk = testing_utils.TestChunk
TestTurn = testing_utils.TestTurn
TestPromptBuilder = testing_utils.TestPromptBuilder


class BaseChunkTest(absltest.TestCase):

  def test_chunk_creation(self):
    chunk = TestChunk(content="Hello", kind=ChunkKind.CONTENT)
    self.assertEqual(chunk.content, "Hello")
    self.assertEqual(chunk.kind, ChunkKind.CONTENT)

  def test_chunk_str(self):
    chunk = TestChunk(content="HI", kind=ChunkKind.CONTENT)
    self.assertEqual(str(chunk), "<chunk_start>[content]HI<chunk_end>")


class BaseTurnTest(absltest.TestCase):

  def test_turn_creation_no_content(self):
    turn = TestTurn(role="user")
    self.assertEqual(turn.role, "user")
    self.assertEqual(turn.content, [])
    self.assertEqual(turn.inner_content, "")
    self.assertEqual(str(turn), "<turn_start>user\n<turn_end>")

  def test_turn_creation_single_chunk(self):
    chunk = TestChunk("Hello")
    turn = TestTurn(role="model", content=[chunk])
    self.assertEqual(turn.role, "model")
    self.assertEqual(turn.content, [chunk])
    self.assertEqual(
        turn.inner_content, "<chunk_start>[content]Hello<chunk_end>"
    )
    self.assertEqual(
        str(turn),
        "<turn_start>model\n<chunk_start>[content]Hello<chunk_end><turn_end>",
    )

  def test_turn_creation_list_chunks(self):
    chunk1 = TestChunk("Hi")
    chunk2 = TestChunk("Tool Call", kind=ChunkKind.TOOL_CALL)
    turn = TestTurn(role="user", content=[chunk1, chunk2])
    self.assertEqual(turn.role, "user")
    self.assertEqual(turn.content, [chunk1, chunk2])
    expected_inner = (
        "<chunk_start>[content]Hi<chunk_end>\n<chunk_start>[tool_call]Tool"
        " Call<chunk_end>"
    )
    self.assertEqual(turn.inner_content, expected_inner)
    self.assertEqual(str(turn), f"<turn_start>user\n{expected_inner}<turn_end>")

  def test_role_setter(self):
    turn = TestTurn(role="user", content=[TestChunk("Test")])
    self.assertEqual(turn.role, "user")
    turn.role = "model"
    self.assertEqual(turn.role, "model")
    self.assertEqual(
        str(turn),
        "<turn_start>model\n<chunk_start>[content]Test<chunk_end><turn_end>",
    )

  def test_content_setter_list(self):
    turn = TestTurn(role="user")
    chunk1 = TestChunk("New1")
    chunk2 = TestChunk("New2")
    turn.content = [chunk1, chunk2]
    self.assertEqual(turn.content, [chunk1, chunk2])
    expected_inner = "<chunk_start>[content]New1<chunk_end>\n<chunk_start>[content]New2<chunk_end>"
    self.assertEqual(turn.inner_content, expected_inner)

  def test_add_chunk(self):
    turn = TestTurn(role="model")
    chunk1 = TestChunk("First")
    chunk2 = TestChunk("Second")
    turn.add_chunk(chunk1)
    self.assertEqual(turn.content, [chunk1])
    turn.add_chunk(chunk2)
    self.assertEqual(turn.content, [chunk1, chunk2])
    expected_inner = "<chunk_start>[content]First<chunk_end>\n<chunk_start>[content]Second<chunk_end>"
    self.assertEqual(turn.inner_content, expected_inner)


class BasePromptBuilderTest(absltest.TestCase):

  def test_initialization_success(self):
    builder = TestPromptBuilder()
    self.assertTrue(issubclass(builder._turn_class, BaseTurn))
    self.assertEqual(builder._turn_class, TestTurn)
    self.assertTrue(issubclass(builder._chunk_class, BaseChunk))
    self.assertEqual(builder._chunk_class, TestChunk)
    self.assertEqual(builder._state, [])
    self.assertIsNone(builder._current_turn)

  def test_role_properties(self):
    builder = TestPromptBuilder()
    self.assertEqual(builder.user_role, "user")
    self.assertEqual(builder.model_role, "model")
    self.assertEqual(builder.tool_role, "tool")

  def test_begin_turn(self):
    builder = TestPromptBuilder()
    builder.begin_turn("test_role")
    self.assertIsNotNone(builder._current_turn)
    self.assertIsInstance(builder._current_turn, TestTurn)
    self.assertIsNotNone(builder._current_turn)
    self.assertEqual(cast(BaseTurn, builder._current_turn).role, "test_role")
    self.assertEqual(cast(BaseTurn, builder._current_turn).content, [])

  def test_begin_turn_when_already_in_turn_raises_value_error(self):
    builder = TestPromptBuilder()
    builder.begin_turn("test_role")
    with self.assertRaisesRegex(ValueError, "Cannot begin a new turn"):
      builder.begin_turn("another_role")

  def test_end_turn_success(self):
    builder = TestPromptBuilder()
    builder.begin_turn("test_role")
    builder.add_content(TestChunk("Some content"))
    builder.end_turn()
    self.assertIsNone(builder._current_turn)
    self.assertLen(builder._state, 1)
    self.assertIsInstance(builder._state[0], TestTurn)
    self.assertEqual(builder._state[0].role, "test_role")
    self.assertLen(builder._state[0].content, 1)
    self.assertEqual(builder._state[0].content[0].content, "Some content")

  def test_end_turn_without_begin_raises_value_error(self):
    builder = TestPromptBuilder()
    with self.assertRaisesRegex(
        ValueError, "Cannot end a turn that has not been started"
    ):
      builder.end_turn()

  def test_end_turn_cant_be_empty(self):
    builder = TestPromptBuilder()
    builder.begin_turn("test_role")
    with self.assertRaisesRegex(
        ValueError, "Cannot end a turn that has no content"
    ):
      builder.end_turn()

  def test_double_end_turn_raises_value_error(self):
    builder = TestPromptBuilder()
    builder.begin_turn("test_role")
    builder.add_content(TestChunk("Some content"))
    builder.end_turn()
    with self.assertRaisesRegex(
        ValueError, "Cannot end a turn that has not been started"
    ):
      builder.end_turn()

  def test_add_content_chunk_object(self):
    builder = TestPromptBuilder()
    builder.begin_turn("test_role")
    chunk_obj = TestChunk("Pre-made", kind=ChunkKind.TOOL_RESULT)
    builder.add_content(chunk_obj)
    self.assertIsNotNone(builder._current_turn)
    current_turn = cast(TestTurn, builder._current_turn)
    self.assertLen(current_turn.content, 1)
    self.assertIs(current_turn.content[0], chunk_obj)
    self.assertEqual(current_turn.content[0].content, "Pre-made")
    self.assertEqual(current_turn.content[0].kind, ChunkKind.TOOL_RESULT)

  def test_add_content_chunk_object_ignores_kind_kwargs(self):
    builder = TestPromptBuilder()
    builder.begin_turn("test_role")
    chunk_obj = TestChunk("Pre-made", kind=ChunkKind.CONTENT)
    builder.add_content(chunk_obj)
    self.assertIsNotNone(builder._current_turn)
    current_turn = cast(TestTurn, builder._current_turn)
    self.assertLen(current_turn.content, 1)
    self.assertIs(current_turn.content[0], chunk_obj)
    self.assertEqual(current_turn.content[0].kind, ChunkKind.CONTENT)

  def test_add_content_without_begin_turn_raises_value_error(self):
    builder = TestPromptBuilder()
    with self.assertRaisesRegex(
        ValueError, "Cannot add content - no turn has been started"
    ):
      builder.add_content(TestChunk("Some content"))

  def test_full_conversation_flow(self):
    builder = TestPromptBuilder()
    builder.begin_turn(builder.user_role)
    builder.add_content(TestChunk("Hello there."))
    builder.end_turn()
    builder.begin_turn(builder.model_role)
    builder.add_content(TestChunk("General Kenobi!"))
    chunk_tc = TestChunk("use_lightsaber()", kind=ChunkKind.TOOL_CALL)
    builder.add_content(chunk_tc)
    builder.add_content(
        TestChunk("Lightsaber activated.", kind=ChunkKind.TOOL_RESULT)
    )
    builder.end_turn()

    state = builder._state
    self.assertLen(state, 2)

    self.assertEqual(state[0].role, builder.user_role)
    self.assertLen(state[0].content, 1)
    self.assertEqual(state[0].content[0].content, "Hello there.")
    self.assertEqual(state[0].content[0].kind, ChunkKind.CONTENT)
    self.assertEqual(
        str(state[0]),
        "<turn_start>user\n<chunk_start>[content]Hello"
        " there.<chunk_end><turn_end>",
    )

    self.assertEqual(state[1].role, builder.model_role)
    self.assertLen(state[1].content, 3)
    self.assertEqual(state[1].content[0].content, "General Kenobi!")
    self.assertEqual(state[1].content[0].kind, ChunkKind.CONTENT)
    self.assertIs(state[1].content[1], chunk_tc)
    self.assertEqual(state[1].content[2].content, "Lightsaber activated.")
    self.assertEqual(state[1].content[2].kind, ChunkKind.TOOL_RESULT)

  def test_convenience_methods(self):
    builder = TestPromptBuilder()
    builder.begin_turn(builder.user_role)
    builder.add_content(TestChunk("First user message."))
    builder.end_turn()
    builder.begin_turn(builder.model_role)
    tool_call = TestChunk("calculate(1+1)", kind=ChunkKind.TOOL_CALL)
    tool_result = TestChunk("2", kind=ChunkKind.TOOL_RESULT)
    builder.add_content(TestChunk("Response text."))
    builder.add_content(tool_call)
    builder.add_content(tool_result)
    builder.end_turn()

    state = builder._state
    self.assertLen(state, 2)
    self.assertEqual(state[0].role, builder.user_role)
    self.assertEqual(state[0].content[0].content, "First user message.")
    self.assertEqual(state[1].role, builder.model_role)
    self.assertLen(state[1].content, 3)
    self.assertEqual(state[1].content[0].content, "Response text.")
    self.assertEqual(state[1].content[0].kind, ChunkKind.CONTENT)
    self.assertIs(state[1].content[1], tool_call)
    self.assertIs(state[1].content[2], tool_result)

  def test_get_chunk(self):
    builder = TestPromptBuilder()
    chunk = builder.get_chunk("Test content", kind=ChunkKind.TOOL_RESULT)
    self.assertEqual(chunk.content, "Test content")
    self.assertEqual(chunk.kind, ChunkKind.TOOL_RESULT)

  def test_get_prompt(self):
    builder = TestPromptBuilder()
    builder.begin_turn(builder.user_role)
    builder.add_content(TestChunk("First user message."))
    builder.end_turn()
    builder.begin_turn(builder.model_role)
    tool_call = TestChunk("calculate(1+1)", kind=ChunkKind.TOOL_CALL)
    tool_result = TestChunk("2", kind=ChunkKind.TOOL_RESULT)
    builder.add_content(TestChunk("Response"))
    builder.add_content(tool_call)
    builder.add_content(tool_result)
    builder.end_turn()

    prompt = builder.get_prompt()
    self.assertEqual(
        prompt,
        "<turn_start>user\n<chunk_start>[content]First user"
        " message.<chunk_end><turn_end>"
        "<turn_start>model\n<chunk_start>[content]Response<chunk_end>\n<chunk_start>[tool_call]calculate(1+1)<chunk_end>\n<chunk_start>[tool_result]2<chunk_end><turn_end>",
    )

  def test_get_prompt_empty(self):
    builder = TestPromptBuilder()
    builder.begin_turn(builder.user_role)
    with self.assertRaises(ValueError):
      builder.get_prompt()

  def test_get_prompt_for_inference(self):
    builder = TestPromptBuilder()
    builder.begin_turn(builder.user_role)
    builder.add_content(TestChunk("First user message."))
    builder.end_turn()

    self.assertEqual(
        builder.get_prompt(inference=True),
        "<turn_start>user\n<chunk_start>[content]First user"
        " message.<chunk_end><turn_end><turn_start>model\n",
    )

  def test_get_state(self):
    builder = TestPromptBuilder()
    builder.begin_turn(builder.user_role)
    builder.add_content(TestChunk("First user message."))
    builder.end_turn()
    builder.begin_turn(builder.model_role)
    tool_call = TestChunk("calculate(1+1)", kind=ChunkKind.TOOL_CALL)
    tool_result = TestChunk("2", kind=ChunkKind.TOOL_RESULT)
    builder.add_content(TestChunk("Response"))
    builder.add_content(tool_call)
    builder.add_content(tool_result)
    builder.end_turn()

    state = builder.get_state()
    self.assertLen(state, 2)
    self.assertEqual(state[0].role, builder.user_role)
    self.assertEqual(state[0].content[0].content, "First user message.")
    self.assertEqual(state[1].role, builder.model_role)
    self.assertLen(state[1].content, 3)
    self.assertEqual(state[1].content[0].content, "Response")

    self.assertEqual(state[1].content[1].content, tool_call.content)
    self.assertEqual(state[1].content[1].kind, tool_call.kind)
    self.assertEqual(str(state[1].content[1]), str(tool_call))
    self.assertEqual(state[1].content[2].content, tool_result.content)
    self.assertEqual(state[1].content[2].kind, tool_result.kind)
    self.assertEqual(str(state[1].content[2]), str(tool_result))

  def test_get_state_mutable(self):
    builder = TestPromptBuilder()
    builder.begin_turn(builder.user_role)
    builder.add_content(TestChunk("First user message."))
    builder.end_turn()
    builder.begin_turn(builder.model_role)
    builder.add_content(TestChunk("Response"))
    builder.end_turn()
    self.assertLen(builder.get_state_mutable(), 2)
    builder.get_state_mutable().pop()
    self.assertLen(builder.get_state(), 1)


if __name__ == "__main__":
  googletest.main()
