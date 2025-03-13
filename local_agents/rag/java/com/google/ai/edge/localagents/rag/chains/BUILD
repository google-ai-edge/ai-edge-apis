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
        "Chain.java",
        "ChainConfig.java",
        "RetrievalAndInferenceChain.java",
        "RetrievalChain.java",
    ],
)

android_library(
    name = "chain",
    srcs = [
        "Chain.java",
    ],
    deps = [
        "@ai_edge_apis//local_agents/rag/java/com/google/ai/edge/localagents/rag/models:language_model",
        "@maven//:com_google_guava_guava",
        "@maven//:org_jspecify_jspecify",
    ],
)

android_library(
    name = "config",
    srcs = [
        "ChainConfig.java",
    ],
    deps = [
        "//third_party:autovalue",
        "@ai_edge_apis//local_agents/rag/java/com/google/ai/edge/localagents/rag/memory:semantic_memory",
        "@ai_edge_apis//local_agents/rag/java/com/google/ai/edge/localagents/rag/models:language_model",
        "@ai_edge_apis//local_agents/rag/java/com/google/ai/edge/localagents/rag/prompt:prompt_builder",
        "@maven//:androidx_annotation_annotation",
        "@maven//:org_checkerframework_checker_qual",
    ],
)

android_library(
    name = "retrieval_and_inference_chain",
    srcs = [
        "RetrievalAndInferenceChain.java",
    ],
    deps = [
        ":chain",
        ":config",
        "@ai_edge_apis//local_agents/rag/core/protos:retrieval_java_proto_lite",
        "@ai_edge_apis//local_agents/rag/java/com/google/ai/edge/localagents/rag/memory:semantic_memory",
        "@ai_edge_apis//local_agents/rag/java/com/google/ai/edge/localagents/rag/models:language_model",
        "@ai_edge_apis//local_agents/rag/java/com/google/ai/edge/localagents/rag/retrieval:entities",
        "@maven//:androidx_annotation_annotation",
        "@maven//:com_google_guava_guava",
        "@maven//:org_jspecify_jspecify",
    ],
)

android_library(
    name = "retrieval_chain",
    srcs = [
        "RetrievalChain.java",
    ],
    deps = [
        ":chain",
        ":config",
        "@ai_edge_apis//local_agents/rag/java/com/google/ai/edge/localagents/rag/memory:semantic_memory",
        "@ai_edge_apis//local_agents/rag/java/com/google/ai/edge/localagents/rag/models:language_model",
        "@ai_edge_apis//local_agents/rag/java/com/google/ai/edge/localagents/rag/retrieval:entities",
        "@maven//:androidx_annotation_annotation",
        "@maven//:com_google_guava_guava",
        "@maven//:org_checkerframework_checker_qual",
        "@maven//:org_jspecify_jspecify",
    ],
)
