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

import json

from absl.testing import absltest
from tool_simulation.core import base_prompt_builder
from tool_simulation.stages.exports import export_hf_chat
from tool_simulation.stages.testing_utils import testing_commons


ChunkKind = base_prompt_builder.ChunkKind


class ExportHuggingfaceChatTest(absltest.TestCase):

  def test_empty_prompt_builder(self):
    test_prompt_builder = testing_commons.TestPromptBuilder()
    hf_chat = export_hf_chat.export_hf_chat(test_prompt_builder)
    self.assertEmpty(hf_chat)

  def test_single_user_turn_content(self):
    test_prompt_builder = testing_commons.TestPromptBuilder()
    test_prompt_builder.begin_turn(test_prompt_builder.user_role)
    test_prompt_builder.add_content(test_prompt_builder.get_chunk('Hello'))
    test_prompt_builder.end_turn()
    hf_chat = export_hf_chat.export_hf_chat(test_prompt_builder)
    expected = [{'role': 'user', 'content': 'Hello'}]
    self.assertEqual(hf_chat, expected)

  def test_single_model_turn_content(self):
    test_prompt_builder = testing_commons.TestPromptBuilder()
    test_prompt_builder.begin_turn(test_prompt_builder.model_role)
    test_prompt_builder.add_content(test_prompt_builder.get_chunk('Hi there!'))
    test_prompt_builder.end_turn()
    hf_chat = export_hf_chat.export_hf_chat(test_prompt_builder)
    expected = [{'role': 'assistant', 'content': 'Hi there!'}]
    self.assertEqual(hf_chat, expected)

  def test_single_tool_turn_result(self):
    test_prompt_builder = testing_commons.TestPromptBuilder()
    tool_result_content = json.dumps({'result': 4})
    test_prompt_builder.begin_turn(test_prompt_builder.tool_role)
    test_prompt_builder.add_content(
        test_prompt_builder.get_chunk(
            tool_result_content, kind=ChunkKind.TOOL_RESULT
        )
    )
    test_prompt_builder.end_turn()
    hf_chat = export_hf_chat.export_hf_chat(test_prompt_builder)
    expected = [{'role': 'tool', 'content': tool_result_content}]
    self.assertEqual(hf_chat, expected)

  def test_user_then_model_turn(self):
    test_prompt_builder = testing_commons.TestPromptBuilder()
    test_prompt_builder.begin_turn(test_prompt_builder.user_role)
    test_prompt_builder.add_content(test_prompt_builder.get_chunk('Hello'))
    test_prompt_builder.end_turn()
    test_prompt_builder.begin_turn(test_prompt_builder.model_role)
    test_prompt_builder.add_content(test_prompt_builder.get_chunk('Hi there!'))
    test_prompt_builder.end_turn()
    hf_chat = export_hf_chat.export_hf_chat(test_prompt_builder)
    expected = [
        {'role': 'user', 'content': 'Hello'},
        {'role': 'assistant', 'content': 'Hi there!'},
    ]
    self.assertEqual(hf_chat, expected)

  def test_tool_result_in_tool_role(self):
    test_prompt_builder = testing_commons.TestPromptBuilder()
    tool_call_content = 'calculator(a=2, b=2)'
    tool_result_content = json.dumps({'result': 4})

    test_prompt_builder.begin_turn(test_prompt_builder.user_role)
    test_prompt_builder.add_content(
        test_prompt_builder.get_chunk('Calculate 2+2')
    )
    test_prompt_builder.end_turn()
    test_prompt_builder.begin_turn(test_prompt_builder.model_role)
    test_prompt_builder.add_content(
        test_prompt_builder.get_chunk(
            tool_call_content, kind=ChunkKind.TOOL_CALL
        )
    )
    test_prompt_builder.end_turn()
    test_prompt_builder.begin_turn(test_prompt_builder.tool_role)
    test_prompt_builder.add_content(
        test_prompt_builder.get_chunk(
            tool_result_content, kind=ChunkKind.TOOL_RESULT
        )
    )
    test_prompt_builder.end_turn()
    test_prompt_builder.begin_turn(test_prompt_builder.model_role)
    test_prompt_builder.add_content(
        test_prompt_builder.get_chunk('The result is 4.')
    )
    test_prompt_builder.end_turn()

    hf_chat = export_hf_chat.export_hf_chat(test_prompt_builder)
    expected = [
        {'role': 'user', 'content': 'Calculate 2+2'},
        {'role': 'assistant', 'content': tool_call_content},
        {'role': 'tool', 'content': tool_result_content},
        {'role': 'assistant', 'content': 'The result is 4.'},
    ]
    self.assertEqual(hf_chat, expected)

  def test_tool_result_in_user_role(self):
    test_prompt_builder = testing_commons.TestPromptBuilder()
    tool_call_content = 'calculator(a=3, b=5)'
    tool_result_content = json.dumps({'result': 8})

    test_prompt_builder.begin_turn(test_prompt_builder.user_role)
    test_prompt_builder.add_content(
        test_prompt_builder.get_chunk('Calculate 3+5')
    )
    test_prompt_builder.end_turn()
    test_prompt_builder.begin_turn(test_prompt_builder.model_role)
    test_prompt_builder.add_content(
        test_prompt_builder.get_chunk(
            tool_call_content, kind=ChunkKind.TOOL_CALL
        )
    )
    test_prompt_builder.end_turn()
    test_prompt_builder.begin_turn(test_prompt_builder.user_role)
    test_prompt_builder.add_content(
        test_prompt_builder.get_chunk(
            tool_result_content, kind=ChunkKind.TOOL_RESULT
        )
    )
    test_prompt_builder.end_turn()
    test_prompt_builder.begin_turn(test_prompt_builder.model_role)
    test_prompt_builder.add_content(
        test_prompt_builder.get_chunk('The sum is 8.')
    )
    test_prompt_builder.end_turn()

    hf_chat = export_hf_chat.export_hf_chat(test_prompt_builder)
    expected = [
        {'role': 'user', 'content': 'Calculate 3+5'},
        {'role': 'assistant', 'content': tool_call_content},
        {'role': 'tool', 'content': tool_result_content},
        {'role': 'assistant', 'content': 'The sum is 8.'},
    ]
    self.assertEqual(hf_chat, expected)

  def test_ignore_system_turn(self):
    test_prompt_builder = testing_commons.TestPromptBuilder()
    test_prompt_builder.begin_turn('system')
    test_prompt_builder.add_content(
        test_prompt_builder.get_chunk('System instructions')
    )
    test_prompt_builder.end_turn()
    test_prompt_builder.begin_turn(test_prompt_builder.user_role)
    test_prompt_builder.add_content(test_prompt_builder.get_chunk('User query'))
    test_prompt_builder.end_turn()
    test_prompt_builder.begin_turn(test_prompt_builder.model_role)
    test_prompt_builder.add_content(
        test_prompt_builder.get_chunk('Model answer')
    )
    test_prompt_builder.end_turn()

    hf_chat = export_hf_chat.export_hf_chat(test_prompt_builder)
    expected = [
        {'role': 'user', 'content': 'User query'},
        {'role': 'assistant', 'content': 'Model answer'},
    ]
    self.assertEqual(hf_chat, expected)

  def test_multiple_chunks_in_turns(self):
    test_prompt_builder = testing_commons.TestPromptBuilder()
    tool_call_content = 'some_tool(arg=1)'
    tool_result_content = json.dumps({'status': 'ok'})

    test_prompt_builder.begin_turn(test_prompt_builder.user_role)
    test_prompt_builder.add_content(test_prompt_builder.get_chunk('Part 1.'))
    test_prompt_builder.add_content(test_prompt_builder.get_chunk('Part 2?'))
    test_prompt_builder.end_turn()

    test_prompt_builder.begin_turn(test_prompt_builder.model_role)
    test_prompt_builder.add_content(
        test_prompt_builder.get_chunk('Okay, processing...')
    )
    test_prompt_builder.add_content(
        test_prompt_builder.get_chunk(
            tool_call_content, kind=ChunkKind.TOOL_CALL
        )
    )
    test_prompt_builder.end_turn()

    test_prompt_builder.begin_turn(test_prompt_builder.tool_role)
    test_prompt_builder.add_content(
        test_prompt_builder.get_chunk(
            tool_result_content, kind=ChunkKind.TOOL_RESULT
        )
    )
    test_prompt_builder.end_turn()

    hf_chat = export_hf_chat.export_hf_chat(test_prompt_builder)
    expected = [
        {'role': 'user', 'content': 'Part 1.'},
        {'role': 'user', 'content': 'Part 2?'},
        {'role': 'assistant', 'content': 'Okay, processing...'},
        {'role': 'assistant', 'content': tool_call_content},
        {'role': 'tool', 'content': tool_result_content},
    ]
    self.assertEqual(hf_chat, expected)

  def test_user_turn_with_tool_call_raises_error(self):
    test_prompt_builder = testing_commons.TestPromptBuilder()
    test_prompt_builder.begin_turn(test_prompt_builder.user_role)
    test_prompt_builder.add_content(test_prompt_builder.get_chunk('User text'))
    test_prompt_builder.add_content(
        test_prompt_builder.get_chunk('tool_call()', kind=ChunkKind.TOOL_CALL)
    )
    test_prompt_builder.end_turn()

    with self.assertRaisesRegex(
        ValueError, 'Tool calls should not appear in user turns'
    ):
      _ = export_hf_chat.export_hf_chat(test_prompt_builder)

  def test_user_turn_with_content_and_tool_result(self):
    test_prompt_builder = testing_commons.TestPromptBuilder()
    test_prompt_builder.begin_turn(test_prompt_builder.user_role)
    test_prompt_builder.add_content(test_prompt_builder.get_chunk('User text'))
    test_prompt_builder.add_content(
        test_prompt_builder.get_chunk('tool_result', kind=ChunkKind.TOOL_RESULT)
    )
    test_prompt_builder.end_turn()
    hf_chat = export_hf_chat.export_hf_chat(test_prompt_builder)
    expected = [
        {'role': 'user', 'content': 'User text'},
        {'role': 'tool', 'content': 'tool_result'},
    ]
    self.assertEqual(hf_chat, expected)


if __name__ == '__main__':
  googletest.main()
