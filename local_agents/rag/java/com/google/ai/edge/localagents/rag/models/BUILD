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

filegroup(
    name = "maven_srcs",
    srcs = [
        "AsyncProgressListener.java",
        "EmbedData.java",
        "Embedder.java",
        "EmbeddingRequest.java",
        "GeckoEmbeddingModel.java",
        "GeminiEmbedder.java",
        "LanguageModel.java",
        "LanguageModelRequest.java",
        "LanguageModelResponse.java",
        "MediaPipeLlmBackend.java",
    ],
)

android_library(
    name = "language_model",
    srcs = [
        "AsyncProgressListener.java",
        "LanguageModel.java",
        "LanguageModelRequest.java",
        "LanguageModelResponse.java",
    ],
    deps = [
        "//third_party:autovalue",
        "@maven//:com_google_guava_guava",
        "@maven//:org_jspecify_jspecify",
    ],
)

android_library(
    name = "embedder",
    srcs = [
        "Embedder.java",
    ],
    deps = [
        ":entities",
        "@maven//:com_google_guava_guava",
    ],
)

android_library(
    name = "mediapipe_llm_backend",
    srcs = ["MediaPipeLlmBackend.java"],
    deps = [
        ":language_model",
        "@maven//:com_google_android_android",
        "@maven//:com_google_guava_guava",
        "@maven//:com_google_mediapipe_tasks_genai",
        "@maven//:org_checkerframework_checker_qual",
        "@maven//:org_jspecify_jspecify",
    ],
)

android_library(
    name = "gecko_embedding_model",
    srcs = ["GeckoEmbeddingModel.java"],
    deps = [
        ":embedder",
        ":entities",
        "@ai_edge_apis//local_agents/rag/core/protos:embedding_models_java_proto_lite",
        "@maven//:com_google_guava_guava",
    ],
)

android_library(
    name = "gemini_embedder",
    srcs = ["GeminiEmbedder.java"],
    deps = [
        ":embedder",
        ":entities",
        "@maven//:com_google_android_android",
        "@maven//:com_google_guava_guava",
        "@maven//:com_squareup_okhttp3_okhttp",
        "@maven//:org_checkerframework_checker_qual",
        "@maven//:org_json_json",
    ],
)

android_library(
    name = "entities",
    srcs = [
        "EmbedData.java",
        "EmbeddingRequest.java",
    ],
    deps = [
        "//third_party:autovalue",
        "@maven//:com_google_guava_guava",
        "@maven//:org_checkerframework_checker_qual",
    ],
)
