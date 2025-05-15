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

#ifndef THIRD_PARTY_ODML_GENAI_MODULES_FUNCTION_CALLING_JNI_JNI_UTILS_H_
#define THIRD_PARTY_ODML_GENAI_MODULES_FUNCTION_CALLING_JNI_JNI_UTILS_H_

#include <jni.h>
#include <jni_md.h>

#include <memory>
#include <type_traits>

#include "absl/log/check.h"  // from @abseil-cpp
// A deleter to be used with std::unique_ptr to delete JNI local references.
class LocalRefDeleter {
 public:
  // Style guide violating implicit constructor so that the LocalRefDeleter
  // is implicitly constructed from the second argument to ScopedLocalRef.
  LocalRefDeleter(JNIEnv* env) : env_(env) {}  // NOLINT

  LocalRefDeleter(const LocalRefDeleter& orig) = default;

  // Copy assignment to allow move semantics in ScopedLocalRef.
  LocalRefDeleter& operator=(const LocalRefDeleter& rhs) {
    // As the deleter and its state are thread-local, ensure the envs
    // are consistent but do nothing.
    CHECK_EQ(env_, rhs.env_);  // NOLINT
    return *this;
  }

  // The delete operator.
  void operator()(jobject o) const { env_->DeleteLocalRef(o); }

 private:
  // The env_ stashed to use for deletion. Thread-local, don't share!
  JNIEnv* const env_;
};

// A smart pointer that deletes a JNI local reference when it goes out
// of scope. Usage is:
// ScopedLocalRef<jobject> scoped_local(env->JniFunction(), env);
//
// In general you should create ScopedLocalRef by using the functions
// in JniHelper, such as:
// ScopedLocalRef<jstring> my_string =
//     CHECK_JNI(FATAL, env).NewStringUTF("my string");
//
// Note that this class is not thread-safe since it caches JNIEnv in
// the deleter. Do not use the same jobject across different threads.
template <typename T>
using ScopedLocalRef =
    std::unique_ptr<typename std::remove_pointer<T>::type, LocalRefDeleter>;

template <typename ProtoT>
bool ParseProto(JNIEnv* env, jbyteArray proto_bytes, ProtoT& proto);

template <typename ProtoT>
jbyteArray SerializeProto(JNIEnv* env, const ProtoT& proto);

#endif  // THIRD_PARTY_ODML_GENAI_MODULES_FUNCTION_CALLING_JNI_JNI_UTILS_H_
