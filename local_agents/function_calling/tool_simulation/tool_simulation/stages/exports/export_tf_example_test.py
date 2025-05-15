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
import tensorflow as tf
from tool_simulation.core import base_prompt_builder
from tool_simulation.stages.exports import export_tf_example
from tool_simulation.stages.testing_utils import testing_commons


def _get_example(prompt: str, label: str) -> tf.train.Example:
  """Builds a tf.train.Example for test comparison."""
  example_dict = {}
  example_dict["inputs"] = tf.train.Feature(
      bytes_list=tf.train.BytesList(value=[prompt.encode()])
  )
  example_dict["targets"] = tf.train.Feature(
      bytes_list=tf.train.BytesList(value=[label.encode()])
  )
  return tf.train.Example(features=tf.train.Features(feature=example_dict))


class ExportTfExampleTest(absltest.TestCase):

  def test_empty_prompt_builder(self):
    test_prompt_builder = testing_commons.TestPromptBuilder()
    with self.assertRaises(ValueError):
      _ = export_tf_example.export_tf_example(test_prompt_builder)

  def test_only_user_turn(self):
    test_prompt_builder = testing_commons.TestPromptBuilder()
    test_prompt_builder.begin_turn(test_prompt_builder.user_role)
    test_prompt_builder.add_content(test_prompt_builder.get_chunk("Hello"))
    test_prompt_builder.end_turn()
    with self.assertRaises(ValueError):
      _ = export_tf_example.export_tf_example(test_prompt_builder)

  def test_only_nonmodel_turns(self):
    test_prompt_builder = testing_commons.TestPromptBuilder()
    test_prompt_builder.begin_turn(test_prompt_builder.user_role)
    test_prompt_builder.add_content(test_prompt_builder.get_chunk("Hello"))
    test_prompt_builder.end_turn()
    test_prompt_builder.begin_turn(test_prompt_builder.tool_role)
    test_prompt_builder.add_content(test_prompt_builder.get_chunk("Hello"))
    test_prompt_builder.end_turn()
    test_prompt_builder.begin_turn(test_prompt_builder.user_role)
    test_prompt_builder.add_content(test_prompt_builder.get_chunk("Hello"))
    test_prompt_builder.end_turn()
    test_prompt_builder.begin_turn(test_prompt_builder.tool_role)
    test_prompt_builder.add_content(test_prompt_builder.get_chunk("Hello"))
    test_prompt_builder.end_turn()
    self.assertEmpty(export_tf_example.export_tf_example(test_prompt_builder))

  def test_only_model_turn(self):
    test_prompt_builder = testing_commons.TestPromptBuilder()
    test_prompt_builder.begin_turn(test_prompt_builder.model_role)
    test_prompt_builder.add_content(
        test_prompt_builder.get_chunk("Model response")
    )
    test_prompt_builder.end_turn()
    with self.assertRaises(ValueError):
      _ = export_tf_example.export_tf_example(test_prompt_builder)

  def test_user_then_model_turn(self):
    test_prompt_builder = testing_commons.TestPromptBuilder()
    test_prompt_builder.begin_turn(test_prompt_builder.user_role)
    test_prompt_builder.add_content(test_prompt_builder.get_chunk("Hello"))
    test_prompt_builder.end_turn()
    test_prompt_builder.begin_turn(test_prompt_builder.model_role)
    test_prompt_builder.add_content(
        test_prompt_builder.get_chunk("Model response")
    )
    test_prompt_builder.end_turn()
    tf_examples = export_tf_example.export_tf_example(test_prompt_builder)

    test_prompt_builder.get_state_mutable().pop()

    expected_tf_examples = [
        _get_example(
            test_prompt_builder.get_prompt(inference=True),
            "<chunk_start>[content]Model response<chunk_end>",
        )
    ]

    self.assertLen(tf_examples, 1)
    self.assertEqual(tf_examples[0], expected_tf_examples[0])

  def test_only_model_turns(self):
    test_prompt_builder = testing_commons.TestPromptBuilder()
    test_prompt_builder.begin_turn(test_prompt_builder.model_role)
    test_prompt_builder.add_content(test_prompt_builder.get_chunk("Hello"))
    test_prompt_builder.end_turn()
    test_prompt_builder.begin_turn(test_prompt_builder.model_role)
    test_prompt_builder.add_content(test_prompt_builder.get_chunk("Hello"))
    test_prompt_builder.end_turn()
    test_prompt_builder.begin_turn(test_prompt_builder.model_role)
    test_prompt_builder.add_content(test_prompt_builder.get_chunk("Hello"))
    test_prompt_builder.end_turn()
    tf_examples = export_tf_example.export_tf_example(test_prompt_builder)

    test_prompt_builder.get_state_mutable().pop()
    expected_prompt_1 = test_prompt_builder.get_prompt(inference=True)
    test_prompt_builder.get_state_mutable().pop()
    expected_prompt_2 = test_prompt_builder.get_prompt(inference=True)
    test_prompt_builder.get_state_mutable().pop()
    expected_prompt_3 = test_prompt_builder.get_prompt(inference=True)

    expected_tf_examples = [
        _get_example(
            expected_prompt_1,
            "<chunk_start>[content]Hello<chunk_end>",
        ),
        _get_example(
            expected_prompt_2,
            "<chunk_start>[content]Hello<chunk_end>",
        ),
        _get_example(
            expected_prompt_3,
            "<chunk_start>[content]Hello<chunk_end>",
        ),
    ]

    self.assertLen(tf_examples, 3)
    self.assertEqual(tf_examples[0], expected_tf_examples[0])
    self.assertEqual(tf_examples[1], expected_tf_examples[1])
    self.assertEqual(tf_examples[2], expected_tf_examples[2])

  def test_user_tool_model_turn(self):
    test_prompt_builder = testing_commons.TestPromptBuilder()
    test_prompt_builder.begin_turn(test_prompt_builder.user_role)
    test_prompt_builder.add_content(test_prompt_builder.get_chunk("Hello"))
    test_prompt_builder.end_turn()
    test_prompt_builder.begin_turn(test_prompt_builder.tool_role)
    test_prompt_builder.add_content(test_prompt_builder.get_chunk("Hello"))
    test_prompt_builder.end_turn()
    test_prompt_builder.begin_turn(test_prompt_builder.model_role)
    test_prompt_builder.add_content(
        test_prompt_builder.get_chunk("Model response")
    )
    test_prompt_builder.end_turn()
    tf_examples = export_tf_example.export_tf_example(test_prompt_builder)

    test_prompt_builder.get_state_mutable().pop()
    expected_tf_examples = [
        _get_example(
            test_prompt_builder.get_prompt(inference=True),
            "<chunk_start>[content]Model response<chunk_end>",
        )
    ]

    self.assertLen(tf_examples, 1)
    self.assertEqual(tf_examples[0], expected_tf_examples[0])

  def test_e2e_conversation_multiple_examples(self):
    test_prompt_builder = testing_commons.TestPromptBuilder()
    test_prompt_builder.begin_turn(test_prompt_builder.user_role)
    test_prompt_builder.add_content(test_prompt_builder.get_chunk("Hello"))
    test_prompt_builder.end_turn()
    test_prompt_builder.begin_turn(test_prompt_builder.model_role)
    test_prompt_builder.add_content(test_prompt_builder.get_chunk("Answer 1"))
    test_prompt_builder.end_turn()
    test_prompt_builder.begin_turn(test_prompt_builder.user_role)
    test_prompt_builder.add_content(test_prompt_builder.get_chunk("Hello"))
    test_prompt_builder.end_turn()
    test_prompt_builder.begin_turn(test_prompt_builder.model_role)
    test_prompt_builder.add_content(test_prompt_builder.get_chunk("Answer 2"))
    test_prompt_builder.end_turn()
    tf_examples = export_tf_example.export_tf_example(test_prompt_builder)

    test_prompt_builder.get_state_mutable().pop()
    expected_prompt_1 = test_prompt_builder.get_prompt(inference=True)
    test_prompt_builder.get_state_mutable().pop()
    test_prompt_builder.get_state_mutable().pop()
    expected_prompt_2 = test_prompt_builder.get_prompt(inference=True)

    expected_tf_examples = [
        _get_example(
            expected_prompt_1,
            "<chunk_start>[content]Answer 2<chunk_end>",
        ),
        _get_example(
            expected_prompt_2,
            "<chunk_start>[content]Answer 1<chunk_end>",
        ),
    ]

    self.assertLen(tf_examples, 2)
    self.assertEqual(tf_examples[0], expected_tf_examples[0])
    self.assertEqual(tf_examples[1], expected_tf_examples[1])

  def test_conversation_with_tool_calls_and_results(self):
    test_prompt_builder = testing_commons.TestPromptBuilder()
    test_prompt_builder.begin_turn(test_prompt_builder.user_role)
    test_prompt_builder.add_content(
        test_prompt_builder.get_chunk("Use the calculator for 2+2")
    )
    test_prompt_builder.end_turn()
    test_prompt_builder.begin_turn(test_prompt_builder.model_role)
    test_prompt_builder.add_content(
        test_prompt_builder.get_chunk(
            "calculator(2, 2)", kind=base_prompt_builder.ChunkKind.TOOL_CALL
        )
    )
    test_prompt_builder.end_turn()
    test_prompt_builder.begin_turn(test_prompt_builder.tool_role)
    test_prompt_builder.add_content(
        test_prompt_builder.get_chunk(
            "{'result': 4}", kind=base_prompt_builder.ChunkKind.TOOL_RESULT
        )
    )
    test_prompt_builder.end_turn()
    test_prompt_builder.begin_turn(test_prompt_builder.model_role)
    test_prompt_builder.add_content(
        test_prompt_builder.get_chunk("The result is 4.")
    )
    test_prompt_builder.end_turn()
    tf_examples = export_tf_example.export_tf_example(test_prompt_builder)

    test_prompt_builder.get_state_mutable().pop()
    expected_prompt_1 = test_prompt_builder.get_prompt(inference=True)
    test_prompt_builder.get_state_mutable().pop()
    test_prompt_builder.get_state_mutable().pop()
    expected_prompt_2 = test_prompt_builder.get_prompt(inference=True)

    expected_tf_examples = [
        _get_example(
            expected_prompt_1,
            "<chunk_start>[content]The result is 4.<chunk_end>",
        ),
        _get_example(
            expected_prompt_2,
            "<chunk_start>[tool_call]calculator(2, 2)<chunk_end>",
        ),
    ]

    self.assertLen(tf_examples, 2)
    self.assertEqual(tf_examples[0], expected_tf_examples[0])
    self.assertEqual(tf_examples[1], expected_tf_examples[1])

  def test_multiple_roles_mixed(self):
    test_prompt_builder = testing_commons.TestPromptBuilder()
    test_prompt_builder.begin_turn("system")
    test_prompt_builder.add_content(
        test_prompt_builder.get_chunk("System Info")
    )
    test_prompt_builder.end_turn()
    test_prompt_builder.begin_turn(test_prompt_builder.user_role)
    test_prompt_builder.add_content(test_prompt_builder.get_chunk("User 1"))
    test_prompt_builder.end_turn()
    test_prompt_builder.begin_turn(test_prompt_builder.model_role)
    test_prompt_builder.add_content(test_prompt_builder.get_chunk("Model 1"))
    test_prompt_builder.end_turn()
    test_prompt_builder.begin_turn("dummy_role1")
    test_prompt_builder.add_content(test_prompt_builder.get_chunk("Dev Note"))
    test_prompt_builder.end_turn()
    test_prompt_builder.begin_turn("dummy_role2")
    test_prompt_builder.add_content(
        test_prompt_builder.get_chunk("Context Info")
    )
    test_prompt_builder.end_turn()
    test_prompt_builder.begin_turn(test_prompt_builder.user_role)
    test_prompt_builder.add_content(test_prompt_builder.get_chunk("User 2"))
    test_prompt_builder.end_turn()
    test_prompt_builder.begin_turn(test_prompt_builder.model_role)
    test_prompt_builder.add_content(test_prompt_builder.get_chunk("Model 2"))
    test_prompt_builder.end_turn()
    tf_examples = export_tf_example.export_tf_example(test_prompt_builder)

    test_prompt_builder.get_state_mutable().pop()
    expected_prompt_1 = test_prompt_builder.get_prompt(inference=True)
    test_prompt_builder.get_state_mutable().pop()
    test_prompt_builder.get_state_mutable().pop()
    test_prompt_builder.get_state_mutable().pop()
    test_prompt_builder.get_state_mutable().pop()
    expected_prompt_2 = test_prompt_builder.get_prompt(inference=True)
    expected_tf_examples = [
        _get_example(
            expected_prompt_1,
            "<chunk_start>[content]Model 2<chunk_end>",
        ),
        _get_example(
            expected_prompt_2,
            "<chunk_start>[content]Model 1<chunk_end>",
        ),
    ]

    self.assertLen(tf_examples, 2)
    self.assertEqual(tf_examples[0], expected_tf_examples[0])
    self.assertEqual(tf_examples[1], expected_tf_examples[1])


if __name__ == "__main__":
  googletest.main()
