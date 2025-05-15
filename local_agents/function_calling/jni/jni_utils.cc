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

#include "local_agents/function_calling/jni/jni_utils.h"

#include <jni.h>
#include <jni_md.h>

#include <cstdint>

#include "local_agents/core/proto/content.pb.h"
#include "local_agents/core/proto/generative_service.pb.h"
#include "local_agents/function_calling/core/proto/model_formatter_options.pb.h"

// Helper function to parse protos from jbyteArray
template <typename ProtoT>
bool ParseProto(JNIEnv *env, jbyteArray proto_bytes, ProtoT &proto) {
  const int size = env->GetArrayLength(proto_bytes);
  void *ptr = env->GetPrimitiveArrayCritical(proto_bytes, nullptr);
  if (ptr == nullptr) {
    return false;  // Failed to get array critical section
  }
  bool parsed_ok = proto.ParseFromArray(static_cast<char *>(ptr), size);
  env->ReleasePrimitiveArrayCritical(proto_bytes, ptr, JNI_ABORT);
  return parsed_ok;
}

template <typename ProtoT>
jbyteArray SerializeProto(JNIEnv *env, const ProtoT &proto) {
  const int byte_size = proto.ByteSizeLong();
  ScopedLocalRef<jbyteArray> array(env->NewByteArray(byte_size), env);
  if (!array) {
    return ScopedLocalRef<jbyteArray>(nullptr, env).release();
  }
  void *ptr = env->GetPrimitiveArrayCritical(array.get(), nullptr);
  if (!ptr) {
    return ScopedLocalRef<jbyteArray>(nullptr, env).release();
  }
  proto.SerializeWithCachedSizesToArray(static_cast<uint8_t *>(ptr));
  // NOMUTANTS -- Array must be released.
  env->ReleasePrimitiveArrayCritical(array.get(), ptr, 0);
  return array.release();
}

template bool
ParseProto<::odml::genai_modules::core::proto::GenerateContentRequest>(
    JNIEnv *env, jbyteArray proto_bytes,
    ::odml::genai_modules::core::proto::GenerateContentRequest &request);

template bool ParseProto<::odml::genai_modules::core::proto::Content>(
    JNIEnv *env, jbyteArray proto_bytes,
    ::odml::genai_modules::core::proto::Content &proto);

template bool ParseProto<::odml::generativeai::ModelFormatterOptions>(
    JNIEnv *env, jbyteArray proto_bytes,
    ::odml::generativeai::ModelFormatterOptions &options);

template jbyteArray
SerializeProto<::odml::genai_modules::core::proto::GenerateContentResponse>(
    JNIEnv *env,
    const ::odml::genai_modules::core::proto::GenerateContentResponse &proto);

template jbyteArray SerializeProto<::odml::genai_modules::core::proto::Tool>(
    JNIEnv *env, const ::odml::genai_modules::core::proto::Tool &proto);
