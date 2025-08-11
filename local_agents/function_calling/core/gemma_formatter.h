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

#ifndef THIRD_PARTY_ODML_GENAI_MODULES_FUNCTION_CALLING_CORE_GEMMA_FORMATTER_H_
#define THIRD_PARTY_ODML_GENAI_MODULES_FUNCTION_CALLING_CORE_GEMMA_FORMATTER_H_

#include <string>

#include "absl/status/statusor.h"      // from @abseil-cpp
#include "absl/strings/string_view.h"  // from @abseil-cpp
#include "absl/types/span.h"           // from @abseil-cpp
#include "local_agents/core/proto/content.pb.h"
#include "local_agents/core/proto/generative_service.pb.h"
#include "local_agents/function_calling/core/model_formatter.h"
#include "local_agents/function_calling/core/proto/model_formatter_options.pb.h"

namespace odml::generativeai {

// Formats the system message and tools into a string.
absl::StatusOr<std::string> FormatGemmaSystemMessage(
    const odml::genai_modules::core::proto::Content& system_instruction,
    absl::Span<const odml::genai_modules::core::proto::Tool* const> tools,
    const odml::generativeai::ModelFormatterOptions& options);

// Formats the content into a string.
absl::StatusOr<std::string> FormatGemmaContent(
    const odml::genai_modules::core::proto::Content& content,
    const odml::generativeai::ModelFormatterOptions& options);

// Returns the string that starts a Gemma model response.
std::string StartGemmaTurn(
    const odml::generativeai::ModelFormatterOptions& options);

// Formats a GenerateContentRequest into a string that can be sent to the Gemma
// model.
absl::StatusOr<std::string> FormatGemmaRequest(
    const odml::genai_modules::core::proto::GenerateContentRequest& request,
    const odml::generativeai::ModelFormatterOptions& options);

// Parses the string output from the Gemma model into a GenerateContentResponse.
absl::StatusOr<odml::genai_modules::core::proto::GenerateContentResponse>
ParseGemmaResponse(absl::string_view response);

class GemmaFormatter : public ModelFormatter {
 public:
  static constexpr absl::string_view kStartTurn = "<start_of_turn>";
  static constexpr absl::string_view kEndTurn = "<end_of_turn>";
  static constexpr absl::string_view kToolCodeStart = "```tool_code";
  static constexpr absl::string_view kToolCodeEnd = "```";
  static constexpr absl::string_view kToolOutputs = "```tool_outputs";

  explicit GemmaFormatter() { options_.set_add_prompt_template(true); }

  explicit GemmaFormatter(
      const odml::generativeai::ModelFormatterOptions& options)
      : options_(options) {}

  // Formats a system message and associated tools into a string that can be
  // sent to the inference backend.
  absl::StatusOr<std::string> FormatSystemMessage(
      const odml::genai_modules::core::proto::Content& system_instruction,
      absl::Span<const odml::genai_modules::core::proto::Tool* const> tools)
      override;

  // Formats a Content object into a string that can be sent to a the inference
  // backend.
  absl::StatusOr<std::string> FormatContent(
      const odml::genai_modules::core::proto::Content& content) override;

  // Returns a string that indicates the start of a model turn.
  std::string StartModelTurn() override;

  // Returns the strings that indicate when a tool call starts and ends.
  std::string CodeFenceStart() override;
  std::string CodeFenceEnd() override;

  // Formats a GenerateContentRequest into a string that can be sent to the
  // Gemma model.
  absl::StatusOr<std::string> FormatRequest(
      const odml::genai_modules::core::proto::GenerateContentRequest& request)
      override;

  // Parses the string output from the Gemma model into a
  // GenerateContentResponse.
  absl::StatusOr<odml::genai_modules::core::proto::GenerateContentResponse>
  ParseResponse(absl::string_view response_str) override;

 private:
  odml::generativeai::ModelFormatterOptions options_;
};

}  // namespace odml::generativeai

#endif  // THIRD_PARTY_ODML_GENAI_MODULES_FUNCTION_CALLING_CORE_GEMMA_FORMATTER_H_
