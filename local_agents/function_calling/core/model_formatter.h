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

#ifndef THIRD_PARTY_ODML_GENAI_MODULES_FUNCTION_CALLING_CORE_MODEL_FORMATTER_H_
#define THIRD_PARTY_ODML_GENAI_MODULES_FUNCTION_CALLING_CORE_MODEL_FORMATTER_H_

#include <string>

#include "absl/status/statusor.h"      // from @abseil-cpp
#include "absl/strings/string_view.h"  // from @abseil-cpp
#include "absl/types/span.h"           // from @abseil-cpp
#include "local_agents/core/proto/generative_service.pb.h"
namespace odml {
namespace generativeai {

// A ModelFormatter is responsible for converting between
// GenerateContentRequest/Response objects and the format expected by a specific
// Generative AI model.
class ModelFormatter {
 public:
  virtual ~ModelFormatter() = default;

  // Formats a system message and associated tools into a string that can be
  // sent to the inference backend.
  virtual absl::StatusOr<std::string> FormatSystemMessage(
      const odml::genai_modules::core::proto::Content& system_instruction,
      absl::Span<const odml::genai_modules::core::proto::Tool* const> tools)
      const = 0;

  // Formats a Content object into a string that can be sent to a the inference
  // backend.
  virtual absl::StatusOr<std::string> FormatContent(
      const odml::genai_modules::core::proto::Content& content) const = 0;

  // Returns a string that indicates the start of a model turn.
  virtual std::string StartModelTurn() const = 0;

  // Returns the strings that indicate when a tool call starts and ends.
  virtual std::string CodeFenceStart() const = 0;
  virtual std::string CodeFenceEnd() const = 0;

  // Formats a GenerateContentRequest into a string that can be sent to a
  // Generative AI model.
  virtual absl::StatusOr<std::string> FormatRequest(
      const odml::genai_modules::core::proto::GenerateContentRequest& request)
      const = 0;

  // Parses a response string from a Generative AI model into a
  // GenerateContentResponse.
  virtual absl::StatusOr<
      odml::genai_modules::core::proto::GenerateContentResponse>
  ParseResponse(absl::string_view response) const = 0;
};

}  // namespace generativeai
}  // namespace odml

#endif  // THIRD_PARTY_ODML_GENAI_MODULES_FUNCTION_CALLING_CORE_MODEL_FORMATTER_H_
