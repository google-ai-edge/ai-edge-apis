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

#include <jni.h>
#include <jni_md.h>

#include <string>

#include "absl/status/statusor.h"  // from @abseil-cpp
#include "local_agents/core/proto/content.pb.h"
#include "local_agents/core/proto/generative_service.pb.h"
#include "local_agents/function_calling/core/hammer_formatter.h"
#include "local_agents/function_calling/core/proto/model_formatter_options.pb.h"
#include "local_agents/function_calling/jni/jni_utils.h"

namespace {

using odml::genai_modules::core::proto::Content;
using odml::genai_modules::core::proto::GenerateContentRequest;
using odml::generativeai::ModelFormatterOptions;

}  // namespace

extern "C" {
JNIEXPORT jstring JNICALL
Java_com_google_ai_edge_localagents_fc_HammerFormatter_nativeFormatSystemMessage(
    JNIEnv* env, jclass ignored, jbyteArray request_bytes,
    jbyteArray options_bytes) {
  GenerateContentRequest request;
  if (!ParseProto(env, request_bytes, request)) {
    return nullptr;
  }
  ModelFormatterOptions options;
  if (options_bytes != nullptr) {
    if (!ParseProto(env, options_bytes, options)) {
      return nullptr;
    }
  }

  absl::StatusOr<std::string> prompt =
      odml::generativeai::FormatHammerSystemMessage(
          request.system_instruction(), request.tools(), options);
  if (!prompt.ok()) {
    return nullptr;
  }
  return env->NewStringUTF(prompt.value().c_str());
}

JNIEXPORT jstring JNICALL
Java_com_google_ai_edge_localagents_fc_HammerFormatter_nativeFormatContent(
    JNIEnv* env, jclass ignored, jbyteArray content_bytes,
    jbyteArray options_bytes) {
  Content content;
  if (!ParseProto(env, content_bytes, content)) {
    return nullptr;
  }

  ModelFormatterOptions options;
  if (!ParseProto(env, options_bytes, options)) {
    return nullptr;
  }

  absl::StatusOr<std::string> prompt =
      odml::generativeai::FormatHammerContent(content, options);
  if (!prompt.ok()) {
    return nullptr;
  }
  return env->NewStringUTF(prompt.value().c_str());
}

JNIEXPORT jstring JNICALL
Java_com_google_ai_edge_localagents_fc_HammerFormatter_nativeStartModelTurn(
    JNIEnv* env, jclass ignored, jbyteArray options_bytes) {
  ModelFormatterOptions options;
  if (!ParseProto(env, options_bytes, options)) {
    return nullptr;
  }
  return env->NewStringUTF(
      odml::generativeai::StartHammerTurn(options).c_str());
}

JNIEXPORT jstring JNICALL
Java_com_google_ai_edge_localagents_fc_HammerFormatter_nativeFormatRequest(
    JNIEnv* env, jclass ignored, jbyteArray request_bytes,
    jbyteArray options_bytes) {
  GenerateContentRequest request;
  if (!ParseProto(env, request_bytes, request)) {
    return nullptr;
  }
  ModelFormatterOptions options;
  if (!ParseProto(env, options_bytes, options)) {
    return nullptr;
  }
  absl::StatusOr<std::string> prompt =
      odml::generativeai::FormatHammerRequest(request, options);
  if (!prompt.ok()) {
    return nullptr;
  }
  return env->NewStringUTF(prompt.value().c_str());
}

JNIEXPORT jbyteArray JNICALL
Java_com_google_ai_edge_localagents_fc_HammerFormatter_nativeParseResponse(
    JNIEnv* env, jclass ignored, jstring output, jbyteArray options_bytes) {
  ModelFormatterOptions options;
  if (!ParseProto(env, options_bytes, options)) {
    return nullptr;
  }
  auto response = odml::generativeai::ParseHammerResponse(
      env->GetStringUTFChars(output, nullptr), options);
  if (!response.ok()) {
    return nullptr;
  }
  return SerializeProto(env, *response);
}
}
