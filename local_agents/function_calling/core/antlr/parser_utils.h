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

#ifndef THIRD_PARTY_ODML_GENAI_MODULES_FUNCTION_CALLING_CORE_ANTLR_PARSER_UTILS_H_
#define THIRD_PARTY_ODML_GENAI_MODULES_FUNCTION_CALLING_CORE_ANTLR_PARSER_UTILS_H_

#include <vector>

#include "absl/status/statusor.h"      // from @abseil-cpp
#include "absl/strings/string_view.h"  // from @abseil-cpp
#include "google/protobuf/struct.pb.h"
#include "local_agents/core/proto/content.pb.h"
#include "local_agents/core/proto/generative_service.pb.h"

namespace odml::generativeai {

// A struct to hold the text and function calls strings.
struct TextAndFunctionCalls {
  absl::string_view text;
  absl::string_view function_calls;
};

enum class SyntaxType {
  kUnknown = 0,
  kPython = 1,
  kJson = 2,
};

// Parses a Python string containing function calls.
absl::StatusOr<std::vector<genai_modules::core::proto::FunctionCall>>
ParsePythonExpression(absl::string_view text);

// Parses a Json string containing function calls.
absl::StatusOr<std::vector<genai_modules::core::proto::FunctionCall>>
ParseJsonExpression(absl::string_view text);

// Parses a raw response string, attempting to extract a code block delimited
// by `code_fence_start` and `code_fence_end`.
//
// Args:
//   `response_str`: The raw string response from the model.
//   `code_fence_start`: The string marking the beginning of the code block.
//   `code_fence_end`: The string marking the end of the code block.
//   `escape_in_fence_strings`: If true, regex special characters within the
//     fence strings will be escaped using RE2::QuoteMeta. Set to false if the
//     fence strings already contain valid regex patterns.
// Returns:
//   A TextAndFunctionCalls struct. `text` contains the portion of
//   `response_str` *before* the `code_fence_start`. `function_calls` contains
//   the portion of `response_str` *between* the start and end fences.
//   If the pattern is not found, behavior depends:
//     - If `code_fence_start` is not found at all, the entire `response_str`
//       is returned in `text`, and `function_calls` is empty.
//     - If `code_fence_start` is found but `code_fence_end` is not (or the
//       regex match fails), the text before the start fence is returned in
//       `text`, and the text *after* the start fence is returned in
//       `function_calls`.
TextAndFunctionCalls ParseTextAndFunctionCallsString(
    absl::string_view response_str, absl::string_view code_fence_start,
    absl::string_view code_fence_end, bool escape_in_fence_strings = true);

// Parses a raw response string, extracts function calls from a delimited code
// block, and constructs a GenerateContentResponse proto.
//
// Args:
//   `response_str`: The raw string response from the model.
//   `code_fence_start`: The string marking the beginning of the code block.
//   `code_fence_end`: The string marking the end of the code block.
//   `response_role`: The role to assign to the response content (e.g.,
//      "model"). `syntax_type`: The syntax type of the function calls string.
//   `escape_in_fence_strings`: If true, regex special characters
//      within the fence strings will be escaped.
//
// Returns:
//   A StatusOr containing the populated GenerateContentResponse proto on
//   success, or an error status if parsing the function calls within the code
//   block fails.
absl::StatusOr<odml::genai_modules::core::proto::GenerateContentResponse>
ParseResponse(absl::string_view response_str,
              absl::string_view code_fence_start,
              absl::string_view code_fence_end, absl::string_view response_role,
              const SyntaxType& syntax_type,
              bool escape_in_fence_strings = true);

}  // namespace odml::generativeai

#endif  // THIRD_PARTY_ODML_GENAI_MODULES_FUNCTION_CALLING_CORE_ANTLR_PARSER_UTILS_H_
