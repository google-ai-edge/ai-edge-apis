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

# TODO(b/405415695): Test with multiple functions

from absl.testing import absltest
from absl.testing import parameterized
from tool_simulation.core import gemma_prompt_builder


class GemmaPromptBuilderTest(parameterized.TestCase):

  def test_user_turn(self):
    builder = gemma_prompt_builder.GemmaPromptBuilder()
    builder.user_turn("Hello")
    self.assertEqual(
        builder.get_prompt(), "<start_of_turn>user\nHello<end_of_turn>"
    )

  def test_model_turn(self):
    builder = gemma_prompt_builder.GemmaPromptBuilder()
    builder.model_turn("Hello")
    self.assertEqual(
        builder.get_prompt(), "<start_of_turn>model\nHello<end_of_turn>"
    )

  def test_multiple_turns(self):
    builder = gemma_prompt_builder.GemmaPromptBuilder()
    builder.user_turn("Hello")
    builder.model_turn("Hi")
    self.assertEqual(
        builder.get_prompt(),
        "<start_of_turn>user\n"
        + "Hello"
        + "<end_of_turn>"
        + "<start_of_turn>model\n"
        + "Hi"
        + "<end_of_turn>",
    )

  def test_empty_turns(self):
    builder = gemma_prompt_builder.GemmaPromptBuilder()
    self.assertEqual(builder.get_prompt(), "")

  def test_get_prompt_for_inference(self):
    builder = gemma_prompt_builder.GemmaPromptBuilder()
    builder.user_turn("Hello")
    self.assertEqual(
        builder.get_prompt(inference=True),
        "<start_of_turn>user\nHello<end_of_turn><start_of_turn>model\n",
    )

  def test_append_turns(self):
    builder = gemma_prompt_builder.GemmaPromptBuilder()
    builder.append_turns([
        gemma_prompt_builder.GemmaTurn(
            "user", [gemma_prompt_builder.GemmaChunk("Hello")]
        ),
        gemma_prompt_builder.GemmaTurn(
            "model", [gemma_prompt_builder.GemmaChunk("Hi")]
        ),
    ])
    builder2 = gemma_prompt_builder.GemmaPromptBuilder()
    builder2.user_turn("Hello")
    builder2.model_turn("Hi")
    self.assertEqual(
        builder.get_prompt(),
        builder2.get_prompt(),
    )

    self.assertEqual(
        builder.get_prompt(inference=True),
        builder2.get_prompt(inference=True),
    )

  def test_begin_get_prompt(self):
    builder = gemma_prompt_builder.GemmaPromptBuilder()
    builder.begin_user_turn()
    with self.assertRaises(ValueError):
      builder.get_prompt()
    with self.assertRaises(ValueError):
      builder.get_prompt(inference=True)

  def test_begin_content_get_prompt(self):
    builder = gemma_prompt_builder.GemmaPromptBuilder()
    builder.begin_user_turn()
    builder.add_content(gemma_prompt_builder.GemmaChunk("Hello"))
    with self.assertRaises(ValueError):
      builder.get_prompt()
    with self.assertRaises(ValueError):
      builder.get_prompt(inference=True)

  def test_begin_content_end_get_prompt(self):
    builder = gemma_prompt_builder.GemmaPromptBuilder()
    builder.begin_user_turn()
    builder.add_content(gemma_prompt_builder.GemmaChunk("Hello"))
    builder.end_turn()
    self.assertEqual(
        builder.get_prompt(), "<start_of_turn>user\nHello<end_of_turn>"
    )

  def test_begin_end_get_prompt(self):
    builder = gemma_prompt_builder.GemmaPromptBuilder()
    builder.begin_user_turn()
    builder.add_content(gemma_prompt_builder.GemmaChunk("Hello"))
    builder.end_turn()
    self.assertEqual(
        builder.get_prompt(), "<start_of_turn>user\nHello<end_of_turn>"
    )

  def test_double_begin_turn(self):
    builder = gemma_prompt_builder.GemmaPromptBuilder()
    builder.begin_user_turn()
    with self.assertRaises(ValueError):
      builder.begin_user_turn()

  def test_double_begin_turn_after_content(self):
    builder = gemma_prompt_builder.GemmaPromptBuilder()
    builder.begin_user_turn()
    builder.add_content(gemma_prompt_builder.GemmaChunk("Hello"))
    with self.assertRaises(ValueError):
      builder.begin_user_turn()

  def test_double_end_turn(self):
    builder = gemma_prompt_builder.GemmaPromptBuilder()
    builder.begin_user_turn()
    builder.add_content(gemma_prompt_builder.GemmaChunk("Hello"))
    builder.end_turn()
    with self.assertRaises(ValueError):
      builder.end_turn()

  def test_end_turn_not_started(self):
    builder = gemma_prompt_builder.GemmaPromptBuilder()
    with self.assertRaises(ValueError):
      builder.end_turn()

  def test_add_content_to_ended_turn(self):
    builder = gemma_prompt_builder.GemmaPromptBuilder()
    builder.begin_user_turn()
    builder.add_content(gemma_prompt_builder.GemmaChunk("Hello"))
    builder.end_turn()
    with self.assertRaises(ValueError):
      builder.add_content(gemma_prompt_builder.GemmaChunk("Hello"))

  def test_add_content_empty(self):
    builder = gemma_prompt_builder.GemmaPromptBuilder()
    with self.assertRaises(ValueError):
      builder.add_content(gemma_prompt_builder.GemmaChunk("Hello"))

  def test_empty_turn_content(self):
    builder = gemma_prompt_builder.GemmaPromptBuilder()
    builder.begin_user_turn()
    with self.assertRaises(ValueError):
      builder.end_turn()

  def test_get_state(self):
    instance = gemma_prompt_builder.GemmaPromptBuilder()
    instance.user_turn("Hello")
    instance.model_turn("Hi")
    expected = list(
        map(
            str,
            [
                gemma_prompt_builder.GemmaTurn(
                    "user", [gemma_prompt_builder.GemmaChunk("Hello")]
                ),
                gemma_prompt_builder.GemmaTurn(
                    "model", [gemma_prompt_builder.GemmaChunk("Hi")]
                ),
            ],
        )
    )
    got = list(map(str, instance.get_state()))
    self.assertEqual(expected, got)

  def test_get_chunk(self):
    builder = gemma_prompt_builder.GemmaPromptBuilder()
    chunk = builder.get_chunk(
        "Test content", kind=gemma_prompt_builder.ChunkKind.CONTENT
    )
    self.assertEqual(chunk.content, "Test content")
    self.assertEqual(chunk.kind, gemma_prompt_builder.ChunkKind.CONTENT)

  def test_tool_role(self):
    builder = gemma_prompt_builder.GemmaPromptBuilder()
    self.assertEqual(builder.tool_role, builder.user_role)

  def test_get_state_mutable(self):
    builder = gemma_prompt_builder.GemmaPromptBuilder()
    builder.user_turn("Hello")
    builder.model_turn("Hi")
    builder.user_turn("f()", kind=gemma_prompt_builder.ChunkKind.TOOL_CALL)
    builder.user_turn("blabla", kind=gemma_prompt_builder.ChunkKind.TOOL_RESULT)
    self.assertLen(builder.get_state_mutable(), len(builder.get_state()))
    builder.get_state_mutable().pop()
    self.assertLen(builder.get_state_mutable(), len(builder.get_state()))


class GemmaTurnTest(absltest.TestCase):

  def test_gemma_turn(self):
    turn = gemma_prompt_builder.GemmaTurn(
        "user", [gemma_prompt_builder.GemmaChunk("Hello")]
    )
    self.assertEqual(str(turn), "<start_of_turn>user\nHello<end_of_turn>")

  def test_empty_turn(self):
    turn = gemma_prompt_builder.GemmaTurn(
        "user", [gemma_prompt_builder.GemmaChunk("")]
    )
    self.assertEqual(str(turn), "<start_of_turn>user\n<end_of_turn>")

  def test_set_role(self):
    turn = gemma_prompt_builder.GemmaTurn(
        "user", [gemma_prompt_builder.GemmaChunk("Hello")]
    )
    turn.role = "model"
    self.assertEqual(str(turn), "<start_of_turn>model\nHello<end_of_turn>")

  def test_set_content(self):
    turn = gemma_prompt_builder.GemmaTurn(
        "user", [gemma_prompt_builder.GemmaChunk("Hello")]
    )
    turn.content = [gemma_prompt_builder.GemmaChunk("Hi")]
    self.assertEqual(str(turn), "<start_of_turn>user\nHi<end_of_turn>")

  def test_inner_content(self):
    turn = gemma_prompt_builder.GemmaTurn(
        "user", [gemma_prompt_builder.GemmaChunk("Hello")]
    )
    turn.add_chunk(gemma_prompt_builder.GemmaChunk("Hi"))
    self.assertEqual(turn.inner_content, "Hello\nHi")

  def test_multiple_chunks(self):
    turn = gemma_prompt_builder.GemmaTurn(
        "user", [gemma_prompt_builder.GemmaChunk("Hello")]
    )
    turn.add_chunk(
        gemma_prompt_builder.GemmaChunk(
            "f()", kind=gemma_prompt_builder.ChunkKind.TOOL_CALL
        )
    )
    turn.add_chunk(
        gemma_prompt_builder.GemmaChunk(
            "blabla", kind=gemma_prompt_builder.ChunkKind.TOOL_RESULT
        )
    )
    self.assertEqual(
        str(turn),
        "<start_of_turn>user\nHello\n```tool_code\nf()\n```\n```tool_outputs\nblabla\n```<end_of_turn>",
    )


if __name__ == "__main__":
  googletest.main()
