#ifndef THIRD_PARTY_ODML_GENAI_MODULES_FUNCTION_CALLING_CORE_STREAMING_LLM_ENGINE_H_
#define THIRD_PARTY_ODML_GENAI_MODULES_FUNCTION_CALLING_CORE_STREAMING_LLM_ENGINE_H_

#include <functional>
#include <vector>

#include "absl/status/status.h"  // from @abseil-cpp
#include "local_agents/function_calling/core/model_formatter.h"
#include "local_agents/function_calling/core/streaming.h"
#include "third_party/odml/infra/genai/inference/llm_engine.h"

namespace odml::generativeai {

std::function<absl::Status(
    std::vector<odml::infra::LlmInferenceEngine::Session::Response>)>
CreateLlmEnginePredictFn(ToolCallPredictFn::Callback callback,
                         ModelFormatter* formatter);

}  // namespace odml::generativeai

#endif  // THIRD_PARTY_ODML_GENAI_MODULES_FUNCTION_CALLING_CORE_STREAMING_LLM_ENGINE_H_
