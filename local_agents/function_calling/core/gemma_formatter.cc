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

#include "local_agents/function_calling/core/gemma_formatter.h"

#include <sstream>
#include <string>
#include <vector>

#include "absl/log/check.h"            // from @abseil-cpp
#include "absl/status/status.h"        // from @abseil-cpp
#include "absl/status/statusor.h"      // from @abseil-cpp
#include "absl/strings/str_cat.h"      // from @abseil-cpp
#include "absl/strings/string_view.h"  // from @abseil-cpp
#include "absl/types/span.h"           // from @abseil-cpp
#include "google/protobuf/struct.pb.h"
#include "local_agents/core/proto/content.pb.h"
#include "local_agents/core/proto/generative_service.pb.h"
#include "local_agents/function_calling/core/antlr/parser_utils.h"
#include "local_agents/function_calling/core/format_utils.h"
#include "local_agents/function_calling/core/proto/model_formatter_options.pb.h"

namespace odml::generativeai {
namespace {

using ::odml::genai_modules::core::proto::Content;
using ::odml::genai_modules::core::proto::FunctionCall;
using ::odml::genai_modules::core::proto::FunctionResponse;
using ::odml::genai_modules::core::proto::GenerateContentRequest;
using ::odml::genai_modules::core::proto::GenerateContentResponse;
using ::odml::genai_modules::core::proto::Tool;

constexpr absl::string_view kStartTurn = "<start_of_turn>";
constexpr absl::string_view kEndTurn = "<end_of_turn>";
constexpr absl::string_view kToolCode = "```tool_code";
constexpr absl::string_view kToolOutputs = "```tool_outputs";

absl::StatusOr<std::string> FormatFunctionResponse(
    const FunctionResponse& function_response) {
  std::stringstream ss;
  ss << kToolOutputs << "\n";
  ss << FormatStructAsPython(function_response.response());
  ss << "\n```";
  return ss.str();
}

}  // namespace

absl::StatusOr<std::string> FormatGemmaSystemMessage(
    const Content& system_instruction,
    absl::Span<const odml::genai_modules::core::proto::Tool* const> tools,
    const ModelFormatterOptions& options) {
  std::stringstream ss;
  if (options.add_prompt_template()) {
    ss << kStartTurn << "system\n";
  }

  // Append system instruction.
  if (system_instruction.parts_size() > 0 &&
      system_instruction.parts()[0].has_text()) {
    ss << system_instruction.parts()[0].text();
  }

  // Append tool instructions.
  if (!tools.empty()) {
    ss << "\n\n";
    ss << "Here is a list of functions in JSON format that you can invoke.\n";
    ss << "[\n";
    int tool_count = 0;
    for (const auto& tool : tools) {
      ss << FormatToolAsJson(*tool);
      tool_count += 1;
      if (tool_count < tools.size()) {
        ss << ",";
      }
    }
    ss << "]\n";
  }
  if (options.add_prompt_template()) {
    ss << kEndTurn;
  }
  ss << "\n";
  return ss.str();
}

absl::StatusOr<std::string> FormatGemmaContent(
    const Content& content, const ModelFormatterOptions& options) {
  std::stringstream prompt;
  if (options.add_prompt_template()) {
    prompt << kStartTurn << content.role() << "\n";
  }
  std::vector<const FunctionCall*> function_calls;

  for (const auto& part : content.parts()) {
    if (part.has_text()) {
      prompt << part.text();
    } else if (part.has_function_call()) {
      function_calls.push_back(&part.function_call());
    } else if (part.has_function_response()) {
      absl::StatusOr<std::string> function_response =
          FormatFunctionResponse(part.function_response());
      if (function_response.ok()) {
        prompt << *function_response;
      } else {
        return absl::InternalError(
            "Failed to convert function response to string.");
      }
    } else {
      return absl::InternalError("Unsupported part type.");
    }
  }

  // Add function calls to the end.
  if (!function_calls.empty()) {
    prompt << kToolCode << "\n[";
    int count = 0;
    for (const auto& function_call : function_calls) {
      absl::StatusOr<std::string> function_call_str =
          FormatFunctionCallAsPython(*function_call);
      if (function_call_str.ok()) {
        prompt << *function_call_str;
      } else {
        return absl::InternalError(
            "Failed to convert function call to string.");
      }
      if (++count < function_calls.size()) {
        prompt << ",";
      }
    }
    prompt << "]\n```";
  }
  if (options.add_prompt_template()) {
    prompt << kEndTurn;
  }
  prompt << "\n";
  return prompt.str();
}

std::string StartGemmaTurn(const ModelFormatterOptions& options) {
  return options.add_prompt_template() ? absl::StrCat(kStartTurn, "model\n")
                                       : "";
}

absl::StatusOr<std::string> FormatGemmaRequest(
    const GenerateContentRequest& request,
    const ModelFormatterOptions& options) {
  std::stringstream prompt;

  const bool has_system_instruction =
      request.system_instruction().parts_size() > 0 &&
      request.system_instruction().parts()[0].has_text();
  const bool has_tools = request.tools_size() > 0;

  if (has_system_instruction || has_tools) {
    absl::StatusOr<std::string> system_message = FormatGemmaSystemMessage(
        request.system_instruction(), request.tools(), options);
    if (!system_message.ok()) {
      return absl::InternalError("Failed to format system message.");
    }
    prompt << *system_message;
  }

  // Append contents.
  for (const auto& content : request.contents()) {
    absl::StatusOr<std::string> content_str =
        FormatGemmaContent(content, options);
    if (content_str.ok()) {
      prompt << *content_str;
    } else {
      return absl::InternalError("Failed to convert content to string.");
    }
  }

  // Append start of model turn.
  prompt << StartGemmaTurn(options);
  return prompt.str();
}

absl::StatusOr<GenerateContentResponse> ParseGemmaResponse(
    absl::string_view response_str) {
  return ParseResponse(response_str, absl::StrCat(kToolCode, "\n"), "\n```",
                       "model", SyntaxType::kPython);
}

}  // namespace odml::generativeai
