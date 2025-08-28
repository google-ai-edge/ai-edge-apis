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
load("@rules_cc//cc:cc_binary.bzl", "cc_binary")
load("@rules_cc//cc:cc_library.bzl", "cc_library")
load("//third_party:ai_edge_files.bzl", "ai_edge_files")

package(default_visibility = [
    "//visibility:public",
])

ai_edge_files(
    srcs = [
        "rag_pipeline_android_arm64_libgecko_embedding_model_jni.so",
        "rag_pipeline_android_arm64_libsqlite_vector_store_jni.so",
        "rag_pipeline_android_arm64_libtext_chunker_jni.so",
        "rag_pipeline_x86_64_libgecko_embedding_model_jni.so",
        "rag_pipeline_x86_64_libsqlite_vector_store_jni.so",
        "rag_pipeline_x86_64_libtext_chunker_jni.so",
    ],
)

# The next version of the RAG SDK.
# The minor version code should be bumped after every release.
RAG_SDK_VERSION = "0.3.0"

android_library(
    name = "rag_lib",
    srcs = [
        "@ai_edge_apis//local_agents/rag/core/protos:embedding_models_java_proto_lite_srcs",
        "@ai_edge_apis//local_agents/rag/core/protos:memory_java_proto_lite_srcs",
        "@ai_edge_apis//local_agents/rag/core/protos:vector_stores_java_proto_lite_srcs",
        "@ai_edge_apis//local_agents/rag/java/com/google/ai/edge/localagents/rag/chains:maven_srcs",
        "@ai_edge_apis//local_agents/rag/java/com/google/ai/edge/localagents/rag/chunking:maven_srcs",
        "@ai_edge_apis//local_agents/rag/java/com/google/ai/edge/localagents/rag/memory:maven_srcs",
        "@ai_edge_apis//local_agents/rag/java/com/google/ai/edge/localagents/rag/models:maven_srcs",
        "@ai_edge_apis//local_agents/rag/java/com/google/ai/edge/localagents/rag/prompt:maven_srcs",
        "@ai_edge_apis//local_agents/rag/java/com/google/ai/edge/localagents/rag/retrieval:maven_srcs",
        "@ai_edge_apis//local_agents/rag/java/com/google/ai/edge/localagents/rag/shared:maven_srcs",
    ],
    deps = [
        "//third_party:autovalue",
        "@maven//:com_google_android_android",
        "@maven//:com_google_guava_guava",
        "@maven//:com_google_mediapipe_tasks_genai",
        "@maven//:com_squareup_okhttp3_okhttp",
        "@maven//:org_checkerframework_checker_qual",
        "@maven//:org_json_json",
        "@maven//:org_jspecify_jspecify",
        "@protobuf//:protobuf_javalite",
    ],
)

cc_library(
    name = "libgecko_embedding_model_jni_lib",
    srcs = select({
        "//:android_arm64": [":rag_pipeline_android_arm64_libgecko_embedding_model_jni.so"],
        "//conditions:default": [":rag_pipeline_x86_64_libgecko_embedding_model_jni.so"],
    }),
    alwayslink = 1,
)

cc_library(
    name = "libsqlite_vector_store_jni_lib",
    srcs = select({
        "//:android_arm64": [":rag_pipeline_android_arm64_libsqlite_vector_store_jni.so"],
        "//conditions:default": [":rag_pipeline_x86_64_libsqlite_vector_store_jni.so"],
    }),
    alwayslink = 1,
)

cc_library(
    name = "libtext_chunker_jni_lib",
    srcs = select({
        "//:android_arm64": [":rag_pipeline_android_arm64_libtext_chunker_jni.so"],
        "//conditions:default": [":rag_pipeline_x86_64_libtext_chunker_jni.so"],
    }),
    alwayslink = 1,
)

android_jni_aar(
    name = "rag_jni_aar",
    native_libraries = [
        ":libgecko_embedding_model_jni_lib",
        ":libsqlite_vector_store_jni_lib",
        ":libtext_chunker_jni_lib",
    ],
    source_library = ":rag_lib",
)

# Should be build as such:
# blaze --blazerc=/dev/null build --android_platforms=//:arm64-v8a -c opt --copt=-Os --linkopt -s --strip always \
#   //local_agents/rag/java/com/google/ai/edge/localagents/rag:rag_maven_artifact \
maven_artifact(
    name = "rag_maven_artifact",
    src = "rag_jni_aar.aar",
    artifact_deps = [
        "com.google.guava:guava:33.3.1-android",
        "com.squareup.okhttp3:okhttp:4.12.0",
        "org.json:json:20250107",
    ],
    artifact_id = "localagents-rag",
    artifact_optional_deps = [
        "com.google.mediapipe:tasks-genai:(,)",
    ],
    group_id = "com.google.ai.edge.localagents",
    inception_year = "2024",
    lib_description = "The Google AI Edge RAG library.",
    lib_name = "Google AI Edge RAG",
    lib_url = "https://github.com/google-ai-edge/ai-edge-apis",
    version = RAG_SDK_VERSION,
)
