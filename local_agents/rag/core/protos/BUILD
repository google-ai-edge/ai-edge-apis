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

load("@ai_edge_apis//local_agents/rag/maven:maven_repository.bzl", "java_proto_lite_srcs")
load("//local_agents/core/proto:build_config.bzl", "ai_edge_proto_library")

package(default_visibility = [
    ":default_visibility",
])

package_group(
    name = "default_visibility",
    packages = [
        "//local_agents/...",
    ],
)

ai_edge_proto_library(
    name = "language_models_proto",
    srcs = ["language_models.proto"],
)

ai_edge_proto_library(
    name = "embedding_models_proto",
    srcs = ["embedding_models.proto"],
)

java_proto_lite_srcs(
    name = "embedding_models_java_proto_lite_srcs",
    jar = ":embedding_models_java_proto_lite",
    package_root = "com.google.ai.edge.localagents.rag.models.proto",
    proto_files = [
        "TextEmbeddingRequest.java",
        "TextEmbeddingRequestOrBuilder.java",
        "EmbeddingModels.java",
        "EmbedTextOrBuilder.java",
        "EmbedText.java",
    ],
)

ai_edge_proto_library(
    name = "retrieval_proto",
    srcs = ["retrieval.proto"],
    deps = [":memory_proto"],
)

ai_edge_proto_library(
    name = "memory_proto",
    srcs = ["memory.proto"],
)

java_proto_lite_srcs(
    name = "memory_java_proto_lite_srcs",
    jar = ":memory_java_proto_lite",
    package_root = "com.google.ai.edge.localagents.rag.memory.proto",
    proto_files = [
        "KeyValuePair.java",
        "KeyValuePairOrBuilder.java",
        "Memory.java",
        "MemoryEntry.java",
        "MemoryEntryOrBuilder.java",
        "MemoryRecord.java",
        "MemoryRecordOrBuilder.java",
        "Metadata.java",
        "MetadataOrBuilder.java",
    ],
)

ai_edge_proto_library(
    name = "vector_stores_proto",
    srcs = ["vector_stores.proto"],
)

java_proto_lite_srcs(
    name = "vector_stores_java_proto_lite_srcs",
    jar = ":vector_stores_java_proto_lite",
    package_root = "com.google.ai.edge.localagents.rag.memory.proto",
    proto_files = [
        "TableConfig.java",
        "TableConfigOrBuilder.java",
        "VectorStores.java",
    ],
)
