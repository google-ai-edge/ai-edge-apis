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

"""AI Studio backend for function calling simulation."""

import json
from typing import Optional

from google import genai
from google.genai import types
from tool_simulation.core import aistudio_prompt_builder
from tool_simulation.core import base_prompt_builder


AIStudioTurn = aistudio_prompt_builder.AIStudioTurn
AIStudioPromptBuilder = aistudio_prompt_builder.AIStudioPromptBuilder


class AIStudioModel:
  """A wrapper class for the google.generativeai.GenerativeModel.

  Attributes:
    model_name: The name of the model to use.
    client: The google.generativeai.Client instance.
    config: The GenerateContentConfig instance.
    tools: The tools to use for the model.
  """

  def __init__(
      self,
      api_key: str,
      model_name: str = "gemini-pro",
      tools: Optional[types.Tool] = None,
  ):
    self.model_name = model_name
    self.client = genai.Client(api_key=api_key)
    self.config = types.GenerateContentConfig(tools=[tools] if tools else None)
    if tools:
      self.tools = tools

  def _turn_to_content(self, aistudio_turn: AIStudioTurn) -> types.Content:
    return types.Content(
        role=aistudio_turn.role,
        parts=[chunk.content for chunk in aistudio_turn.content],
    )

  # TODO(b/412697872): Support parallel function calling. Currently we take the
  # first function call in the response, which makes it possible to handle
  # parallel-style queries by unrolling into several inferences.
  def query_model(
      self, source_pb: base_prompt_builder.BasePromptBuilder | str
  ) -> Optional[str]:
    """Queries the gemini model with the given prompt or conversation history.

    Args:
      source_pb: The BasePromptBuilder instance containing the conversation
        history.

    Returns:
      The response from the model or None if there is an error.
      The response can be a string or a function call representation.
    """
    if isinstance(source_pb, aistudio_prompt_builder.AIStudioPromptBuilder):
      content = [self._turn_to_content(turn) for turn in source_pb.get_state()]
    elif isinstance(source_pb, base_prompt_builder.BasePromptBuilder):
      content = source_pb.get_prompt(inference=True)
    elif isinstance(source_pb, str):
      content = source_pb
    else:
      raise ValueError(f"Unsupported source type: {type(source_pb)}")

    try:
      response = self.client.models.generate_content(
          model=self.model_name,
          contents=content,
          config=self.config,
      )
    except Exception as e:  # pylint: disable=broad-exception-caught
      print(e)
      return None

    text_part = response.text
    function_calls = response.function_calls
    if not text_part and not function_calls:
      return None

    if text_part:
      return text_part
    if function_calls:
      return json.dumps(function_calls[0].to_json_dict())
