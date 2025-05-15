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

"""Library for validating conversations."""

from tool_simulation.core import base_prompt_builder
from tool_simulation.core import model_instance
from tool_simulation.stages.validation import validation_prompt_builder


# TODO(b/405415695): Make this collate turns when we repeating ones.
def populate_validation_builder(
    validation_builder: validation_prompt_builder.ValidationPromptBuilder,
    input_builder: base_prompt_builder.BasePromptBuilder,
) -> validation_prompt_builder.ValidationPromptBuilder:
  """Populates the validation builder with the state of another prompt builder.

  Args:
    validation_builder: The validation builder to populate.
    input_builder: The input builder to populate the validation builder from.

  Returns:
    The populated validation builder.
  """
  for turn in input_builder.get_state():
    if turn.role == input_builder.user_role:
      for chunk in turn.content:
        # Some formats have the tool reply under the user role while others
        # have a special turn role. This code handles both cases by doing all
        # checks and doign the mapping on the chunk kind level.
        if chunk.kind == base_prompt_builder.ChunkKind.TOOL_RESULT:
          validation_builder.tool_turn(str(chunk.content))
        elif chunk.kind == base_prompt_builder.ChunkKind.CONTENT:
          validation_builder.user_turn(str(chunk.content))
        else:
          raise ValueError(f"Unknown chunk kind for user turn: {chunk.kind}")
    elif turn.role == input_builder.model_role:
      for chunk in turn.content:
        if (
            chunk.kind == base_prompt_builder.ChunkKind.TOOL_CALL
            or chunk.kind == base_prompt_builder.ChunkKind.CONTENT
        ):
          validation_builder.assistant_turn(str(chunk.content), kind=chunk.kind)
        else:
          raise ValueError(f"Unknown chunk kind for model turn: {chunk.kind}")
    elif turn.role == input_builder.tool_role:
      for chunk in turn.content:
        if chunk.kind == base_prompt_builder.ChunkKind.TOOL_RESULT:
          validation_builder.tool_turn(str(chunk.content))
        else:
          raise ValueError(f"Unknown chunk kind for tool turn: {chunk.kind}")
  return validation_builder


def query_validation_model(
    sample_validation_prompt_builder: validation_prompt_builder.ValidationPromptBuilder,
    model: model_instance.ModelInstance,
) -> bool:
  """Queries the validation model with the provided validation prompt builder.

  Note: This requires the model to return YES or NO only.

  Args:
    sample_validation_prompt_builder: The validation prompt builder to use.
    model: The model to use for querying.

  Returns:
    True if the validation result is YES, False if the validation result is NO,
    and raises a ValueError if the validation result is not YES or NO.
  """
  result = model.query_model(sample_validation_prompt_builder)
  if result is not None and "YES" in result:
    return True
  elif result is not None and "NO" in result:
    return False
  else:
    raise ValueError(f"Unknown validation result: {result}")
