// Copyright 2025 The Google AI Edge Authors.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

#ifndef THIRD_PARTY_ODML_GENAI_MODULES_FUNCTION_CALLING_CORE_HAMMER_FORMATTER_H_
#define THIRD_PARTY_ODML_GENAI_MODULES_FUNCTION_CALLING_CORE_HAMMER_FORMATTER_H_

#include <string>

#include "absl/status/statusor.h"      // from @abseil-cpp
#include "absl/strings/string_view.h"  // from @abseil-cpp
#include "absl/types/span.h"           // from @abseil-cpp
#include "local_agents/core/proto/content.pb.h"
#include "local_agents/core/proto/generative_service.pb.h"
#include "local_agents/function_calling/core/proto/model_formatter_options.pb.h"

namespace odml::generativeai {

// Formats the system message and tools into a string. This function combines
// the provided system instruction and tool definitions according to the
// specified formatting options, creating a string that can be used as the
// initial part of the prompt for the Hammer model.
//
// Parameters:
//  `system_instruction`
//    The content containing the system-level instructions for the model.
//  `tools`
//    A span of pointers to the Tool protos defining the available functions the
//    model can call. If the pointer is null, the tool will be ignored.
//  `formatter_options`
//    Options controlling the specific formatting style.
//
// Returns:
//   An absl::StatusOr containing the formatted string on success, or an error
//   status if formatting fails (e.g., due to invalid input or options).
absl::StatusOr<std::string> FormatHammerSystemMessage(
    const genai_modules::core::proto::Content& system_instruction,
    absl::Span<const genai_modules::core::proto::Tool* const> tools,
    const ModelFormatterOptions& formatter_options);

// Formats the Content proto with the given role and parts into a string,
// following the Hammer model format.
//
// Parameters:
//  `content`
//    The Content proto to format.
//  `formatter_options`
//    Options controlling the specific formatting style.
//
// Returns:
//   An absl::StatusOr containing the formatted string on success, or an error
//   status if formatting fails (e.g., due to invalid input or options).
absl::StatusOr<std::string> FormatHammerContent(
    const genai_modules::core::proto::Content& content,
    const ModelFormatterOptions& formatter_options);

// Returns the string that starts a Hammer model response turn.
//
// Parameters:
//  `formatter_options`
//    Options controlling the specific formatting style.
//
// Returns:
//   The string representing the start of a model turn.
std::string StartHammerTurn(const ModelFormatterOptions& formatter_options);

// Formats a GenerateContentRequest into a single prompt string that can be
// sent to the Hammer model.
//
// Parameters:
//  `request`
//    The GenerateContentRequest proto containing the full context for the
//    model.
//  `formatter_options`
//    Options controlling the specific formatting style.
//
// Returns:
//   An absl::StatusOr containing the formatted prompt string on success, or an
//   error status if formatting fails (e.g., due to invalid input or options).
absl::StatusOr<std::string> FormatHammerRequest(
    const genai_modules::core::proto::GenerateContentRequest& request,
    const ModelFormatterOptions& formatter_options);

// Parses the raw string output from the Hammer model into a structured
// GenerateContentResponse proto. This involves identifying different parts of
// the response, such as text content and function calls.
//
// Parameters:
//  `response`
//    The raw string view of the model's output.
//  `formatter_options`
//    Options controlling the specific formatting style.
//
// Returns:
//   An absl::StatusOr containing the parsed GenerateContentResponse proto on
//   success, or an error status if parsing fails (e.g., due to malformed
//   output or unexpected format).
absl::StatusOr<genai_modules::core::proto::GenerateContentResponse>
ParseHammerResponse(absl::string_view response,
                    const ModelFormatterOptions& formatter_options);

}  // namespace odml::generativeai

#endif  // THIRD_PARTY_ODML_GENAI_MODULES_FUNCTION_CALLING_CORE_HAMMER_FORMATTER_H_
