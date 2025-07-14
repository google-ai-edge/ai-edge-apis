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

load("//third_party/bazel_rules/rules_cc/cc:cc_library.bzl", "cc_library")

package(default_visibility = [
    ":default_visibility",
])

package_group(
    name = "default_visibility",
    packages = [
        "//local_agents/...",
    ],
)

cc_library(
    name = "base_language_model",
    hdrs = ["base_language_model.h"],
    deps = [
        "@abseil-cpp//absl/status",
        "@abseil-cpp//absl/status:statusor",
        "@ai_edge_apis//local_agents/rag/core/protos:language_models_cc_proto",
    ],
)

cc_library(
    name = "base_text_embedding_model",
    hdrs = ["base_text_embedding_model.h"],
    deps = [
        "@abseil-cpp//absl/status:statusor",
        "@abseil-cpp//absl/strings:string_view",
        "@abseil-cpp//absl/types:span",
        "@ai_edge_apis//local_agents/rag/core/protos:embedding_models_cc_proto",
    ],
)
