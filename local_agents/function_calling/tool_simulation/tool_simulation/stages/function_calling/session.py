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

"""Module defining the SyntheticSession interface."""

import abc
import dataclasses
import json
from typing import Any, Protocol

from tool_simulation.core import str2call


@dataclasses.dataclass
class FunctionReply:
  """Class representing a function reply."""

  # TODO(b/405415695): Fold raw_reply into reply type hint as
  # `dict[str, Any] | str`.
  reply: dict[str, Any] | None
  raw_reply: str | None = None

  def __str__(self):
    if self.raw_reply is not None:
      return self.raw_reply
    else:
      return json.dumps(self.reply)


class SyntheticSession(Protocol):
  """Class representing a session generating synthetic responses to API calls."""

  @abc.abstractmethod
  def reply(self, function_call: str2call.FunctionCall) -> FunctionReply:
    """Generates a synthetic response to a function call.

    This is a pure virtual method used by the data generation code to interface
    with the synthetic API backends.

    Args:
      function_call: A parsed function call object.

    Returns:
      A dict containing the function response.

    Raises:
      NotImplementedError if not implemented by derived class
    """
    raise NotImplementedError
