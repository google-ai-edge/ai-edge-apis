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

#include "local_agents/function_calling/core/llama_formatter.h"

#include <sstream>
#include <string>
#include <vector>

#include "absl/status/status.h"        // from @abseil-cpp
#include "absl/status/statusor.h"      // from @abseil-cpp
#include "absl/strings/ascii.h"        // from @abseil-cpp
#include "absl/strings/str_cat.h"      // from @abseil-cpp
#include "absl/strings/string_view.h"  // from @abseil-cpp
#include "absl/strings/strip.h"        // from @abseil-cpp
#include "absl/types/span.h"           // from @abseil-cpp
#include "local_agents/core/proto/content.pb.h"
#include "local_agents/core/proto/generative_service.pb.h"
#include "local_agents/function_calling/core/antlr/parser_utils.h"
#include "local_agents/function_calling/core/format_utils.h"
#include "local_agents/function_calling/core/proto/model_formatter_options.pb.h"
#include "re2/re2.h"  // from @re2

namespace odml::generativeai {

namespace {

using ::odml::genai_modules::core::proto::Candidate;
using ::odml::genai_modules::core::proto::Content;
using ::odml::genai_modules::core::proto::FunctionCall;
using ::odml::genai_modules::core::proto::FunctionResponse;
using ::odml::genai_modules::core::proto::GenerateContentRequest;
using ::odml::genai_modules::core::proto::GenerateContentResponse;
using ::odml::genai_modules::core::proto::Tool;

absl::StatusOr<std::string> FormatFunctionResponse(
    const FunctionResponse& function_response) {
  std::stringstream ss;
  ss << FormatStructAsPython(function_response.response());
  return ss.str();
}

}  // namespace

absl::StatusOr<std::string> FormatLlamaSystemMessage(
    const Content& system_instruction, absl::Span<const Tool* const> tools,
    const ModelFormatterOptions& formatter_options) {
  std::stringstream prompt;
  if (formatter_options.add_prompt_template()) {
    prompt << LlamaFormatter::kStartHeader << "system"
           << LlamaFormatter::kEndHeader << "\n";
  }

  // Append system instruction.
  if (system_instruction.parts_size() > 0) {
    prompt << system_instruction.parts()[0].text();
  }

  // Append tool instructions.
  if (!tools.empty()) {
    prompt << "\n\n";
    prompt
        << "Here is a list of functions in JSON format that you can invoke.\n";
    prompt << "[\n";
    int tool_count = 0;
    for (const auto tool : tools) {
      prompt << FormatToolAsJson(*tool);
      if (++tool_count < tools.size()) {
        prompt << ",";
      }
    }
    prompt << "]\n";
  }
  if (formatter_options.add_prompt_template()) {
    prompt << LlamaFormatter::kEndTurn;
  } else {
    prompt << "\n";
  }
  return prompt.str();
}

absl::StatusOr<std::string> FormatLlamaContent(
    const Content& content, const ModelFormatterOptions& formatter_options) {
  std::stringstream prompt;
  if (formatter_options.add_prompt_template()) {
    prompt << LlamaFormatter::kStartHeader << content.role()
           << LlamaFormatter::kEndHeader << "\n";
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
    prompt << "[";
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
    prompt << "]\n";
  }
  if (formatter_options.add_prompt_template()) {
    prompt << LlamaFormatter::kEndTurn;
  }
  return prompt.str();
}

std::string StartLlamaTurn(const ModelFormatterOptions& formatter_options) {
  return formatter_options.add_prompt_template()
             ? absl::StrCat(LlamaFormatter::kStartHeader, "assistant",
                            LlamaFormatter::kEndHeader)
             : "";
}

absl::StatusOr<std::string> FormatLlamaRequest(
    const GenerateContentRequest& request,
    const ModelFormatterOptions& formatter_options) {
  std::stringstream prompt;

  // Append system instruction and tools.
  if (request.system_instruction().parts_size() > 0 ||
      request.tools_size() > 0) {
    absl::StatusOr<std::string> system_message = FormatLlamaSystemMessage(
        request.system_instruction(), absl::MakeSpan(request.tools()),
        formatter_options);
    if (!system_message.ok()) {
      return absl::InternalError("Failed to format system message.");
    }
    prompt << *system_message;
  }

  // Append contents.
  for (const auto& content : request.contents()) {
    absl::StatusOr<std::string> content_str =
        FormatLlamaContent(content, formatter_options);
    if (!content_str.ok()) {
      return absl::InternalError("Failed to format content.");
    }
    prompt << *content_str;
  }

  // Append start of model turn.
  prompt << StartLlamaTurn(formatter_options);

  return prompt.str();
}

absl::StatusOr<GenerateContentResponse> ParseLlamaResponse(
    absl::string_view response_str) {
  response_str = absl::StripAsciiWhitespace(
      absl::StripSuffix(response_str, LlamaFormatter::kEndTurn));
  TextAndFunctionCalls text_and_function_calls =
      // Only allow code fence to start from the beginning of the line.
      ParseTextAndFunctionCallsString(response_str,
                                      absl::StrCat("^", RE2::QuoteMeta("[")),
                                      RE2::QuoteMeta("]"),
                                      /*escape_in_fence_strings=*/false);
  GenerateContentResponse response;
  Candidate* candidate = response.add_candidates();
  Content* content = candidate->mutable_content();
  content->set_role("assistant");
  if (!text_and_function_calls.text.empty()) {
    content->add_parts()->set_text(text_and_function_calls.text);
  }
  if (!text_and_function_calls.function_calls.empty()) {
    // Llama model returns function calls in the format of
    // "[function_call_1, function_call_2, ...]". The bracket is stripped during
    // parsing. We need to add the brackets back to make it parsable.
    absl::StatusOr<std::vector<FunctionCall>> function_calls =
        ParsePythonExpression(
            absl::StrCat("[", text_and_function_calls.function_calls, "]"));
    if (function_calls.ok()) {
      for (const auto& function_call : *function_calls) {
        *content->add_parts()->mutable_function_call() = function_call;
      }
    } else {
      return absl::InternalError("Failed to parse tool call from output.");
    }
  }
  return response;
}

absl::StatusOr<std::string> LlamaFormatter::FormatSystemMessage(
    const Content& system_instruction,
    absl::Span<const Tool* const> tools) const {
  return FormatLlamaSystemMessage(system_instruction, tools,
                                  formatter_options_);
}

absl::StatusOr<std::string> LlamaFormatter::FormatContent(
    const Content& content) const {
  return FormatLlamaContent(content, formatter_options_);
}

std::string LlamaFormatter::StartModelTurn() const {
  return StartLlamaTurn(formatter_options_);
}

std::string LlamaFormatter::CodeFenceStart() const { return "["; }

std::string LlamaFormatter::CodeFenceEnd() const { return "]"; }

absl::StatusOr<std::string> LlamaFormatter::FormatRequest(
    const GenerateContentRequest& request) const {
  return FormatLlamaRequest(request, formatter_options_);
}

absl::StatusOr<GenerateContentResponse> LlamaFormatter::ParseResponse(
    absl::string_view response) const {
  return ParseLlamaResponse(response);
}

}  // namespace odml::generativeai
