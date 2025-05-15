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
    name = "format_utils",
    srcs = ["format_utils.cc"],
    hdrs = ["format_utils.h"],
    deps = [
        "//local_agents/core/proto:content_cc_proto",
        "//local_agents/core/proto:generative_service_cc_proto",
        "@abseil-cpp//absl/container:flat_hash_set",
        "@abseil-cpp//absl/status:statusor",
        "@abseil-cpp//absl/strings",
        "@abseil-cpp//absl/strings:string_view",
        "@protobuf//:struct_cc_proto",
    ],
)

cc_library(
    name = "gemma_formatter",
    srcs = ["gemma_formatter.cc"],
    hdrs = ["gemma_formatter.h"],
    deps = [
        ":format_utils",
        "//local_agents/core/proto:content_cc_proto",
        "//local_agents/core/proto:generative_service_cc_proto",
        "//local_agents/function_calling/core/antlr:parser_utils",
        "//local_agents/function_calling/core/proto:model_formatter_options_cc_proto",
        "@abseil-cpp//absl/log:check",
        "@abseil-cpp//absl/status",
        "@abseil-cpp//absl/status:statusor",
        "@abseil-cpp//absl/strings",
        "@abseil-cpp//absl/strings:string_view",
        "@abseil-cpp//absl/types:span",
        "@protobuf//:struct_cc_proto",
    ],
)

cc_library(
    name = "llama_formatter",
    srcs = ["llama_formatter.cc"],
    hdrs = ["llama_formatter.h"],
    deps = [
        ":format_utils",
        "//local_agents/core/proto:content_cc_proto",
        "//local_agents/core/proto:generative_service_cc_proto",
        "//local_agents/function_calling/core/antlr:parser_utils",
        "//local_agents/function_calling/core/proto:model_formatter_options_cc_proto",
        "@abseil-cpp//absl/status",
        "@abseil-cpp//absl/status:statusor",
        "@abseil-cpp//absl/strings",
        "@abseil-cpp//absl/strings:string_view",
        "@abseil-cpp//absl/types:span",
        "@re2",
    ],
)

cc_library(
    name = "hammer_formatter",
    srcs = ["hammer_formatter.cc"],
    hdrs = ["hammer_formatter.h"],
    deps = [
        ":format_utils",
        "//local_agents/core/proto:content_cc_proto",
        "//local_agents/core/proto:generative_service_cc_proto",
        "//local_agents/function_calling/core/antlr:parser_utils",
        "//local_agents/function_calling/core/proto:model_formatter_options_cc_proto",
        "@abseil-cpp//absl/log:absl_log",
        "@abseil-cpp//absl/status",
        "@abseil-cpp//absl/status:statusor",
        "@abseil-cpp//absl/strings",
        "@abseil-cpp//absl/strings:str_format",
        "@abseil-cpp//absl/strings:string_view",
        "@abseil-cpp//absl/types:span",
        "@re2",
    ],
)
