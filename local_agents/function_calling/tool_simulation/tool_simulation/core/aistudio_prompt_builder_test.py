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
from typing import cast

from absl.testing import absltest
from absl.testing import parameterized
from google.genai import types
from tool_simulation.core import aistudio_prompt_builder

ChunkKind = aistudio_prompt_builder.ChunkKind
AIStudioChunk = aistudio_prompt_builder.AIStudioChunk
AIStudioTurn = aistudio_prompt_builder.AIStudioTurn
AIStudioPromptBuilder = aistudio_prompt_builder.AIStudioPromptBuilder

TEXT_CONTENT = "Hello, AI Studio!"
TEXT_PART = types.Part(text=TEXT_CONTENT)

TOOL_CALL_NAME = "search_web"
TOOL_CALL_ARGS = {"query": "latest AI news"}
TOOL_CALL_DICT = {
    "name": TOOL_CALL_NAME,
    "args": TOOL_CALL_ARGS,
}
TOOL_CALL_STR = json.dumps(TOOL_CALL_DICT)
TOOL_CALL_PART = types.Part(
    function_call=types.FunctionCall(name=TOOL_CALL_NAME, args=TOOL_CALL_ARGS)
)

TOOL_RESPONSE_NAME = "search_web"
TOOL_RESPONSE_DATA = {"results": ["News A", "News B"]}
TOOL_RESPONSE_DICT = {
    "name": TOOL_RESPONSE_NAME,
    "response": TOOL_RESPONSE_DATA,
}
TOOL_RESPONSE_STR = json.dumps(TOOL_RESPONSE_DICT)
TOOL_RESPONSE_PART = types.Part(
    function_response=types.FunctionResponse(
        name=TOOL_RESPONSE_NAME,
        response=TOOL_RESPONSE_DATA,
    )
)


class AIStudioChunkTest(absltest.TestCase):

  def test_creation_content_chunk(self):
    chunk = AIStudioChunk(TEXT_PART, kind=ChunkKind.CONTENT)
    self.assertEqual(chunk.content, TEXT_PART)
    self.assertEqual(chunk.kind, ChunkKind.CONTENT)

  def test_creation_tool_call_chunk(self):
    chunk = AIStudioChunk(TOOL_CALL_PART, kind=ChunkKind.TOOL_CALL)
    self.assertEqual(chunk.content, TOOL_CALL_PART)
    self.assertEqual(chunk.kind, ChunkKind.TOOL_CALL)

  def test_creation_tool_result_chunk(self):
    chunk = AIStudioChunk(TOOL_RESPONSE_PART, kind=ChunkKind.TOOL_RESULT)
    self.assertEqual(chunk.content, TOOL_RESPONSE_PART)
    self.assertEqual(chunk.kind, ChunkKind.TOOL_RESULT)

  def test_to_dict(self):
    chunk = AIStudioChunk(TEXT_PART, kind=ChunkKind.CONTENT)
    self.assertEqual(chunk.to_dict(), TEXT_PART.to_json_dict())
    chunk_tc = AIStudioChunk(TOOL_CALL_PART, kind=ChunkKind.TOOL_CALL)
    self.assertEqual(chunk_tc.to_dict(), TOOL_CALL_PART.to_json_dict())
    chunk_tr = AIStudioChunk(TOOL_RESPONSE_PART, kind=ChunkKind.TOOL_RESULT)
    self.assertEqual(chunk_tr.to_dict(), TOOL_RESPONSE_PART.to_json_dict())

  def test_str(self):
    chunk = AIStudioChunk(TEXT_PART, kind=ChunkKind.CONTENT)
    self.assertEqual(str(chunk), json.dumps(TEXT_PART.to_json_dict()))
    chunk_tc = AIStudioChunk(TOOL_CALL_PART, kind=ChunkKind.TOOL_CALL)
    self.assertEqual(str(chunk_tc), json.dumps(TOOL_CALL_PART.to_json_dict()))
    chunk_tr = AIStudioChunk(TOOL_RESPONSE_PART, kind=ChunkKind.TOOL_RESULT)
    self.assertEqual(
        str(chunk_tr), json.dumps(TOOL_RESPONSE_PART.to_json_dict())
    )


class AIStudioTurnTest(absltest.TestCase):

  def test_creation_empty(self):
    turn = AIStudioTurn(role="user")
    self.assertEqual(turn.role, "user")
    self.assertEqual(turn.content, [])

  def test_creation_with_content(self):
    chunk1 = AIStudioChunk(TEXT_PART)
    turn = AIStudioTurn(role="model", content=[chunk1])
    self.assertEqual(turn.role, "model")
    self.assertEqual(turn.content, [chunk1])

  def test_content_property(self):
    turn = AIStudioTurn(role="user")
    chunk1 = AIStudioChunk(TEXT_PART)
    chunk2 = AIStudioChunk(TOOL_CALL_PART, kind=ChunkKind.TOOL_CALL)

    turn.content = [chunk1, chunk2]
    self.assertEqual(turn._content, [chunk1, chunk2])

  def test_add_chunk(self):
    turn = AIStudioTurn(role="model")
    chunk1 = AIStudioChunk(TEXT_PART)
    turn.add_chunk(chunk1)
    self.assertEqual(turn.content, [chunk1])

    chunk2 = AIStudioChunk(TOOL_CALL_PART, kind=ChunkKind.TOOL_CALL)
    turn.add_chunk(chunk2)
    self.assertEqual(turn.content, [chunk1, chunk2])

  def test_to_dict_single_text_chunk(self):
    chunk = AIStudioChunk(TEXT_PART)
    turn = AIStudioTurn(role="user", content=[chunk])
    expected_dict = types.Content(role="user", parts=[TEXT_PART]).to_json_dict()
    self.assertEqual(turn.to_dict(), expected_dict)

  def test_to_dict_multiple_chunks(self):
    chunk1 = AIStudioChunk(TEXT_PART)
    chunk2 = AIStudioChunk(TOOL_CALL_PART, kind=ChunkKind.TOOL_CALL)
    turn = AIStudioTurn(role="model", content=[chunk1, chunk2])
    expected_dict = types.Content(
        role="model", parts=[TEXT_PART, TOOL_CALL_PART]
    ).to_json_dict()
    self.assertEqual(turn.to_dict(), expected_dict)

  def test_str(self):
    chunk = AIStudioChunk(TEXT_PART)
    turn = AIStudioTurn(role="user", content=[chunk])
    self.assertEqual(str(turn), json.dumps(turn.to_dict()))

  def test_inner_content(self):
    chunk = AIStudioChunk(TEXT_PART)
    turn = AIStudioTurn(role="user", content=[chunk])
    self.assertEqual(turn.inner_content, str(turn))


class AIStudioPromptBuilderTest(parameterized.TestCase):

  def setUp(self):
    super().setUp()
    self.builder = AIStudioPromptBuilder()

  def test_initialization(self):
    self.assertIsInstance(self.builder, AIStudioPromptBuilder)
    self.assertEqual(self.builder._turn_class, AIStudioTurn)
    self.assertEqual(self.builder._chunk_class, AIStudioChunk)
    self.assertEqual(self.builder._state, [])
    self.assertIsNone(self.builder._current_turn)

  def test_role_properties(self):
    self.assertEqual(self.builder.user_role, "user")
    self.assertEqual(self.builder.model_role, "model")
    self.assertEqual(self.builder.tool_role, "user")

  @parameterized.named_parameters(
      ("str_content", TEXT_CONTENT, ChunkKind.CONTENT, TEXT_PART),
      ("str_tool_call", TOOL_CALL_STR, ChunkKind.TOOL_CALL, TOOL_CALL_PART),
      (
          "str_tool_result",
          TOOL_RESPONSE_STR,
          ChunkKind.TOOL_RESULT,
          TOOL_RESPONSE_PART,
      ),
      ("part_content", TEXT_PART, ChunkKind.CONTENT, TEXT_PART),
      ("part_tool_call", TOOL_CALL_PART, ChunkKind.TOOL_CALL, TOOL_CALL_PART),
      (
          "part_tool_result",
          TOOL_RESPONSE_PART,
          ChunkKind.TOOL_RESULT,
          TOOL_RESPONSE_PART,
      ),
  )
  def test_get_chunk_success(self, content_input, kind, expected_part_content):
    chunk = self.builder.get_chunk(content_input, kind)
    self.assertIsInstance(chunk, AIStudioChunk)
    self.assertEqual(chunk.kind, kind)
    self.assertEqual(
        chunk.content.to_json_dict(), expected_part_content.to_json_dict()
    )

  @parameterized.named_parameters(
      (
          "content_missing_text",
          types.Part(function_call=TOOL_CALL_PART.function_call),
          ChunkKind.CONTENT,
      ),
      (
          "tool_call_missing_fc",
          types.Part(text=TEXT_CONTENT),
          ChunkKind.TOOL_CALL,
      ),
      (
          "tool_result_missing_fr",
          types.Part(text=TEXT_CONTENT),
          ChunkKind.TOOL_RESULT,
      ),
      (
          "tool_call_invalid_json_str",
          "not_json",
          ChunkKind.TOOL_CALL,
      ),
      (
          "tool_call_missing_name_str",
          json.dumps({"args": {}}),
          ChunkKind.TOOL_CALL,
      ),
      (
          "tool_call_missing_args_str",
          json.dumps({"name": "n"}),
          ChunkKind.TOOL_CALL,
      ),
      (
          "tool_result_invalid_json_str",
          "not_json_either",
          ChunkKind.TOOL_RESULT,
      ),
      (
          "tool_result_missing_name_str",
          json.dumps({"response": {}}),
          ChunkKind.TOOL_RESULT,
      ),
      (
          "tool_result_missing_response_str",
          json.dumps({"name": "n"}),
          ChunkKind.TOOL_RESULT,
      ),
  )
  def test_get_chunk_invalid_part_type_for_kind(self, part_input, kind):
    with self.assertRaises(ValueError):
      self.builder.get_chunk(part_input, kind)

  def test_begin_user_turn(self):
    self.builder.begin_user_turn()
    self.assertIsNotNone(self.builder._current_turn)
    self.assertEqual(
        cast(AIStudioTurn, self.builder._current_turn).role, "user"
    )

  def test_begin_model_turn(self):
    self.builder.begin_model_turn()
    self.assertIsNotNone(self.builder._current_turn)
    self.assertEqual(
        cast(AIStudioTurn, self.builder._current_turn).role, "model"
    )

  def test_begin_tool_turn(self):
    self.builder.begin_tool_turn()
    self.assertIsNotNone(self.builder._current_turn)
    self.assertEqual(
        cast(AIStudioTurn, self.builder._current_turn).role, "user"
    )

  def test_add_content_success(self):
    self.builder.begin_user_turn()
    chunk = self.builder.get_chunk(TEXT_CONTENT)
    self.builder.add_content(chunk)
    self.assertIn(chunk, cast(AIStudioTurn, self.builder._current_turn).content)

  def test_add_content_no_turn_started_fails(self):
    chunk = self.builder.get_chunk(TEXT_CONTENT)
    with self.assertRaises(ValueError):
      self.builder.add_content(chunk)

  def test_end_turn_success(self):
    self.builder.begin_user_turn()
    self.builder.add_content(self.builder.get_chunk(TEXT_CONTENT))
    self.builder.end_turn()
    self.assertIsNone(self.builder._current_turn)
    self.assertLen(self.builder._state, 1)
    self.assertEqual(self.builder._state[0].role, "user")

  def test_end_turn_not_started_fails(self):
    with self.assertRaises(ValueError):
      self.builder.end_turn()

  def test_end_turn_empty_content_fails(self):
    self.builder.begin_user_turn()
    with self.assertRaises(ValueError):
      self.builder.end_turn()

  def test_user_turn_str(self):
    self.builder.user_turn(TEXT_CONTENT)
    self.assertLen(self.builder._state, 1)
    turn = self.builder._state[0]
    self.assertEqual(turn.role, "user")
    self.assertLen(turn.content, 1)
    self.assertEqual(turn.content[0].content.text, TEXT_CONTENT)
    self.assertEqual(turn.content[0].kind, ChunkKind.CONTENT)

  def test_user_turn_part(self):
    self.builder.user_turn(TEXT_PART)
    self.assertLen(self.builder._state, 1)
    turn = self.builder._state[0]
    self.assertEqual(turn.role, "user")
    self.assertLen(turn.content, 1)
    self.assertEqual(turn.content[0].content, TEXT_PART)

  def test_model_turn_str_tool_call(self):
    self.builder.model_turn(TOOL_CALL_STR, kind=ChunkKind.TOOL_CALL)
    self.assertLen(self.builder._state, 1)
    turn = self.builder._state[0]
    self.assertEqual(turn.role, "model")
    self.assertLen(turn.content, 1)
    self.assertEqual(
        turn.content[0].content.function_call, TOOL_CALL_PART.function_call
    )
    self.assertEqual(turn.content[0].kind, ChunkKind.TOOL_CALL)

  def test_model_turn_part(self):
    self.builder.model_turn(TOOL_CALL_PART, kind=ChunkKind.TOOL_CALL)
    self.assertLen(self.builder._state, 1)
    turn = self.builder._state[0]
    self.assertEqual(turn.role, "model")
    self.assertLen(turn.content, 1)
    self.assertEqual(turn.content[0].content, TOOL_CALL_PART)

  def test_tool_turn_str(self):
    self.builder.tool_turn(TOOL_RESPONSE_STR)
    self.assertLen(self.builder._state, 1)
    turn = self.builder._state[0]
    self.assertEqual(turn.role, "user")
    self.assertLen(turn.content, 1)
    self.assertEqual(
        turn.content[0].content.function_response,
        TOOL_RESPONSE_PART.function_response,
    )
    self.assertEqual(turn.content[0].kind, ChunkKind.TOOL_RESULT)

  def test_tool_turn_part_explicit_kind(self):
    self.builder.tool_turn(TOOL_RESPONSE_PART, kind=ChunkKind.TOOL_RESULT)
    self.assertLen(self.builder._state, 1)
    turn = self.builder._state[0]
    self.assertEqual(turn.role, "user")
    self.assertLen(turn.content, 1)
    self.assertEqual(turn.content[0].content, TOOL_RESPONSE_PART)
    self.assertEqual(turn.content[0].kind, ChunkKind.TOOL_RESULT)

  def test_get_state_returns_deepcopy(self):
    self.builder.user_turn(TEXT_CONTENT)
    state1 = self.builder.get_state()
    state2 = self.builder.get_state()
    self.assertIsNot(state1, state2)
    self.assertIsNot(state1[0], state2[0])
    state1[0].role = "changed"
    self.assertEqual(self.builder.get_state()[0].role, "user")

  def test_get_state_mutable_returns_actual_list(self):
    self.builder.user_turn(TEXT_CONTENT)
    mutable_state = self.builder.get_state_mutable()
    self.assertIs(mutable_state, self.builder._state)
    mutable_state.pop()
    self.assertEmpty(self.builder.get_state())

  @parameterized.named_parameters(
      ("get_state_in_turn", lambda b: b.get_state()),
      ("get_state_mutable_in_turn", lambda b: b.get_state_mutable()),
      ("get_prompt_in_turn", lambda b: b.get_prompt()),
  )
  def test_actions_in_middle_of_turn_fail(self, action_fn):
    self.builder.begin_user_turn()
    with self.assertRaises(ValueError):
      action_fn(self.builder)

  def test_get_prompt_empty(self):
    self.assertEqual(self.builder.get_prompt(), "[]")
    self.assertEqual(self.builder.get_prompt(inference=True), "[]")

  def test_get_prompt_single_turn(self):
    self.builder.user_turn(TEXT_CONTENT)
    expected_json_str = json.dumps(
        [types.Content(role="user", parts=[TEXT_PART]).to_json_dict()]
    )
    self.assertEqual(self.builder.get_prompt(), expected_json_str)

  def test_get_prompt_multi_turn_and_chunk(self):
    self.builder.user_turn(TEXT_CONTENT)
    self.builder.begin_model_turn()
    self.builder.add_content(self.builder.get_chunk("Response text"))
    self.builder.add_content(
        self.builder.get_chunk(TOOL_CALL_STR, kind=ChunkKind.TOOL_CALL)
    )
    self.builder.end_turn()
    self.builder.tool_turn(TOOL_RESPONSE_STR)

    expected_list = [
        types.Content(role="user", parts=[TEXT_PART]).to_json_dict(),
        types.Content(
            role="model",
            parts=[types.Part(text="Response text"), TOOL_CALL_PART],
        ).to_json_dict(),
        types.Content(role="user", parts=[TOOL_RESPONSE_PART]).to_json_dict(),
    ]
    self.assertEqual(self.builder.get_prompt(), json.dumps(expected_list))
    self.assertEqual(
        self.builder.get_prompt(inference=True), json.dumps(expected_list)
    )


if __name__ == "__main__":
  googletest.main()
