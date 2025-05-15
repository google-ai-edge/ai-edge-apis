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

import warnings
from absl.testing import absltest
from absl.testing import parameterized
from tool_simulation.stages.function_calling import datagen_prompt_builder
from tool_simulation.stages.testing_utils import testing_commons


class DatagenPromptBuilderTest(parameterized.TestCase):

  @parameterized.named_parameters(
      (
          "compute_function_reply_error",
          "ERROR",
          datagen_prompt_builder.ComputeFunctionResult(
              success=False, forward=None
          ),
      ),
      (
          "compute_function_reply_fc_and_follow_up",
          "FC_AND_FOLLOW_UP",
          datagen_prompt_builder.ComputeFunctionResult(
              success=True, forward="Follow up"
          ),
      ),
      (
          "compute_function_reply_fc_only",
          "FC_ONLY",
          datagen_prompt_builder.ComputeFunctionResult(
              success=True, forward=None
          ),
      ),
      (
          "compute_function_reply_follow_up_only",
          "FOLLOW_UP_ONLY",
          datagen_prompt_builder.ComputeFunctionResult(
              success=True, forward="Follow up"
          ),
      ),
  )
  def test_compute_function_reply(self, reply, expected_result):
    prompt_builder = datagen_prompt_builder.DataGenerationPromptBuilder(
        testing_commons.TestPromptBuilder(),
        testing_commons.TestSession(),
        testing_commons.test_parse_fn,
    )
    warnings.filterwarnings(
        "ignore", ".*Combined function call and forward text.*"
    )
    self.assertEqual(
        prompt_builder.compute_function_reply(reply),
        expected_result,
    )

  def test_compute_function_reply_prompt_builder(self):
    prompt_builder = datagen_prompt_builder.DataGenerationPromptBuilder(
        testing_commons.TestPromptBuilder(),
        testing_commons.TestSession(),
        testing_commons.test_parse_fn,
    )
    prompt_builder.user_turn("Hello")
    self.assertEqual(
        prompt_builder.compute_function_reply("FC_ONLY"),
        datagen_prompt_builder.ComputeFunctionResult(
            success=True, forward=None
        ),
    )
    self.assertEqual(
        prompt_builder.get_prompt(),
        "<turn_start>user\n<chunk_start>[content]Hello<chunk_end><turn_end>"
        + "<turn_start>model\n<chunk_start>[tool_call]dummy_function()<chunk_end><turn_end>"
        + f"<turn_start>tool\n<chunk_start>[tool_result]{testing_commons.TestSession.EXPECTED_REPLY}<chunk_end><turn_end>",
    )

  def test_compute_function_reply_prompt_builder_error(self):
    prompt_builder = datagen_prompt_builder.DataGenerationPromptBuilder(
        testing_commons.TestPromptBuilder(),
        testing_commons.TestSession(),
        testing_commons.test_parse_fn,
    )
    prompt_builder.user_turn("Hello")
    prompt_builder.model_turn("Hello, pretend this is a function call")
    self.assertEqual(
        prompt_builder.compute_function_reply("ERROR"),
        datagen_prompt_builder.ComputeFunctionResult(
            success=False, forward=None
        ),
    )
    self.assertEqual(
        prompt_builder.get_prompt(),
        "<turn_start>user\n<chunk_start>[content]Hello<chunk_end><turn_end>"
        + "<turn_start>model\n<chunk_start>[content]Hello, pretend this is a"
        " function call<chunk_end><turn_end>",
    )


if __name__ == "__main__":
  googletest.main()
