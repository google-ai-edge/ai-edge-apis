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
from tool_simulation.core import llama_prompt_builder


class LlamaPromptBuilderTest(parameterized.TestCase):

  def test_user_turn(self):
    builder = llama_prompt_builder.LlamaPromptBuilder()
    builder.user_turn("Hello")
    self.assertEqual(
        builder.get_prompt(),
        "<|start_header_id|>user<|end_header_id|>Hello<|eot_id|>",
    )

  def test_model_turn(self):
    builder = llama_prompt_builder.LlamaPromptBuilder()
    builder.model_turn("Hello")
    self.assertEqual(
        builder.get_prompt(),
        "<|start_header_id|>assistant<|end_header_id|>Hello<|eot_id|>",
    )

  def test_model_turn_with_function_call(self):
    builder = llama_prompt_builder.LlamaPromptBuilder()
    builder.model_turn("f()", kind=llama_prompt_builder.ChunkKind.TOOL_CALL)
    self.assertEqual(
        builder.get_prompt(),
        "<|start_header_id|>assistant<|end_header_id|>[f()]<|eot_id|>",
    )

  def test_system_turn(self):
    builder = llama_prompt_builder.LlamaPromptBuilder()
    builder.system_turn("Hello")
    self.assertEqual(
        builder.get_prompt(),
        "<|start_header_id|>system<|end_header_id|>Hello<|eot_id|>",
    )

  def test_tool_turn(self):
    builder = llama_prompt_builder.LlamaPromptBuilder()
    builder.tool_turn("Hello")
    self.assertEqual(
        builder.get_prompt(),
        "<|start_header_id|>tool<|end_header_id|>Hello<|eot_id|>",
    )

  def test_user_turn_with_tool_result(self):
    builder = llama_prompt_builder.LlamaPromptBuilder()
    builder.user_turn("Hello", kind=llama_prompt_builder.ChunkKind.TOOL_RESULT)
    self.assertEqual(
        builder.get_prompt(),
        "<|start_header_id|>tool<|end_header_id|>Hello<|eot_id|>",
    )

  def test_multiple_turns(self):
    builder = llama_prompt_builder.LlamaPromptBuilder()
    builder.user_turn("Hello")
    builder.model_turn("Hi")
    builder.user_turn("f()", kind=llama_prompt_builder.ChunkKind.TOOL_CALL)
    builder.tool_turn("blabla")
    builder.user_turn("blabla", kind=llama_prompt_builder.ChunkKind.TOOL_RESULT)
    self.assertEqual(
        builder.get_prompt(),
        "<|start_header_id|>user<|end_header_id|>"
        + "Hello"
        + "<|eot_id|>"
        + "<|start_header_id|>assistant<|end_header_id|>"
        + "Hi"
        + "<|eot_id|><|start_header_id|>user<|end_header_id|>"
        + "[f()]"
        + "<|eot_id|><|start_header_id|>tool<|end_header_id|>"
        + "blabla"
        + "<|eot_id|>"
        + "<|start_header_id|>tool<|end_header_id|>"
        + "blabla"
        + "<|eot_id|>",
    )

  def test_empty_turns(self):
    builder = llama_prompt_builder.LlamaPromptBuilder()
    self.assertEqual(builder.get_prompt(), "")

  def test_get_prompt_for_inference(self):
    builder = llama_prompt_builder.LlamaPromptBuilder()
    builder.user_turn("Hello")
    self.assertEqual(
        builder.get_prompt(inference=True),
        "<|start_header_id|>user<|end_header_id|>Hello<|eot_id|><|start_header_id|>assistant<|end_header_id|>",
    )

  def test_append_turns(self):
    builder = llama_prompt_builder.LlamaPromptBuilder()
    builder.append_turns([
        llama_prompt_builder.LlamaTurn(
            "user", [llama_prompt_builder.LlamaChunk("Hello")]
        ),
        llama_prompt_builder.LlamaTurn(
            "assistant", [llama_prompt_builder.LlamaChunk("Hi")]
        ),
        llama_prompt_builder.LlamaTurn(
            "system", [llama_prompt_builder.LlamaChunk("Bye")]
        ),
    ])
    builder2 = llama_prompt_builder.LlamaPromptBuilder()
    builder2.user_turn("Hello")
    builder2.model_turn("Hi")
    builder2.system_turn("Bye")
    self.assertEqual(
        builder.get_prompt(),
        builder2.get_prompt(),
    )

    self.assertEqual(
        builder.get_prompt(inference=True),
        builder2.get_prompt(inference=True),
    )

  def test_begin_get_prompt(self):
    builder = llama_prompt_builder.LlamaPromptBuilder()
    builder.begin_user_turn()
    with self.assertRaises(ValueError):
      builder.get_prompt()
    with self.assertRaises(ValueError):
      builder.get_prompt(inference=True)

  def test_begin_content_get_prompt(self):
    builder = llama_prompt_builder.LlamaPromptBuilder()
    builder.begin_user_turn()
    builder.add_content(llama_prompt_builder.LlamaChunk("Hello"))
    with self.assertRaises(ValueError):
      builder.get_prompt()
    with self.assertRaises(ValueError):
      builder.get_prompt(inference=True)

  def test_begin_content_end_get_prompt(self):
    builder = llama_prompt_builder.LlamaPromptBuilder()
    builder.begin_user_turn()
    builder.add_content(llama_prompt_builder.LlamaChunk("Hello"))
    builder.end_turn()
    self.assertEqual(
        builder.get_prompt(),
        "<|start_header_id|>user<|end_header_id|>Hello<|eot_id|>",
    )

  def test_begin_end_get_prompt(self):
    builder = llama_prompt_builder.LlamaPromptBuilder()
    builder.begin_user_turn()
    builder.add_content(llama_prompt_builder.LlamaChunk("Hello"))
    builder.end_turn()
    self.assertEqual(
        builder.get_prompt(),
        "<|start_header_id|>user<|end_header_id|>Hello<|eot_id|>",
    )

  def test_double_begin_turn(self):
    builder = llama_prompt_builder.LlamaPromptBuilder()
    builder.begin_user_turn()
    with self.assertRaises(ValueError):
      builder.begin_user_turn()

  def test_double_begin_turn_after_content(self):
    builder = llama_prompt_builder.LlamaPromptBuilder()
    builder.begin_user_turn()
    builder.add_content(llama_prompt_builder.LlamaChunk("Hello"))
    with self.assertRaises(ValueError):
      builder.begin_user_turn()

  def test_double_end_turn(self):
    builder = llama_prompt_builder.LlamaPromptBuilder()
    builder.begin_user_turn()
    builder.add_content(llama_prompt_builder.LlamaChunk("Hello"))
    builder.end_turn()
    with self.assertRaises(ValueError):
      builder.end_turn()

  def test_end_turn_not_started(self):
    builder = llama_prompt_builder.LlamaPromptBuilder()
    with self.assertRaises(ValueError):
      builder.end_turn()

  def test_add_content_to_ended_turn(self):
    builder = llama_prompt_builder.LlamaPromptBuilder()
    builder.begin_user_turn()
    builder.add_content(llama_prompt_builder.LlamaChunk("Hello"))
    builder.end_turn()
    with self.assertRaises(ValueError):
      builder.add_content(llama_prompt_builder.LlamaChunk("Hello"))

  def test_add_content_empty(self):
    builder = llama_prompt_builder.LlamaPromptBuilder()
    with self.assertRaises(ValueError):
      builder.add_content(llama_prompt_builder.LlamaChunk("Hello"))

  def test_empty_turn_content(self):
    builder = llama_prompt_builder.LlamaPromptBuilder()
    builder.begin_user_turn()
    with self.assertRaises(ValueError):
      builder.end_turn()

  def test_get_state(self):
    instance = llama_prompt_builder.LlamaPromptBuilder()
    instance.user_turn("Hello")
    instance.model_turn("Hi")
    expected = list(
        map(
            str,
            [
                llama_prompt_builder.LlamaTurn(
                    "user", [llama_prompt_builder.LlamaChunk("Hello")]
                ),
                llama_prompt_builder.LlamaTurn(
                    "assistant", [llama_prompt_builder.LlamaChunk("Hi")]
                ),
            ],
        )
    )
    got = list(map(str, instance.get_state()))
    self.assertEqual(expected, got)

  def test_get_chunk(self):
    builder = llama_prompt_builder.LlamaPromptBuilder()
    chunk = builder.get_chunk(
        "Test content", kind=llama_prompt_builder.ChunkKind.CONTENT
    )
    self.assertEqual(chunk.content, "Test content")
    self.assertEqual(chunk.kind, llama_prompt_builder.ChunkKind.CONTENT)

  def test_tool_role(self):
    builder = llama_prompt_builder.LlamaPromptBuilder()
    self.assertEqual(builder.tool_role, builder._TOOL_ROLE)


class LlamaTurnTest(absltest.TestCase):

  def test_llama_turn(self):
    turn = llama_prompt_builder.LlamaTurn(
        "user", [llama_prompt_builder.LlamaChunk("Hello")]
    )
    self.assertEqual(
        str(turn), "<|start_header_id|>user<|end_header_id|>Hello<|eot_id|>"
    )

  def test_empty_turn(self):
    turn = llama_prompt_builder.LlamaTurn(
        "user", [llama_prompt_builder.LlamaChunk("")]
    )
    self.assertEqual(
        str(turn), "<|start_header_id|>user<|end_header_id|><|eot_id|>"
    )

  def test_set_role(self):
    turn = llama_prompt_builder.LlamaTurn(
        "user", [llama_prompt_builder.LlamaChunk("Hello")]
    )
    turn.role = "assistant"
    self.assertEqual(
        str(turn),
        "<|start_header_id|>assistant<|end_header_id|>Hello<|eot_id|>",
    )

  def test_set_content(self):
    turn = llama_prompt_builder.LlamaTurn(
        "user", [llama_prompt_builder.LlamaChunk("Hello")]
    )
    turn.content = [llama_prompt_builder.LlamaChunk("Hi")]
    self.assertEqual(
        str(turn), "<|start_header_id|>user<|end_header_id|>Hi<|eot_id|>"
    )

  def test_inner_content(self):
    turn = llama_prompt_builder.LlamaTurn(
        "user", [llama_prompt_builder.LlamaChunk("Hello")]
    )
    turn.add_chunk(llama_prompt_builder.LlamaChunk("Hi"))
    self.assertEqual(turn.inner_content, "Hello\nHi")

  def test_tool_call_format(self):
    turn = llama_prompt_builder.LlamaTurn(
        "assistant",
        [
            llama_prompt_builder.LlamaChunk(
                "f()", kind=llama_prompt_builder.ChunkKind.TOOL_CALL
            )
        ],
    )
    self.assertEqual(
        str(turn),
        "<|start_header_id|>assistant<|end_header_id|>[f()]<|eot_id|>",
    )

  def test_tool_result_format(self):
    turn = llama_prompt_builder.LlamaTurn(
        "tool",
        [
            llama_prompt_builder.LlamaChunk(
                "hi", kind=llama_prompt_builder.ChunkKind.TOOL_RESULT
            )
        ],
    )
    self.assertEqual(
        str(turn), "<|start_header_id|>tool<|end_header_id|>hi<|eot_id|>"
    )

  def test_get_state_mutable(self):
    builder = llama_prompt_builder.LlamaPromptBuilder()
    builder.user_turn("Hello")
    builder.model_turn("Hi")
    builder.user_turn("f()", kind=llama_prompt_builder.ChunkKind.TOOL_CALL)
    builder.tool_turn("blabla")
    builder.user_turn("blabla", kind=llama_prompt_builder.ChunkKind.TOOL_RESULT)
    self.assertLen(builder.get_state_mutable(), len(builder.get_state()))
    builder.get_state_mutable().pop()
    self.assertLen(builder.get_state_mutable(), len(builder.get_state()))


if __name__ == "__main__":
  googletest.main()
