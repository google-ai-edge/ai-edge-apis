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

"""Library to generate seed data samples."""

from typing import Callable

from tool_simulation.core import base_prompt_builder
from tool_simulation.core import model_instance


def generate_seed_data(
    seed_data_prompt_builder: base_prompt_builder.BasePromptBuilder,
    model: model_instance.ModelInstance,
    delimiter: str = "\n",
    filter_fn: Callable[[str], bool] = lambda x: x.strip(),
    post_process_fn: Callable[[str], str] = lambda x: x.strip(),
) -> list[str]:
  """Generates seed data samples using the provided prompt builder and model.

  Args:
    seed_data_prompt_builder: The prompt builder to use for generating seed
      data.
    model: The model to use for generating seed data.
    delimiter: The delimiter to use for splitting the seed data samples.
    filter_fn: The function to apply to each seed data sample after splitting to
      filter out empty samples.
    post_process_fn: The function to apply to each seed data sample after
      splitting and filtering.

  Returns:
    A list of seed data samples.
  """
  result = model.query_model(seed_data_prompt_builder)
  output = []
  if result:
    return list(
        map(post_process_fn, filter(filter_fn, result.split(delimiter)))
    )
  return output
