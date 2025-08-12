#include "local_agents/function_calling/core/streaming_llm_engine.h"

#include <functional>
#include <utility>
#include <vector>

#include "absl/status/status.h"  // from @abseil-cpp
#include "local_agents/function_calling/core/model_formatter.h"
#include "local_agents/function_calling/core/streaming.h"
#include "third_party/odml/infra/genai/inference/llm_engine.h"

namespace odml::generativeai {

std::function<absl::Status(
    std::vector<odml::infra::LlmInferenceEngine::Session::Response>)>
CreateLlmEnginePredictFn(ToolCallPredictFn::Callback callback,
                         ModelFormatter* formatter) {
  ToolCallPredictFn tool_call_predict_fn(callback, formatter);
  return [tool_call_predict_fn = std::move(tool_call_predict_fn)](
             std::vector<odml::infra::LlmInferenceEngine::Session::Response>
                 responses) mutable {
    for (const auto& response : responses) {
      for (const auto& token : response.response_tokens) {
        absl::Status status = tool_call_predict_fn(token);
        if (!status.ok()) {
          return status;
        }
      }
    }

    return absl::OkStatus();
  };
}

}  // namespace odml::generativeai
