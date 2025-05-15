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

"""Base pipeline for generating synthetic data."""

import copy
import dataclasses
from tool_simulation.core import base_prompt_builder
from tool_simulation.core import model_instance
from tool_simulation.stages.data_generation import seed_data
from tool_simulation.stages.function_calling import datagen_prompt_builder
from tool_simulation.stages.function_calling import function_calling_episode
from tool_simulation.stages.function_calling import replier_prompt_builder
from tool_simulation.stages.validation import validate_data
from tool_simulation.stages.validation import validation_prompt_builder


@dataclasses.dataclass
class BasePipelineConfig:
  """Base pipeline for generating synthetic data.

  Attributes:
    seed_data_prompt_builder: The prompt builder to use for generating seed
      data.
    seed_data_model: The model to use for generating seed data. This model
      should not format the input (format_input=False for the Evergreen
      backend).
    fc_replier_prompt_builder: The prompt builder to use for replier.
    fc_replier_model: The model to use for replier. This model should format the
      input (format_input=True for the Evergreen backend).
    fc_prompt_builder: The prompt builder to use for function calling. This
      should contain the system instruction and tool description.
    fc_model: The model to use for function calling. This model should not the
      input (format_input=False for the Evergreen backend).
    fc_max_steps: The maximum number of steps to run function calling episode
      for.
    validation_prompt_builder: The prompt builder to use for validation.
    validation_model: The model to use for validation. This model should format
      the input (format_input=True for the Evergreen backend).
  """

  seed_data_prompt_builder: base_prompt_builder.BasePromptBuilder
  seed_data_model: model_instance.ModelInstance
  fc_replier_prompt_builder: replier_prompt_builder.ReplierPromptBuilder
  fc_replier_model: model_instance.ModelInstance
  fc_prompt_builder: datagen_prompt_builder.DataGenerationPromptBuilder
  fc_model: model_instance.ModelInstance
  fc_max_steps: int
  validation_prompt_builder: validation_prompt_builder.ValidationPromptBuilder
  validation_model: model_instance.ModelInstance


def base_data_generation_pipeline(
    base_pipeline_config: BasePipelineConfig,
) -> list[base_prompt_builder.BasePromptBuilder]:
  """Base pipeline for generating synthetic data.

  The pipeline goes through the following steps:
  1. Generates seed data samples using the seed data prompt builder and model.
  2. Runs function calling episode for each seed data sample.
  3. Validates each function calling episode and returns the valid episodes as
     a list of prompt builder objects.

  Returns:
    A list of valid function calling episodes.

  Args:
    base_pipeline_config: The configuration for the pipeline.
  """
  generated_seed_queries = seed_data.generate_seed_data(
      base_pipeline_config.seed_data_prompt_builder,
      base_pipeline_config.seed_data_model,
  )
  print(len(generated_seed_queries))

  outputs = []
  for query in generated_seed_queries:
    fc_replier_pb = copy.deepcopy(
        base_pipeline_config.fc_replier_prompt_builder
    )
    fc_replier_pb.user_turn(query)
    fc_pb = copy.deepcopy(base_pipeline_config.fc_prompt_builder)
    fc_pb.user_turn(query)
    try:
      outputs.append(
          function_calling_episode.run_function_calling_episode(
              fc_prompt_builder=fc_pb,
              replier_prompt_builder=fc_replier_pb,
              function_calling_model=base_pipeline_config.fc_model,
              replier_model=base_pipeline_config.fc_replier_model,
              max_steps=base_pipeline_config.fc_max_steps,
          )
      )
      print(f"Done with query: {query}")
    except ValueError as e:
      print(f"[SKIPPED] {query} with error: {e}")

  print("Labeled: ", len(outputs))

  validated = []
  for output in outputs:
    validation_pb = copy.deepcopy(
        base_pipeline_config.validation_prompt_builder
    )
    validate_data.populate_validation_builder(
        validation_pb,
        output,
    )
    try:
      validation_result = validate_data.query_validation_model(
          validation_pb,
          base_pipeline_config.validation_model,
      )
      if validation_result:
        validated.append(output)
    except ValueError as e:
      print(f"[SKIPPED] {output} with error: {e}")

  print("Validated: ", len(validated))
  return validated
