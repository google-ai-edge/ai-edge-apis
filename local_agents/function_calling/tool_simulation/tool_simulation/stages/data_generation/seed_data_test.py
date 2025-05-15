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

from absl.testing import absltest
from tool_simulation.core import testing_utils
from tool_simulation.stages.data_generation import seed_data
from tool_simulation.stages.testing_utils import testing_commons


class SeedDataTest(absltest.TestCase):

  def test_generates_seed_data(self):
    model = testing_commons.TestModelInstance(["A\n B\nC \n   "])
    seed_data_pb = testing_utils.TestPromptBuilder()
    seed_data_pb.begin_turn(seed_data_pb.user_role)
    seed_data_pb.add_content(seed_data_pb.get_chunk("Hello"))
    seed_data_pb.end_turn()
    self.assertEqual(
        seed_data.generate_seed_data(seed_data_pb, model), ["A", "B", "C"]
    )

  def test_generates_seed_data_delimeter(self):
    model = testing_commons.TestModelInstance(["A<END>B<END>C<END>"])
    seed_data_pb = testing_utils.TestPromptBuilder()
    seed_data_pb.begin_turn(seed_data_pb.user_role)
    seed_data_pb.add_content(seed_data_pb.get_chunk("Hello"))
    seed_data_pb.end_turn()
    self.assertEqual(
        seed_data.generate_seed_data(seed_data_pb, model, delimiter="<END>"),
        ["A", "B", "C"],
    )

  def test_generates_seed_data_delimeter_and_post_process_fn(self):
    model = testing_commons.TestModelInstance(["A.<END>B.<END>C.<END>"])
    seed_data_pb = testing_utils.TestPromptBuilder()
    seed_data_pb.begin_turn(seed_data_pb.user_role)
    seed_data_pb.add_content(seed_data_pb.get_chunk("Hello"))
    seed_data_pb.end_turn()
    self.assertEqual(
        seed_data.generate_seed_data(
            seed_data_pb,
            model,
            delimiter="<END>",
            post_process_fn=lambda x: x.strip("."),
        ),
        ["A", "B", "C"],
    )

  def test_generates_seed_data_delimeter_and_post_process_fn_filter_fn(self):
    model = testing_commons.TestModelInstance(["A.<END>B.<END>C.<END>"])
    seed_data_pb = testing_utils.TestPromptBuilder()
    seed_data_pb.begin_turn(seed_data_pb.user_role)
    seed_data_pb.add_content(seed_data_pb.get_chunk("Hello"))
    seed_data_pb.end_turn()
    self.assertEqual(
        seed_data.generate_seed_data(
            seed_data_pb,
            model,
            delimiter="<END>",
            post_process_fn=lambda x: x.strip("."),
            filter_fn=lambda x: x.strip() and "B" not in x,
        ),
        ["A", "C"],
    )


if __name__ == "__main__":
  googletest.main()
