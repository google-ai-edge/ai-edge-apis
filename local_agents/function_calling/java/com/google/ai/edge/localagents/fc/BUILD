# Copyright 2025 The Google AI Edge Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

load("@ai_edge_apis//local_agents/rag/maven:maven_repository.bzl", "android_jni_aar", "maven_artifact")
load("@rules_android//android:rules.bzl", "android_library")

package(default_visibility = [
    ":default_visibility",
])

package_group(
    name = "default_visibility",
    packages = [
        "//local_agents/...",
    ],
)

# The next version of the FC SDK.
# The minor version code should be bumped after every release.
FC_SDK_VERSION = "0.2.0"

android_library(
    name = "session",
    srcs = ["Session.java"],
    deps = [
        ":function_call_exception",
        "//local_agents/core/proto:content_java_proto_lite",
        "//local_agents/function_calling/core/proto:constraint_options_java_proto_lite",
        "@maven//:com_google_guava_guava",
    ],
)

android_library(
    name = "inference_backend",
    srcs = ["InferenceBackend.java"],
    deps = [":session"],
)

android_library(
    name = "constraint_provider",
    srcs = ["ConstraintProvider.java"],
    deps = [
        "//local_agents/core/proto:content_java_proto_lite",
        "//local_agents/function_calling/core/proto:constraint_options_java_proto_lite",
    ],
)

android_library(
    name = "fst_constraint_provider",
    srcs = ["FstConstraintProvider.java"],
    deps = [
        ":constraint_provider",
        "//local_agents/core/proto:content_java_proto_lite",
        "//local_agents/function_calling/core/proto:constraint_options_java_proto_lite",
        "//local_agents/function_calling/jni:jni_fst_constraint_android",
    ],
)

android_library(
    name = "llm_inference_backend",
    srcs = [
        "LlmInferenceBackend.java",
        "LlmInferenceBackendSession.java",
    ],
    deps = [
        ":constraint_provider",
        ":fst_constraint_provider",
        ":function_call_exception",
        ":inference_backend",
        ":model_formatter",
        ":session",
        "//local_agents/core/proto:content_java_proto_lite",
        "//local_agents/function_calling/core/proto:constraint_options_java_proto_lite",
        "@maven//:com_google_guava_guava",
        "@maven//:com_google_mediapipe_tasks_genai",
    ],
)

android_library(
    name = "model_formatter",
    srcs = [
        "ModelFormatter.java",
        "ModelFormatterOptions.java",
    ],
    deps = [
        ":function_call_exception",
        "//local_agents/core/proto:content_java_proto_lite",
        "//local_agents/core/proto:generative_service_java_proto_lite",
        "//local_agents/function_calling/core/proto:model_formatter_options_java_proto_lite",
        "//third_party:autovalue",
        "@maven//:org_jspecify_jspecify",
    ],
)

android_library(
    name = "gemma_formatter",
    srcs = ["GemmaFormatter.java"],
    deps = [
        ":function_call_exception",
        ":model_formatter",
        "//local_agents/core/proto:content_java_proto_lite",
        "//local_agents/core/proto:generative_service_java_proto_lite",
        "//local_agents/function_calling/core/proto:model_formatter_options_java_proto_lite",
        "//local_agents/function_calling/jni:jni_gemma_formatter_android",
        "@protobuf//:protobuf_javalite",
    ],
)

android_library(
    name = "llama_formatter",
    srcs = ["LlamaFormatter.java"],
    deps = [
        ":function_call_exception",
        ":model_formatter",
        "//local_agents/core/proto:content_java_proto_lite",
        "//local_agents/core/proto:generative_service_java_proto_lite",
        "//local_agents/function_calling/core/proto:model_formatter_options_java_proto_lite",
        "//local_agents/function_calling/jni:jni_llama_formatter_android",
        "@protobuf//:protobuf_javalite",
    ],
)

android_library(
    name = "hammer_formatter",
    srcs = ["HammerFormatter.java"],
    deps = [
        ":function_call_exception",
        ":model_formatter",
        "//local_agents/core/proto:content_java_proto_lite",
        "//local_agents/core/proto:generative_service_java_proto_lite",
        "//local_agents/function_calling/core/proto:model_formatter_options_java_proto_lite",
        "//local_agents/function_calling/jni:jni_hammer_formatter_android",
        "@protobuf//:protobuf_javalite",
    ],
)

android_library(
    name = "function_call_exception",
    srcs = [
        "FunctionCallException.java",
    ],
    deps = [
        "//local_agents/core/proto:content_java_proto_lite",
        "@maven//:org_jspecify_jspecify",
    ],
)

android_library(
    name = "generative_model",
    srcs = [
        "ChatSession.java",
        "GenerativeModel.java",
    ],
    deps = [
        ":function_call_exception",
        ":inference_backend",
        ":session",
        "//local_agents/core/proto:content_java_proto_lite",
        "//local_agents/core/proto:generative_service_java_proto_lite",
        "//local_agents/function_calling/core/proto:constraint_options_java_proto_lite",
        "//third_party:autovalue",
        "@maven//:com_google_guava_guava",
        "@maven//:org_jspecify_jspecify",
    ],
)

filegroup(
    name = "maven_srcs",
    srcs = [
        "ChatSession.java",
        "ConstraintProvider.java",
        "FstConstraintProvider.java",
        "FunctionCallException.java",
        "GemmaFormatter.java",
        "GenerativeModel.java",
        "HammerFormatter.java",
        "InferenceBackend.java",
        "LlamaFormatter.java",
        "LlmInferenceBackend.java",
        "LlmInferenceBackendSession.java",
        "ModelFormatter.java",
        "ModelFormatterOptions.java",
        "Session.java",
    ],
)

android_library(
    name = "function_calling_srcs_lib",
    srcs = [
        ":maven_srcs",
        "//local_agents/function_calling/core/proto:constraint_options_java_proto_lite_srcs",
        "//local_agents/function_calling/core/proto:content_java_proto_lite_srcs",
        "//local_agents/function_calling/core/proto:generative_service_java_proto_lite_srcs",
        "//local_agents/function_calling/core/proto:model_formatter_options_java_proto_lite_srcs",
        "//local_agents/function_calling/java/com/google/ai/edge/localagents/fc/toolretrieval:maven_srcs",
    ],
    deps = [
        "//local_agents/core/proto:content_java_proto_lite",
        "//local_agents/core/proto:generative_service_java_proto_lite",
        "//local_agents/function_calling/core/proto:constraint_options_java_proto_lite",
        "//local_agents/function_calling/core/proto:model_formatter_options_java_proto_lite",
        "//third_party:autovalue",
        "@ai_edge_apis//local_agents/rag/java/com/google/ai/edge/localagents/rag/memory:semantic_memory",
        "@ai_edge_apis//local_agents/rag/java/com/google/ai/edge/localagents/rag/retrieval:entities",
        "@maven//:com_google_guava_guava",
        "@maven//:com_google_mediapipe_tasks_genai",
        "@maven//:org_checkerframework_checker_qual",
        "@maven//:org_jspecify_jspecify",
        "@protobuf//:protobuf_javalite",
    ],
)

android_jni_aar(
    name = "function_calling_jni_aar",
    native_libraries = [
        "//local_agents/function_calling/jni:jni_fst_constraint_android",
        "//local_agents/function_calling/jni:jni_gemma_formatter_android",
        "//local_agents/function_calling/jni:jni_hammer_formatter_android",
        "//local_agents/function_calling/jni:jni_llama_formatter_android",
    ],
    source_library = ":function_calling_srcs_lib",
)

# Should be build as such:
# blaze --blazerc=/dev/null build --android_platforms=//:arm64-v8a -c opt --copt=-Os --linkopt -s --strip always \
#   //local_agents/function_calling/java/com/google/ai/edge/localagents/fc:fc_maven_artifact \
maven_artifact(
    name = "fc_maven_artifact",
    src = "function_calling_jni_aar.aar",
    artifact_deps = [
        "com.google.errorprone:error_prone_annotations:2.37.0",
        "com.google.guava:guava:33.3.1-android",
        "org.json:json:20250107",
        "com.google.mediapipe:tasks-genai:(,)",
    ],
    artifact_id = "localagents-fc",
    artifact_optional_deps = [],
    group_id = "com.google.ai.edge.localagents",
    inception_year = "2025",
    lib_description = "The Google AI Edge Function Calling library.",
    lib_name = "Google AI Edge Function Calling",
    lib_url = "https://github.com/google-ai-edge/ai-edge-apis",
    version = FC_SDK_VERSION,
)
