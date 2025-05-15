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

"""Functions for exporting prompt builder state to TF Example proto."""

import copy

import tensorflow as tf
from tool_simulation.core import base_prompt_builder


def _get_example(prompt: str, label: str) -> tf.train.Example:
  if not prompt or not label:
    raise ValueError("Malformed prompt or label.")
  example_dict = {}
  example_dict["inputs"] = tf.train.Feature(
      bytes_list=tf.train.BytesList(value=[prompt.encode()])
  )
  example_dict["targets"] = tf.train.Feature(
      bytes_list=tf.train.BytesList(value=[label.encode()])
  )
  return tf.train.Example(features=tf.train.Features(feature=example_dict))


def export_tf_example(
    input_prompt_builder: base_prompt_builder.BasePromptBuilder,
) -> list[tf.train.Example]:
  """Exports a PromptBuilder to a TF Example proto.

  This splits the conversation before every model turn. Then it exports a TF
  Example for each turn with the model turn as the label and the conversation
  up to that point as the input.

  Args:
    input_prompt_builder: The PromptBuilder to export.

  Returns:
    A list of TF Example protos from the conversation history.

  Raises:
    ValueError: If the example contains only a user turn or only a model turn.
  """
  tf_examples = []
  new_pb = copy.deepcopy(input_prompt_builder)
  states = new_pb.get_state_mutable()
  if len(states) < 2:
    raise ValueError("Malformed prompt builder state.")
  i = len(states) - 1
  while i >= 0:
    if states[i].role == input_prompt_builder.model_role:
      result = states[i].inner_content
      del states[i:]
      tf_examples.append(
          _get_example(new_pb.get_prompt(inference=True), result)
      )
    i -= 1

  return tf_examples
