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

"""Exports a PromptBuilder state to Hugging Face chat format."""

from tool_simulation.core import base_prompt_builder

ChunkKind = base_prompt_builder.ChunkKind


def export_hf_chat(
    input_prompt_builder: base_prompt_builder.BasePromptBuilder,
) -> list[dict[str, str]]:
  """Exports a PromptBuilder state to Hugging Face chat format.

  Maps turns to a list of {"role": role, "content": content} dictionaries.
  - User turns with CONTENT chunks map to {"role": "user", "content": ...}.
  - User turns with TOOL_RESULT chunks (like in Gemma) map to {"role": "tool",
  "content": ...}.
  - Model turns with CONTENT or TOOL_CALL chunks map to {"role": "assistant",
  "content": ...}.
  - Tool turns (like in Llama) with TOOL_RESULT chunks map to {"role": "tool",
  "content": ...}.
  - System or other turn types are ignored.
  - Content from multiple relevant chunks is recorded as multiple list entries.

  Args:
    input_prompt_builder: The PromptBuilder instance containing the
      conversation.

  Returns:
    A list of dictionaries representing the conversation in Hugging Face format.

  Raises:
      ValueError: For a malformed input.
  """
  hf_user_role = 'user'
  hf_assistant_role = 'assistant'
  hf_tool_role = 'tool'
  chat_history = []
  for turn in input_prompt_builder.get_state():
    if turn.role == input_prompt_builder.user_role:
      for chunk in turn.content:
        if chunk.kind == ChunkKind.CONTENT:
          chat_history.append(
              {'role': hf_user_role, 'content': str(chunk.content)}
          )
        elif chunk.kind == ChunkKind.TOOL_RESULT:
          chat_history.append(
              {'role': hf_tool_role, 'content': str(chunk.content)}
          )
        elif chunk.kind == ChunkKind.TOOL_CALL:
          raise ValueError(
              'Tool calls should not appear in user turns. Found in turn:'
              f' {turn}'
          )
    elif turn.role == input_prompt_builder.model_role:
      for chunk in turn.content:
        chat_history.append({
            'role': hf_assistant_role,
            'content': str(chunk.content),
        })
    elif turn.role == input_prompt_builder.tool_role:
      for chunk in turn.content:
        chat_history.append(
            {'role': hf_tool_role, 'content': str(chunk.content)}
        )

  return chat_history
