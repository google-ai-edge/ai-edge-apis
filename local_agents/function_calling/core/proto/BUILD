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
    name = "constraint_options_proto",
    srcs = ["constraint_options.proto"],
)

java_proto_lite_srcs(
    name = "constraint_options_java_proto_lite_srcs",
    jar = ":constraint_options_java_proto_lite",
    package_root = "com.google.ai.edge.localagents.fc.proto",
    proto_files = [
        "ConstraintOptions.java",
        "ConstraintOptionsOrBuilder.java",
    ],
)

java_proto_lite_srcs(
    name = "model_formatter_options_java_proto_lite_srcs",
    jar = ":model_formatter_options_java_proto_lite",
    package_root = "com.google.ai.edge.localagents.fc.proto",
    proto_files = [
        "ModelFormatterOptions.java",
        "ModelFormatterOptionsOrBuilder.java",
    ],
)

java_proto_lite_srcs(
    name = "generative_service_java_proto_lite_srcs",
    jar = "//local_agents/core/proto:generative_service_java_proto_lite",
    package_root = "com.google.ai.edge.localagents.core.proto",
    proto_files = [
        "Candidate.java",
        "CandidateOrBuilder.java",
        "GenerateContentResponse.java",
        "GenerateContentResponseOrBuilder.java",
        "GenerateContentRequest.java",
        "GenerateContentRequestOrBuilder.java",
    ],
)

java_proto_lite_srcs(
    name = "content_java_proto_lite_srcs",
    jar = "//local_agents/core/proto:content_java_proto_lite",
    package_root = "com.google.ai.edge.localagents.core.proto",
    proto_files = [
        "Content.java",
        "ContentOrBuilder.java",
        "FunctionDeclaration.java",
        "FunctionDeclarationOrBuilder.java",
        "Tool.java",
        "ToolOrBuilder.java",
        "Part.java",
        "PartOrBuilder.java",
        "FunctionCall.java",
        "FunctionCallOrBuilder.java",
        "FunctionResponse.java",
        "FunctionResponseOrBuilder.java",
        "Schema.java",
        "SchemaOrBuilder.java",
        "Type.java",
    ],
)

ai_edge_proto_library(
    name = "model_formatter_options_proto",
    srcs = ["model_formatter_options.proto"],
)
