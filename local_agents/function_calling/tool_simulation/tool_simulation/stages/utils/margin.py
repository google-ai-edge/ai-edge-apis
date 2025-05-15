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

"""Utilities for working with margin in text."""

import re


def trim_margin(text: str) -> str:
  """Trims the margin from the text.

  This function can be used to format multi-line strings, such as prompts.
  For lines starting with whitespace followed by a '|', the prefix is removed.
  For lines starting with whitespace followed by a '>', the prefix is removed
  and the line is joined with the previous line by a space.
  Other lines are left unchanged.
  Finally, leading and trailing whitespace is removed.

  Args:
    text: The text to trim.

  Returns:
    The trimmed text.
  """
  unwrapped_text = re.sub(r"\n\s*>", " ", text)
  return "\n".join(
      re.sub(r"^\s*\|", "", line) for line in unwrapped_text.split("\n")
  ).strip()
