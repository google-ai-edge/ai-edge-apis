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

#ifndef THIRD_PARTY_ODML_LLM_EXTENSIONS_RAG_PIPELINE_CORE_MODELS_BASE_LANGUAGE_MODEL_H_
#define THIRD_PARTY_ODML_LLM_EXTENSIONS_RAG_PIPELINE_CORE_MODELS_BASE_LANGUAGE_MODEL_H_

#include <functional>
#include <optional>

#include "absl/status/status.h"    // from @abseil-cpp
#include "absl/status/statusor.h"  // from @abseil-cpp
#include "local_agents/rag/core/protos/language_models.pb.h"  // from @ai_edge_apis

namespace rag {
namespace core {

// Callback function to receive streaming results from a language model.
using StreamingResponseFn = std::function<void(const LanguageModelResponse&)>;

// An interface for the language model.
class BaseLanguageModel {
 public:
  virtual absl::StatusOr<LanguageModelResponse> GenerateResponse(
      const LanguageModelRequest& request) = 0;
  virtual absl::Status GenerateStreamResponse(
      const LanguageModelRequest& request,
      std::optional<StreamingResponseFn> callback) = 0;
  virtual ~BaseLanguageModel() = default;
};

}  // namespace core
}  // namespace rag

#endif  // THIRD_PARTY_ODML_LLM_EXTENSIONS_RAG_PIPELINE_CORE_MODELS_BASE_LANGUAGE_MODEL_H_
