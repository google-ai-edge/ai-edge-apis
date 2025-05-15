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

"""Class to label a function calling dataset.

This can be used for data generation and testing.
"""

from tool_simulation.core import base_prompt_builder
from tool_simulation.core import model_instance
from tool_simulation.stages.function_calling import datagen_prompt_builder as datagen_pb
from tool_simulation.stages.function_calling import replier_prompt_builder as replier_pb


def _fail_if_none_or_error(reply: str | None, error_token: str) -> str:
  if reply is None:
    raise ValueError("Failed to get reply")
  if error_token in reply:
    raise ValueError("Reply flagged as error")
  return reply


# TODO(b/405415695): Replace these with base class/protocols
def run_function_calling_episode(
    fc_prompt_builder: datagen_pb.DataGenerationPromptBuilder,
    replier_prompt_builder: replier_pb.ReplierPromptBuilder,
    function_calling_model: model_instance.ModelInstance,
    replier_model: model_instance.ModelInstance,
    max_steps: int = 1,
    stop_token: str = "STOP",
    error_token: str = "ERROR",
) -> base_prompt_builder.BasePromptBuilder:
  """Runs a function calling dataset.

  Notes:
    * This code assumes that the user query is already added to the prompt
    builder.
    * In case you are using a format that allows for both a tool call and a
      text reply in the same model turn, see the comment in
      `DataGenerationPromptBuilder.compute_function_reply` for more details.


  Args:
    fc_prompt_builder: PromptBuilder with the prompt to use
    replier_prompt_builder: ReplierPromptBuilder with the prompt to reply
    function_calling_model: model instance to query for function calling
    replier_model: model instance to query for replier
    max_steps: maximum number of steps to run the episode for
    stop_token: token to use to stop the episode. The code will search for this
      token in the replier reply and if found, will stop the episode.
    error_token: token to use to indicate an error. The code will search for
      this token in the replier reply and if found, will stop the episode.

  Returns:
    PromptBuilder with the function calling and replier turns

  Raises:
    ValueError: If the model fails to reply
  """

  step = 0
  while step < max_steps:
    step += 1
    # Get Function Call
    reply = _fail_if_none_or_error(
        function_calling_model.query_model(
            fc_prompt_builder.get_prompt_builder()
        ),
        error_token,
    )
    # Try processing function call
    compute_function_result = fc_prompt_builder.compute_function_reply(reply)
    # Check if the reply had a follow up
    if not compute_function_result.success:
      raise ValueError("Failed to compute function reply")
    if compute_function_result.forward:
      replier_prompt_builder.model_turn(compute_function_result.forward)
      replier_reply = _fail_if_none_or_error(
          replier_model.query_model(replier_prompt_builder),
          error_token,
      )
      replier_prompt_builder.user_turn(replier_reply)
      fc_prompt_builder.user_turn(replier_reply)
      # TODO(b/351703073): Make this explicit in the prompt builder
      if stop_token in replier_reply:
        break
  return fc_prompt_builder.get_prompt_builder()
