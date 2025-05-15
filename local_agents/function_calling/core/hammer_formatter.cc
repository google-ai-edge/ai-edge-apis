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

#include "local_agents/function_calling/core/hammer_formatter.h"

#include <sstream>
#include <string>
#include <vector>

#include "absl/log/absl_log.h"         // from @abseil-cpp
#include "absl/status/status.h"        // from @abseil-cpp
#include "absl/status/statusor.h"      // from @abseil-cpp
#include "absl/strings/str_cat.h"      // from @abseil-cpp
#include "absl/strings/str_join.h"     // from @abseil-cpp
#include "absl/strings/string_view.h"  // from @abseil-cpp
#include "absl/strings/strip.h"        // from @abseil-cpp
#include "absl/strings/substitute.h"   // from @abseil-cpp
#include "absl/types/span.h"           // from @abseil-cpp
#include "local_agents/core/proto/content.pb.h"
#include "local_agents/core/proto/generative_service.pb.h"
#include "local_agents/function_calling/core/antlr/parser_utils.h"
#include "local_agents/function_calling/core/format_utils.h"
#include "local_agents/function_calling/core/proto/model_formatter_options.pb.h"
#include "re2/re2.h"  // from @re2

namespace odml::generativeai {

namespace {

using ::odml::genai_modules::core::proto::Content;
using ::odml::genai_modules::core::proto::FunctionCall;
using ::odml::genai_modules::core::proto::GenerateContentRequest;
using ::odml::genai_modules::core::proto::GenerateContentResponse;
using ::odml::genai_modules::core::proto::Part;
using ::odml::genai_modules::core::proto::Tool;

constexpr absl::string_view kStartHeader = "<|im_start|>";
constexpr absl::string_view kEndHeader = "<|im_end|>";
constexpr absl::string_view kEndText = "<|endoftext|>";
constexpr absl::string_view kTasksToolsFormatInstructions =
    R"""([BEGIN OF TASK INSTRUCTIONS]
You are a tool calling assistant. In order to complete the user's request, you need to select one or more appropriate tools from the following tools and fill in the correct values for the tool parameters. Your specific tasks are:
1. Make one or more function/tool calls to meet the request based on the question.
2. If none of the function can be used, point it out and refuse to answer.
3. If the given question lacks the parameters required by the function, also point it out.

The following are characters that may interact with you
1. user: Provides query or additional information.
2. tool: Returns the results of the tool calling.

[END OF TASK INSTRUCTIONS]

[BEGIN OF AVAILABLE TOOLS]
$0
[END OF AVAILABLE TOOLS]

[BEGIN OF FORMAT INSTRUCTION]

The output MUST strictly adhere to the following JSON format, and NO other text MUST be included.
The example format is as follows. Please make sure the parameter type is correct. If no function call is needed, please directly output an empty list '[]'
```
[
    {"name": "func_name1", "arguments": {"argument1": "value1", "argument2": "value2"}},
    ... (more tool calls as required)
]
```

[END OF FORMAT INSTRUCTION]

)""";

// Formats a span of tools into a JSON string, that is used by the Hammer
// model.
std::string FormatTools(absl::Span<const Tool* const> tools) {
  std::vector<std::string> tools_str;
  tools_str.reserve(tools.size());
  for (const Tool* tool : tools) {
    if (tool != nullptr) {
      tools_str.push_back(FormatToolAsJson(*tool));
    }
  }
  return absl::StrCat("[", absl::StrJoin(tools_str, ", "), "]");
}

// Returns the agent role string for the model. If not set, the default role is
// "assistant".
std::string AgentRole(const ModelFormatterOptions& formatter_options) {
  return formatter_options.has_agent_role() ? formatter_options.agent_role()
                                            : "assistant";
}

// Strips the response of the Hammer start/end markers with regex. If the
// markers are not found, it will fallback to trim from the original string.
// The returned striped string has the same lifetime as the input string.
absl::string_view StripResponse(
    absl::string_view response,
    const ModelFormatterOptions& formatter_options) {
  std::string pattern = absl::StrCat(
      RE2::QuoteMeta(kStartHeader), "\\s*",
      RE2::QuoteMeta(AgentRole(formatter_options)), "\\s*",
      "(.*?)"  // Capture group 1: the content
      "(?:",
      RE2::QuoteMeta(kEndText), "|", RE2::QuoteMeta(kEndHeader),
      ")");  // Non-capturing group for end markers (kEndText or kEndHeader)

  RE2::Options regex_options;
  regex_options.set_dot_nl(true);
  RE2 regex(pattern, regex_options);
  absl::string_view captured_content;

  if (RE2::PartialMatch(response, regex, &captured_content)) {
    return captured_content;
  } else {
    // Fallback: trim from the original string.
    captured_content = absl::StripPrefix(captured_content, kStartHeader);
    captured_content =
        absl::StripPrefix(captured_content, AgentRole(formatter_options));
    captured_content = absl::StripSuffix(captured_content, kEndText);
    captured_content = absl::StripSuffix(response, kEndHeader);
    return captured_content;
  }
}

}  // namespace

absl::StatusOr<std::string> FormatHammerSystemMessage(
    const Content& system_instruction, absl::Span<const Tool* const> tools,
    const ModelFormatterOptions& formatter_options) {
  std::string prompt;
  if (formatter_options.add_prompt_template()) {
    absl::StrAppend(&prompt, kStartHeader, system_instruction.role(), "\n");
  }

  // Append system instruction.
  if (system_instruction.parts_size() > 0) {
    absl::StrAppend(&prompt, system_instruction.parts()[0].text(), "\n");
  }

  // Tasks, tools and format instructions.
  absl::StrAppend(&prompt, absl::Substitute(kTasksToolsFormatInstructions,
                                            FormatTools(tools)));

  if (formatter_options.add_prompt_template()) {
    absl::StrAppend(&prompt, kEndHeader, "\n");
  }

  return prompt;
};

// Formats the content into a string.
absl::StatusOr<std::string> FormatHammerContent(
    const Content& content, const ModelFormatterOptions& formatter_options) {
  std::string prompt;
  if (formatter_options.add_prompt_template()) {
    absl::StrAppend(&prompt, kStartHeader, content.role(), "\n");
  }
  std::vector<const FunctionCall*> function_calls;

  for (const Part& part : content.parts()) {
    if (part.has_text()) {
      absl::StrAppend(&prompt, part.text());
    } else if (part.has_function_call()) {
      function_calls.push_back(&part.function_call());
    } else if (part.has_function_response()) {
      absl::StatusOr<std::string> function_response =
          FormatFunctionResponseAsJson(part.function_response());
      if (function_response.ok()) {
        absl::StrAppend(&prompt, *function_response);
      } else {
        return absl::InternalError(
            absl::StrCat("Failed to convert function response to string. ",
                         function_response.status().message()));
      }
    } else {
      return absl::InternalError(
          absl::StrCat("Unsupported part type.", part.DebugString()));
    }
  }

  // Add function calls to the end.
  if (!function_calls.empty()) {
    absl::StrAppend(&prompt, "```[");
    int count = 0;
    for (const FunctionCall* function_call : function_calls) {
      absl::StatusOr<std::string> formatted_function_call =
          FormatFunctionCallAsJson(*function_call);
      if (formatted_function_call.ok()) {
        absl::StrAppend(&prompt, *formatted_function_call);
      } else {
        return absl::InternalError(
            absl::StrCat("Failed to convert function call to string. ",
                         formatted_function_call.status().message()));
      }
      if (++count < function_calls.size()) {
        absl::StrAppend(&prompt, ",");
      }
    }
    absl::StrAppend(&prompt, "]```\n");
  }
  if (formatter_options.add_prompt_template()) {
    absl::StrAppend(&prompt, kEndHeader, "\n");
  }
  return prompt;
}

// Returns the string that starts a Hammer model response, if a prompt template
// is provided, otherwise returns an empty string.
std::string StartHammerTurn(const ModelFormatterOptions& formatter_options) {
  if (formatter_options.add_prompt_template()) {
    return absl::StrCat(kStartHeader, AgentRole(formatter_options), "\n");
  }
  return "";
}

// Formats a GenerateContentRequest into a string that can be sent to the Hammer
// model.
absl::StatusOr<std::string> FormatHammerRequest(
    const GenerateContentRequest& request,
    const ModelFormatterOptions& formatter_options) {
  std::stringstream prompt;

  const bool has_system_instruction =
      request.system_instruction().parts_size() > 0 &&
      request.system_instruction().parts()[0].has_text();
  const bool has_tools = request.tools_size() > 0;

  if (has_system_instruction || has_tools) {
    absl::StatusOr<std::string> system_message = FormatHammerSystemMessage(
        request.system_instruction(), request.tools(), formatter_options);
    if (!system_message.ok()) {
      return absl::InternalError(
          absl::StrCat("Failed to format system message. ",
                       system_message.status().message()));
    }
    prompt << *system_message;
  }

  // Append contents.
  for (const Content& content : request.contents()) {
    absl::StatusOr<std::string> formatted_content =
        FormatHammerContent(content, formatter_options);
    if (formatted_content.ok()) {
      prompt << *formatted_content;
    } else {
      return absl::InternalError(
          absl::StrCat("Failed to convert content to string. ",
                       formatted_content.status().message()));
    }
  }

  // Append start of model turn.
  prompt << StartHammerTurn(formatter_options);
  return prompt.str();
}

// Parses the string output from the Hammer model into a
// GenerateContentResponse.
absl::StatusOr<GenerateContentResponse> ParseHammerResponse(
    absl::string_view response,
    const ModelFormatterOptions& formatter_options) {
  return ParseResponse(StripResponse(response, formatter_options), "```", "```",
                       AgentRole(formatter_options), SyntaxType::kJson);
}

}  // namespace odml::generativeai
