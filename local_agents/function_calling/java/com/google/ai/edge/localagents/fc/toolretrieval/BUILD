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
    "//local_agents/function_calling/java/com/google/ai/edge/localagents/fc:default_visibility",
])

android_library(
    name = "tool_retrieval",
    srcs = ["ToolRetrieval.java"],
    deps = [
        ":tool_metadata",
        "//local_agents/core/proto:content_java_proto_lite",
        "@maven//:com_google_guava_guava",
    ],
)

android_library(
    name = "tool_metadata",
    srcs = ["ToolMetadata.java"],
    deps = [
        "@maven//:com_google_errorprone_error_prone_annotations",
        "@maven//:com_google_guava_guava",
    ],
)

android_library(
    name = "tool_formatter",
    srcs = ["ToolFormatter.java"],
    deps = [
        ":tool_metadata",
        "//local_agents/core/proto:content_java_proto_lite",
        "@ai_edge_apis//local_agents/rag/java/com/google/ai/edge/localagents/rag/retrieval:entities",
        "@maven//:com_google_guava_guava",
    ],
)

android_library(
    name = "default_tool_formatter",
    srcs = ["DefaultToolFormatter.java"],
    deps = [
        ":tool_formatter",
        ":tool_metadata",
        "//local_agents/core/proto:content_java_proto_lite",
        "@ai_edge_apis//local_agents/rag/java/com/google/ai/edge/localagents/rag/retrieval:entities",
        "@maven//:com_google_guava_guava",
    ],
)

android_library(
    name = "default_tool_retrieval_client",
    srcs = ["DefaultToolRetrievalClient.java"],
    deps = [
        "tool_formatter",
        ":tool_metadata",
        ":tool_retrieval",
        "//local_agents/core/proto:content_java_proto_lite",
        "@ai_edge_apis//local_agents/rag/java/com/google/ai/edge/localagents/rag/memory:semantic_memory",
        "@ai_edge_apis//local_agents/rag/java/com/google/ai/edge/localagents/rag/retrieval:entities",
        "@maven//:com_google_guava_guava",
    ],
)

filegroup(
    name = "maven_srcs",
    srcs = glob(["*.java"]),
)
