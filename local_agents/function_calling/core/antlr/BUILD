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

load("@rules_antlr//antlr:antlr4.bzl", "antlr")

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
    name = "parser_utils",
    srcs = ["parser_utils.cc"],
    hdrs = ["parser_utils.h"],
    deps = [
        ":antlr_generated_lib",
        "//local_agents/core/proto:content_cc_proto",
        "//local_agents/core/proto:generative_service_cc_proto",
        "@abseil-cpp//absl/log:absl_check",
        "@abseil-cpp//absl/log:absl_log",
        "@abseil-cpp//absl/log:check",
        "@abseil-cpp//absl/status",
        "@abseil-cpp//absl/status:statusor",
        "@abseil-cpp//absl/strings",
        "@abseil-cpp//absl/strings:string_view",
        "@protobuf//:struct_cc_proto",
        "@re2",
    ],
)

antlr(
    name = "antlr_json_function_call_parser",
    srcs = [
        "AntlrJsonLexer.g4",
        "AntlrJsonParser.g4",
    ],
    language = "Cpp",
    listener = True,
)

antlr(
    name = "antlr_python_function_call_parser",
    srcs = [
        "AntlrPythonLexer.g4",
        "AntlrPythonParser.g4",
    ],
    language = "Cpp",
    listener = True,
)

cc_library(
    name = "antlr_generated_lib",
    srcs = [
        ":antlr_json_function_call_parser",
        ":antlr_python_function_call_parser",
    ],
    visibility = ["//visibility:public"],
    deps = [
        ":antlr_json_function_call_parser",
        ":antlr_python_function_call_parser",
        "@antlr4//:cpp",
    ],
)
