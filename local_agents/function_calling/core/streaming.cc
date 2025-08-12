#include "local_agents/function_calling/core/streaming.h"

#include <algorithm>
#include <cstddef>
#include <string>
#include <utility>
#include <vector>

#include "absl/status/status.h"        // from @abseil-cpp
#include "absl/status/statusor.h"      // from @abseil-cpp
#include "absl/strings/string_view.h"  // from @abseil-cpp
#include "local_agents/core/proto/content.pb.h"
#include "local_agents/core/proto/generative_service.pb.h"

namespace odml::generativeai {

namespace {

using ::odml::genai_modules::core::proto::FunctionCall;
using ::odml::genai_modules::core::proto::GenerateContentResponse;
using ::odml::genai_modules::core::proto::Part;

size_t SuffixMatchesPrefix(absl::string_view a, absl::string_view b) {
  if (a.empty() || b.empty()) {
    return false;
  }

  size_t max_overlap = std::min(a.length(), b.length());

  for (size_t len = max_overlap; len > 0; --len) {
    if (a.substr(a.length() - len) == b.substr(0, len)) {
      return len;
    }
  }

  return 0;
}
}  // namespace

absl::Status ToolCallPredictFn::operator()(absl::string_view token) {
  if (formatter_ == nullptr) {
    return absl::InvalidArgumentError("formatter_ must not be null.");
  }
  const std::string& code_fence_start = formatter_->CodeFenceStart();
  const std::string& code_fence_end = formatter_->CodeFenceEnd();

  acc_ += token;
  while (cursor_ < acc_.size()) {
    if (!inside_tool_call_) {
      // Look for code fence start.
      size_t start_pos = acc_.find(code_fence_start, cursor_);
      if (start_pos != std::string::npos) {
        // Call the callback with any text up to start of the code fence.
        SendText(absl::string_view(acc_).substr(cursor_, start_pos - cursor_));

        // Move cursor up to code_fence_start.
        cursor_ = start_pos;
        inside_tool_call_ = true;
      } else {
        // code_fence_start not found, but we still need to check
        // if there's a partial match at the end of the string.
        size_t overlap = SuffixMatchesPrefix(
            absl::string_view(acc_).substr(cursor_), code_fence_start);

        if (overlap > 0) {
          // There's a partial match of the code fence at the end of the
          // string.
          size_t possible_start_pos = acc_.size() - overlap;

          // Call the callback with text up to the potential start of the
          // code fence.
          SendText(absl::string_view(acc_).substr(
              cursor_, possible_start_pos - cursor_));

          // Move cursor up to potential start of code fence.
          cursor_ = possible_start_pos;

          // Break for the next token.
          break;
        } else {
          // Remaining string is text.
          SendText(absl::string_view(acc_).substr(cursor_));
          cursor_ = acc_.size();
        }
      }
    }

    if (inside_tool_call_) {
      // Look for code fence end.
      size_t end_pos = acc_.find(code_fence_end, cursor_);
      if (end_pos != std::string::npos) {
        // Process tool code string.
        absl::StatusOr<std::vector<FunctionCall>> function_calls =
            ParseToolCode(absl::string_view(acc_).substr(
                cursor_, end_pos + code_fence_end.size() - cursor_));

        if (!function_calls.ok()) {
          return function_calls.status();
        }

        // Call callback for each function call.
        for (const auto& function_call : *function_calls) {
          Part part;
          *part.mutable_function_call() = function_call;
          callback_(std::move(part));
        }

        // Move cursor to end of tool code block.
        cursor_ = end_pos + code_fence_end.size();
        inside_tool_call_ = false;
      } else {
        // We're inside a tool call but the code fence end has not been
        // found. Break for the next token.
        break;
      }
    }
  }

  return absl::OkStatus();
}

void ToolCallPredictFn::SendText(absl::string_view text) {
  if (text.empty()) {
    return;
  }
  Part part;
  part.set_text(text);
  callback_(std::move(part));
}

absl::StatusOr<std::vector<FunctionCall>> ToolCallPredictFn::ParseToolCode(
    absl::string_view tool_code) {
  absl::StatusOr<GenerateContentResponse> response =
      formatter_->ParseResponse(tool_code);
  if (!response.ok()) {
    return response.status();
  }

  if (response->candidates().empty() ||
      response->candidates(0).content().parts().empty()) {
    return std::vector<FunctionCall>();
  }

  std::vector<FunctionCall> function_calls;
  for (const auto& part : response->candidates(0).content().parts()) {
    if (part.has_function_call()) {
      function_calls.push_back(part.function_call());
    }
  }

  return function_calls;
}

}  // namespace odml::generativeai
