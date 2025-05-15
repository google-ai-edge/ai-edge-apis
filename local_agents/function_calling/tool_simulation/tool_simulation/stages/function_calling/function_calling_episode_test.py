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
from tool_simulation.stages.function_calling import datagen_prompt_builder as datagen_pb
from tool_simulation.stages.function_calling import function_calling_episode
from tool_simulation.stages.function_calling import replier_prompt_builder as replier_pb
from tool_simulation.stages.testing_utils import testing_commons


class FunctionCallingEpisodeTest(absltest.TestCase):

  def test_basic_episode(self):
    warnings.filterwarnings(
        "ignore", ".*Combined function call and forward text.*"
    )
    datagen_prompt_builder = datagen_pb.DataGenerationPromptBuilder(
        testing_commons.TestPromptBuilder(),
        testing_commons.TestSession(),
        testing_commons.test_parse_fn,
    )
    datagen_prompt_builder.user_turn("dummy_query")
    replier_prompt_builder = replier_pb.ReplierPromptBuilder()
    function_calling_model = testing_commons.TestModelInstance(
        ["FC_AND_FOLLOW_UP"]
    )
    replier_model = testing_commons.TestModelInstance(["dummy_replier_reply"])
    result_pb = function_calling_episode.run_function_calling_episode(
        datagen_prompt_builder,
        replier_prompt_builder,
        function_calling_model,
        replier_model,
        max_steps=1,
    )
    self.assertEqual(
        result_pb.get_prompt(),
        "<turn_start>user\n<chunk_start>[content]dummy_query<chunk_end><turn_end>"
        + "<turn_start>model\n<chunk_start>[tool_call]dummy_function()<chunk_end>\n<chunk_start>[content]Follow"
        " up<chunk_end><turn_end>"
        + f"<turn_start>tool\n<chunk_start>[tool_result]{testing_commons.TestSession.EXPECTED_REPLY}<chunk_end><turn_end>"
        + "<turn_start>user\n<chunk_start>[content]dummy_replier_reply<chunk_end><turn_end>",
    )

  def test_episode_no_follow_up(self):
    datagen_prompt_builder = datagen_pb.DataGenerationPromptBuilder(
        testing_commons.TestPromptBuilder(),
        testing_commons.TestSession(),
        testing_commons.test_parse_fn,
    )
    datagen_prompt_builder.user_turn("dummy_query")
    replier_prompt_builder = replier_pb.ReplierPromptBuilder()
    function_calling_model = testing_commons.TestModelInstance(["FC_ONLY"])
    replier_model = testing_commons.TestModelInstance()
    result_pb = function_calling_episode.run_function_calling_episode(
        datagen_prompt_builder,
        replier_prompt_builder,
        function_calling_model,
        replier_model,
        max_steps=1,
    )
    self.assertEqual(
        result_pb.get_prompt(),
        "<turn_start>user\n<chunk_start>[content]dummy_query<chunk_end><turn_end>"
        + "<turn_start>model\n<chunk_start>[tool_call]dummy_function()<chunk_end><turn_end>"
        + f"<turn_start>tool\n<chunk_start>[tool_result]{testing_commons.TestSession.EXPECTED_REPLY}<chunk_end><turn_end>",
    )

  def test_episode_follow_up_only(self):
    datagen_prompt_builder = datagen_pb.DataGenerationPromptBuilder(
        testing_commons.TestPromptBuilder(),
        testing_commons.TestSession(),
        testing_commons.test_parse_fn,
    )
    datagen_prompt_builder.user_turn("dummy_query")
    replier_prompt_builder = replier_pb.ReplierPromptBuilder()
    function_calling_model = testing_commons.TestModelInstance(
        ["FOLLOW_UP_ONLY"]
    )
    replier_model = testing_commons.TestModelInstance(["dummy_replier_reply"])
    result_pb = function_calling_episode.run_function_calling_episode(
        datagen_prompt_builder,
        replier_prompt_builder,
        function_calling_model,
        replier_model,
        max_steps=1,
    )
    self.assertEqual(
        result_pb.get_prompt(),
        "<turn_start>user\n<chunk_start>[content]dummy_query<chunk_end><turn_end>"
        + "<turn_start>model\n<chunk_start>[content]Follow"
        " up<chunk_end><turn_end>"
        + "<turn_start>user\n<chunk_start>[content]dummy_replier_reply<chunk_end><turn_end>",
    )

  def test_episode_multiturn_stop(self):
    datagen_prompt_builder = datagen_pb.DataGenerationPromptBuilder(
        testing_commons.TestPromptBuilder(),
        testing_commons.TestSession(),
        testing_commons.test_parse_fn,
    )
    datagen_prompt_builder.user_turn("dummy_query")
    replier_prompt_builder = replier_pb.ReplierPromptBuilder()
    function_calling_model = testing_commons.TestModelInstance(
        ["FC_ONLY", "FOLLOW_UP_ONLY"]
    )
    replier_model = testing_commons.TestModelInstance(["STOP"])
    result_pb = function_calling_episode.run_function_calling_episode(
        datagen_prompt_builder,
        replier_prompt_builder,
        function_calling_model,
        replier_model,
        max_steps=100,  # Allow multiple turns
    )
    self.assertEqual(
        result_pb.get_prompt(),
        "<turn_start>user\n<chunk_start>[content]dummy_query<chunk_end><turn_end>"
        + "<turn_start>model\n<chunk_start>[tool_call]dummy_function()<chunk_end><turn_end>"
        + f"<turn_start>tool\n<chunk_start>[tool_result]{testing_commons.TestSession.EXPECTED_REPLY}<chunk_end><turn_end>"
        + "<turn_start>model\n<chunk_start>[content]Follow"
        " up<chunk_end><turn_end>"
        + "<turn_start>user\n<chunk_start>[content]STOP<chunk_end><turn_end>",
    )

  def test_episode_multiturn_userdefined_stop(self):
    datagen_prompt_builder = datagen_pb.DataGenerationPromptBuilder(
        testing_commons.TestPromptBuilder(),
        testing_commons.TestSession(),
        testing_commons.test_parse_fn,
    )
    datagen_prompt_builder.user_turn("dummy_query")
    replier_prompt_builder = replier_pb.ReplierPromptBuilder()
    function_calling_model = testing_commons.TestModelInstance(
        ["FC_ONLY", "FOLLOW_UP_ONLY"]
    )
    replier_model = testing_commons.TestModelInstance(["#STOP#"])
    result_pb = function_calling_episode.run_function_calling_episode(
        datagen_prompt_builder,
        replier_prompt_builder,
        function_calling_model,
        replier_model,
        max_steps=100,  # Allow multiple turns
        stop_token="#STOP#",
    )
    self.assertEqual(
        result_pb.get_prompt(),
        "<turn_start>user\n<chunk_start>[content]dummy_query<chunk_end><turn_end>"
        + "<turn_start>model\n<chunk_start>[tool_call]dummy_function()<chunk_end><turn_end>"
        + f"<turn_start>tool\n<chunk_start>[tool_result]{testing_commons.TestSession.EXPECTED_REPLY}<chunk_end><turn_end>"
        + "<turn_start>model\n<chunk_start>[content]Follow"
        " up<chunk_end><turn_end>"
        + "<turn_start>user\n<chunk_start>[content]#STOP#<chunk_end><turn_end>",
    )

  def test_episode_error_fcmodel(self):
    datagen_prompt_builder = datagen_pb.DataGenerationPromptBuilder(
        testing_commons.TestPromptBuilder(),
        testing_commons.TestSession(),
        testing_commons.test_parse_fn,
    )
    datagen_prompt_builder.user_turn("dummy_query")
    replier_prompt_builder = replier_pb.ReplierPromptBuilder()
    function_calling_model = testing_commons.TestModelInstance(["ERROR"])
    replier_model = testing_commons.TestModelInstance()
    with self.assertRaises(ValueError):
      _ = function_calling_episode.run_function_calling_episode(
          datagen_prompt_builder,
          replier_prompt_builder,
          function_calling_model,
          replier_model,
          max_steps=1,
      )

  def test_episode_error_user_defined(self):
    datagen_prompt_builder = datagen_pb.DataGenerationPromptBuilder(
        testing_commons.TestPromptBuilder(),
        testing_commons.TestSession(),
        testing_commons.test_parse_fn,
    )
    datagen_prompt_builder.user_turn("dummy_query")
    replier_prompt_builder = replier_pb.ReplierPromptBuilder()
    function_calling_model = testing_commons.TestModelInstance(["#ERROR#"])
    replier_model = testing_commons.TestModelInstance()
    with self.assertRaises(ValueError):
      _ = function_calling_episode.run_function_calling_episode(
          datagen_prompt_builder,
          replier_prompt_builder,
          function_calling_model,
          replier_model,
          max_steps=1,
          error_token="#ERROR#",
      )

  def test_episode_error_replier(self):
    warnings.filterwarnings(
        "ignore", ".*Combined function call and forward text.*"
    )
    datagen_prompt_builder = datagen_pb.DataGenerationPromptBuilder(
        testing_commons.TestPromptBuilder(),
        testing_commons.TestSession(),
        testing_commons.test_parse_fn,
    )
    datagen_prompt_builder.user_turn("dummy_query")
    replier_prompt_builder = replier_pb.ReplierPromptBuilder()
    function_calling_model = testing_commons.TestModelInstance(
        ["FC_AND_FOLLOW_UP"]
    )
    replier_model = testing_commons.TestModelInstance(["ERROR"])
    with self.assertRaises(ValueError):
      _ = function_calling_episode.run_function_calling_episode(
          datagen_prompt_builder,
          replier_prompt_builder,
          function_calling_model,
          replier_model,
          max_steps=1,
      )

  def test_episode_fcmodel_error(self):
    datagen_prompt_builder = datagen_pb.DataGenerationPromptBuilder(
        testing_commons.TestPromptBuilder(),
        testing_commons.TestSession(),
        testing_commons.test_parse_fn,
    )
    datagen_prompt_builder.user_turn("dummy_query")
    replier_prompt_builder = replier_pb.ReplierPromptBuilder()
    function_calling_model = testing_commons.TestModelInstance([None])
    replier_model = testing_commons.TestModelInstance()
    with self.assertRaises(ValueError):
      _ = function_calling_episode.run_function_calling_episode(
          datagen_prompt_builder,
          replier_prompt_builder,
          function_calling_model,
          replier_model,
          max_steps=1,
      )

  def test_episode_replier_error(self):
    warnings.filterwarnings(
        "ignore", ".*Combined function call and forward text.*"
    )
    datagen_prompt_builder = datagen_pb.DataGenerationPromptBuilder(
        testing_commons.TestPromptBuilder(),
        testing_commons.TestSession(),
        testing_commons.test_parse_fn,
    )
    datagen_prompt_builder.user_turn("dummy_query")
    replier_prompt_builder = replier_pb.ReplierPromptBuilder()
    function_calling_model = testing_commons.TestModelInstance(
        ["FC_AND_FOLLOW_UP"]
    )
    replier_model = testing_commons.TestModelInstance([None])
    with self.assertRaises(ValueError):
      _ = function_calling_episode.run_function_calling_episode(
          datagen_prompt_builder,
          replier_prompt_builder,
          function_calling_model,
          replier_model,
          max_steps=1,
      )


if __name__ == "__main__":
  googletest.main()
