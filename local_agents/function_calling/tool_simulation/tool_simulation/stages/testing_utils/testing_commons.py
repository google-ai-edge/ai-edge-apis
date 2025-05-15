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

"""Common testing utilities for function calling data generation."""

import dataclasses

from tool_simulation.core import base_prompt_builder
from tool_simulation.core import model_instance
from tool_simulation.core import str2call
from tool_simulation.core import testing_utils
from tool_simulation.stages.function_calling import datagen_prompt_builder
from tool_simulation.stages.function_calling import session as session_lib


TestPromptBuilder = testing_utils.TestPromptBuilder
TestChunk = testing_utils.TestChunk
TestTurn = testing_utils.TestTurn


class TestSession(session_lib.SyntheticSession):
  EXPECTED_REPLY: str = '{"status": "OK"}'

  def reply(
      self, function_call: str2call.FunctionCall
  ) -> session_lib.FunctionReply:
    return session_lib.FunctionReply(reply={"status": "OK"})


def test_parse_fn(
    reply: str,
) -> datagen_prompt_builder.ParseResult:
  """Helper function to test the parsing of function calls."""
  dummy_fc_object = str2call.parse_function_call_expression("dummy_function()")
  if reply == "ERROR":
    return datagen_prompt_builder.ParseResult(function_call=None, forward=None)
  elif reply == "FC_AND_FOLLOW_UP":
    return datagen_prompt_builder.ParseResult(
        function_call=dummy_fc_object, forward="Follow up"
    )
  elif reply == "FC_ONLY":
    return datagen_prompt_builder.ParseResult(
        function_call=dummy_fc_object, forward=None
    )
  elif reply == "FOLLOW_UP_ONLY":
    return datagen_prompt_builder.ParseResult(
        function_call=None, forward="Follow up"
    )
  else:
    raise ValueError(f"Unknown reply: {reply}")


@dataclasses.dataclass
class TestModelInstance(model_instance.ModelInstance):
  """Dummy model instance for testing."""

  replies: list[str | None] = dataclasses.field(default_factory=list)

  def query_model(
      self, prompt: str | base_prompt_builder.BasePromptBuilder
  ) -> str | None:
    if self.replies:
      reply = self.replies.pop(0)
      return reply
    if isinstance(prompt, TestPromptBuilder):
      return prompt.get_prompt(inference=True)
    elif isinstance(prompt, base_prompt_builder.BasePromptBuilder):
      raise ValueError(f"Unsupported prompt builder type: {type(prompt)}")
    return prompt
