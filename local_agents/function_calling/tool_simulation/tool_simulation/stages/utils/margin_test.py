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
from tool_simulation.stages.utils import margin


class MarginTest(absltest.TestCase):

  def test_trim_margin(self):
    prompt = """
        |You are an agent.
        |You help the user.
        """
    expected_trimmed_prompt = "You are an agent.\nYou help the user."

    self.assertEqual(margin.trim_margin(prompt), expected_trimmed_prompt)

  def test_trim_margin_with_indentation(self):
    content = """
        |def f():
        |  print("Hello")
        """
    expected_trimmed_content = 'def f():\n  print("Hello")'

    self.assertEqual(margin.trim_margin(content), expected_trimmed_content)

  def test_trim_margin_with_embedded_content(self):
    content = """
        |You can call functions.
        |You can respond to the user.
        """
    trimmed_content = margin.trim_margin(content)
    prompt = f"""
        |You are an agent.
        |{trimmed_content}
        |You help the user.
        """

    expected_trimmed_prompt = (
        "You are an agent.\nYou can call functions.\nYou can respond to the"
        " user.\nYou help the user."
    )

    self.assertEqual(margin.trim_margin(prompt), expected_trimmed_prompt)

  def test_trim_margin_with_embedded_indented_content(self):
    content = """
        |def f():
        |  print("Hello")
        """
    trimmed_content = margin.trim_margin(content)
    prompt = f"""
        |You are an agent. You can call functions:
        |
        |```
        |{trimmed_content}
        |```
        |
        |You help the user.
        """
    print(prompt)

    expected_trimmed_prompt = (
        "You are an agent. You can call functions:\n\n```\ndef f():\n "
        ' print("Hello")\n```\n\nYou help the user.'
    )

    self.assertEqual(margin.trim_margin(prompt), expected_trimmed_prompt)

  def test_trim_margin_with_unwrapping(self):
    prompt = """
        |You are
        >an agent.
        |You help
        >the
        >user.
        """

    expected_trimmed_prompt = "You are an agent.\nYou help the user."

    self.assertEqual(margin.trim_margin(prompt), expected_trimmed_prompt)


if __name__ == "__main__":
  googletest.main()
