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
        "ColumnConfig.java",
        "DefaultSemanticTextMemory.java",
        "DefaultVectorStore.java",
        "SemanticMemory.java",
        "SqliteVectorStore.java",
        "TableConfig.java",
        "VectorStore.java",
        "VectorStoreRecord.java",
    ],
)

android_library(
    name = "semantic_memory",
    srcs = [
        "SemanticMemory.java",
        "VectorStore.java",
    ],
    deps = [
        ":entities",
        "@ai_edge_apis//local_agents/rag/java/com/google/ai/edge/localagents/rag/retrieval",
        "@ai_edge_apis//local_agents/rag/java/com/google/ai/edge/localagents/rag/retrieval:entities",
        "@maven//:com_google_guava_guava",
        "@maven//:org_jspecify_jspecify",
    ],
)

android_library(
    name = "default_semantic_text_memory",
    srcs = [
        "DefaultSemanticTextMemory.java",
    ],
    deps = [
        ":entities",
        ":semantic_memory",
        "@ai_edge_apis//local_agents/rag/java/com/google/ai/edge/localagents/rag/models:embedder",
        "@ai_edge_apis//local_agents/rag/java/com/google/ai/edge/localagents/rag/models:entities",
        "@ai_edge_apis//local_agents/rag/java/com/google/ai/edge/localagents/rag/retrieval:entities",
        "@maven//:com_google_guava_guava",
    ],
)

android_library(
    name = "default_vector_store",
    srcs = [
        "DefaultVectorStore.java",
    ],
    deps = [
        ":entities",
        ":semantic_memory",
        "@ai_edge_apis//local_agents/rag/java/com/google/ai/edge/localagents/rag/shared:vector_operations",
        "@maven//:com_google_guava_guava",
        "@maven//:org_jspecify_jspecify",
    ],
)

android_library(
    name = "sqlite_vector_store",
    srcs = ["SqliteVectorStore.java"],
    deps = [
        ":entities",
        ":semantic_memory",
        "@ai_edge_apis//local_agents/rag/core/protos:memory_java_proto_lite",
        "@ai_edge_apis//local_agents/rag/core/protos:vector_stores_java_proto_lite",
        "@maven//:com_google_guava_guava",
        "@protobuf//:protobuf_javalite",
    ],
)

android_library(
    name = "entities",
    srcs = [
        "ColumnConfig.java",
        "TableConfig.java",
        "VectorStoreRecord.java",
    ],
    deps = [
        "//third_party:autovalue",
        "@maven//:com_google_guava_guava",
    ],
)
