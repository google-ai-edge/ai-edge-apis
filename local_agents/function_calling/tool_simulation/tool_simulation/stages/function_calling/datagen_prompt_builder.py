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

"""Prompt builder for data generation."""

import dataclasses
from typing import Callable
import warnings

from tool_simulation.core import base_prompt_builder
from tool_simulation.core import str2call
from tool_simulation.stages.function_calling import session as session_lib


@dataclasses.dataclass
class ParseResult:
  function_call: str2call.FunctionCall | None
  forward: str | None


@dataclasses.dataclass
class ComputeFunctionResult:
  success: bool
  forward: str | None


class DataGenerationPromptBuilder:
  """Prompt builder for data generation."""

  def __init__(
      self,
      inner_prompt_builder: base_prompt_builder.BasePromptBuilder,
      session: session_lib.SyntheticSession,
      parse_fn: Callable[[str], ParseResult],
  ):
    self._prompt_builder = inner_prompt_builder
    self._session = session
    self._parse_fn = parse_fn

  def compute_function_reply(self, model_reply: str) -> ComputeFunctionResult:
    """Computes the function reply for a given model reply.

    This function combines a few steps:
    1. Parses the model reply (which could be a function call,
      text, or both) via a user-provided parse function and adds to the prompt
    2. Computes the function reply if a function call was found and adds to the
      prompt
    3. If the model segment had text, forwards the text to the caller, so it
      can be handled by the replier model.

    Args:
      model_reply: Model reply to process

    Returns:
      ComputeFunctionResult: A dataclass containing the success status and the
      forward text.
    """
    parse_result = self._parse_fn(model_reply)
    # If no legal function call or reply was found, return error
    if not parse_result.function_call and not parse_result.forward:
      return ComputeFunctionResult(success=False, forward=None)

    # TODO(b/412697872): Model formats dont cover mixing function
    # calls and forward text. If a model does not have tool role (e.g Gemma) it
    # is unclear if the replier/tool reply need to be bundled or be two turns.
    # If a model has a tool role (e.g Llama) it is unclear if the replier (user
    # turn) or tool turn should come first. We should define a lambda/enum and
    # allow users to define their own behavior. Since this is not blocking (the
    # data can be corrected easily) we emit a warning until we have a better
    # solution.
    if (
        parse_result.function_call is not None
        and parse_result.forward is not None
    ):
      warnings.warn(
          "Combined function call and forward text might lead to formatting"
          " inconsistencies. Please double-check your samples."
      )

    # At this point we either have a function call or forward text
    self._prompt_builder.begin_turn(self._prompt_builder.model_role)
    if parse_result.function_call:
      # Add the function call to the prompt
      self._prompt_builder.add_content(
          self._prompt_builder.get_chunk(
              str(parse_result.function_call),
              kind=base_prompt_builder.ChunkKind.TOOL_CALL,
          )
      )
    if parse_result.forward:
      self._prompt_builder.add_content(
          self._prompt_builder.get_chunk(
              parse_result.forward,
              kind=base_prompt_builder.ChunkKind.CONTENT,
          )
      )
    self._prompt_builder.end_turn()
    if parse_result.function_call:
      function_reply: session_lib.FunctionReply = self._session.reply(
          parse_result.function_call
      )
      self._prompt_builder.begin_turn(self._prompt_builder.tool_role)
      self._prompt_builder.add_content(
          self._prompt_builder.get_chunk(
              str(function_reply),
              kind=base_prompt_builder.ChunkKind.TOOL_RESULT,
          )
      )
      self._prompt_builder.end_turn()

    return ComputeFunctionResult(success=True, forward=parse_result.forward)

  def user_turn(
      self,
      text: str,
      kind: base_prompt_builder.ChunkKind = base_prompt_builder.ChunkKind.CONTENT,
  ) -> None:
    """Adds a user turn to the prompt."""
    self._prompt_builder.begin_turn(self._prompt_builder.user_role)
    self._prompt_builder.add_content(
        self._prompt_builder.get_chunk(
            text,
            kind=kind,
        )
    )
    self._prompt_builder.end_turn()

  def model_turn(
      self,
      text: str,
      kind: base_prompt_builder.ChunkKind = base_prompt_builder.ChunkKind.CONTENT,
  ) -> None:
    """Adds a model turn to the prompt."""
    self._prompt_builder.begin_turn(self._prompt_builder.model_role)
    self._prompt_builder.add_content(
        self._prompt_builder.get_chunk(
            text,
            kind=kind,
        )
    )
    self._prompt_builder.end_turn()

  def tool_turn(
      self,
      text: str,
      kind: base_prompt_builder.ChunkKind = base_prompt_builder.ChunkKind.TOOL_RESULT,
  ) -> None:
    """Adds a model turn to the prompt."""
    self._prompt_builder.begin_turn(self._prompt_builder.tool_role)
    self._prompt_builder.add_content(
        self._prompt_builder.get_chunk(
            text,
            kind=kind,
        )
    )
    self._prompt_builder.end_turn()

  def get_prompt(self, inference: bool = False) -> str:
    """Returns the current prompt."""
    return self._prompt_builder.get_prompt(inference=inference)

  def get_prompt_builder(self) -> base_prompt_builder.BasePromptBuilder:
    """Returns the underlying prompt builder."""
    return self._prompt_builder
