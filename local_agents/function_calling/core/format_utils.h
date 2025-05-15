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

#ifndef THIRD_PARTY_ODML_GENAI_MODULES_FUNCTION_CALLING_CORE_FORMAT_UTILS_H_
#define THIRD_PARTY_ODML_GENAI_MODULES_FUNCTION_CALLING_CORE_FORMAT_UTILS_H_

#include <optional>
#include <string>
#include <utility>
#include <vector>

#include "absl/status/statusor.h"      // from @abseil-cpp
#include "absl/strings/string_view.h"  // from @abseil-cpp
#include "google/protobuf/struct.pb.h"
#include "local_agents/core/proto/content.pb.h"
#include "local_agents/core/proto/generative_service.pb.h"

namespace odml::generativeai {

// Extracts the string between the given prefix and suffix from a given text.
// Returns std::nullopt if the text does not match the prefix and suffix.
std::optional<absl::string_view> ExtractInnerText(absl::string_view text,
                                                  absl::string_view prefix,
                                                  absl::string_view suffix);

// Put required parameters before optional parameters, and sort the parameters
// alphabetically within each group.
std::vector<std::pair<std::string, genai_modules::core::proto::Schema>>
SortParameters(const genai_modules::core::proto::Schema& schema);

std::string FormatTypeAsJson(const genai_modules::core::proto::Type& type);

std::string FormatFunctionDeclarationAsJson(
    const genai_modules::core::proto::FunctionDeclaration&
        function_declaration);

std::string FormatToolAsJson(const genai_modules::core::proto::Tool& tool_def);

std::string FormatValueAsPython(const google::protobuf::Value& value);

std::string FormatStructAsPython(const google::protobuf::Struct& struct_value);

std::string FormatListAsPython(const google::protobuf::ListValue& list_value);

absl::StatusOr<std::string> FormatFunctionCallAsPython(
    const genai_modules::core::proto::FunctionCall& call);

// Formats a Value as a JSON string.
std::string FormatValueAsJson(const google::protobuf::Value& value);

// Formats a Struct as a JSON string.
std::string FormatStructAsJson(const google::protobuf::Struct& struct_value);

// Formats ListValue as a JSON string.
std::string FormatListAsJson(const google::protobuf::ListValue& list_value);

// Formats a FunctionCall as a JSON string.
absl::StatusOr<std::string> FormatFunctionCallAsJson(
    const genai_modules::core::proto::FunctionCall& call);

// Formats a FunctionResponse as a JSON string.
absl::StatusOr<std::string> FormatFunctionResponseAsJson(
    const genai_modules::core::proto::FunctionResponse& response);

}  // namespace odml::generativeai

#endif  // THIRD_PARTY_ODML_GENAI_MODULES_FUNCTION_CALLING_CORE_FORMAT_UTILS_H_
