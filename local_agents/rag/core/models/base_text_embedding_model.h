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

#ifndef THIRD_PARTY_ODML_LLM_EXTENSIONS_RAG_PIPELINE_CORE_MODELS_BASE_EMBEDDING_MODEL_H_
#define THIRD_PARTY_ODML_LLM_EXTENSIONS_RAG_PIPELINE_CORE_MODELS_BASE_EMBEDDING_MODEL_H_

#include <vector>

#include "absl/status/statusor.h"      // from @abseil-cpp
#include "absl/strings/string_view.h"  // from @abseil-cpp
#include "absl/types/span.h"           // from @abseil-cpp
#include "local_agents/rag/core/protos/embedding_models.pb.h"  // from @ai_edge_apis

namespace rag {
namespace core {

// An interface for text embedding model that encodes text as vectors.
class BaseTextEmbeddingModel {
 public:
  // Returns embedding vector for the given text.
  virtual absl::StatusOr<std::vector<float>> GetEmbeddings(
      const TextEmbeddingRequest& request) const = 0;
  // Returns embedding vectors for the given texts in order.
  virtual absl::StatusOr<std::vector<std::vector<float>>> GetBatchEmbeddings(
      const TextEmbeddingRequest& request) const = 0;
  virtual ~BaseTextEmbeddingModel() = default;
};

}  // namespace core
}  // namespace rag

#endif  // THIRD_PARTY_ODML_LLM_EXTENSIONS_RAG_PIPELINE_CORE_MODELS_BASE_EMBEDDING_MODEL_H_
