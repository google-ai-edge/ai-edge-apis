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

load("@rules_jni//jni:cc_jni_library.bzl", "cc_jni_library")
load("//third_party:ai_edge_files.bzl", "ai_edge_files")

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
    name = "jni_utils",
    srcs = ["jni_utils.cc"],
    hdrs = ["jni_utils.h"],
    deps = [
        "//local_agents/core/proto:content_cc_proto",
        "//local_agents/core/proto:generative_service_cc_proto",
        "//local_agents/function_calling/core/proto:model_formatter_options_cc_proto",
        "@abseil-cpp//absl/log:check",
        "@abseil-cpp//absl/status",
        "@abseil-cpp//absl/status:statusor",
        "@abseil-cpp//absl/strings",
        "@abseil-cpp//absl/strings:string_view",
        "@rules_jni//jni",
    ],
)

cc_library(
    name = "jni_gemma_formatter",
    srcs = ["jni_gemma_formatter.cc"],
    deps = [
        ":jni_utils",
        "//local_agents/core/proto:content_cc_proto",
        "//local_agents/core/proto:generative_service_cc_proto",
        "//local_agents/function_calling/core:gemma_formatter",
        "//local_agents/function_calling/core/proto:model_formatter_options_cc_proto",
        "@abseil-cpp//absl/status:statusor",
        "@rules_jni//jni",
    ],
)

cc_jni_library(
    name = "jni_gemma_formatter_android",
    srcs = [
        "jni_gemma_formatter.cc",
    ],
    linkopts = ["-Wl,--strip-all"],
    deps = [
        ":jni_utils",
        "//local_agents/core/proto:content_cc_proto",
        "//local_agents/core/proto:generative_service_cc_proto",
        "//local_agents/function_calling/core:gemma_formatter",
        "//local_agents/function_calling/core/proto:model_formatter_options_cc_proto",
        "@abseil-cpp//absl/status:statusor",
    ],
)

cc_library(
    name = "jni_llama_formatter",
    srcs = ["jni_llama_formatter.cc"],
    deps = [
        ":jni_utils",
        "//local_agents/core/proto:content_cc_proto",
        "//local_agents/core/proto:generative_service_cc_proto",
        "//local_agents/function_calling/core:llama_formatter",
        "//local_agents/function_calling/core/proto:model_formatter_options_cc_proto",
        "@abseil-cpp//absl/status:statusor",
        "@rules_jni//jni",
    ],
)

cc_jni_library(
    name = "jni_llama_formatter_android",
    srcs = ["jni_llama_formatter.cc"],
    linkopts = ["-Wl,--strip-all"],
    deps = [
        ":jni_utils",
        "//local_agents/core/proto:content_cc_proto",
        "//local_agents/core/proto:generative_service_cc_proto",
        "//local_agents/function_calling/core:llama_formatter",
        "//local_agents/function_calling/core/proto:model_formatter_options_cc_proto",
        "@abseil-cpp//absl/status:statusor",
    ],
)

cc_library(
    name = "jni_hammer_formatter",
    srcs = ["jni_hammer_formatter.cc"],
    deps = [
        ":jni_utils",
        "//local_agents/core/proto:content_cc_proto",
        "//local_agents/core/proto:generative_service_cc_proto",
        "//local_agents/function_calling/core:hammer_formatter",
        "//local_agents/function_calling/core/proto:model_formatter_options_cc_proto",
        "@abseil-cpp//absl/status:statusor",
        "@rules_jni//jni",
    ],
)

cc_jni_library(
    name = "jni_hammer_formatter_android",
    srcs = ["jni_hammer_formatter.cc"],
    linkopts = ["-Wl,--strip-all"],
    deps = [
        ":jni_utils",
        "//local_agents/core/proto:content_cc_proto",
        "//local_agents/core/proto:generative_service_cc_proto",
        "//local_agents/function_calling/core:hammer_formatter",
        "//local_agents/function_calling/core/proto:model_formatter_options_cc_proto",
        "@abseil-cpp//absl/status:statusor",
    ],
)

cc_library(
    name = "jni_fst_constraint_android",
    srcs = select({
        "//:android_arm64": [":function_calling_android_arm64_libjni_fst_constraint_android.so"],
        "//conditions:default": [":function_calling_x86_64_libjni_fst_constraint_android.so"],
    }),
    alwayslink = 1,
)

# External targets

ai_edge_files(
    srcs = [
        "function_calling_android_arm64_libjni_fst_constraint_android.so",
        "function_calling_android_arm64_libjni_gemma_formatter_android.so",
        "function_calling_android_arm64_libjni_hammer_formatter_android.so",
        "function_calling_android_arm64_libjni_llama_formatter_android.so",
        "function_calling_x86_64_libjni_fst_constraint_android.so",
        "function_calling_x86_64_libjni_gemma_formatter_android.so",
        "function_calling_x86_64_libjni_hammer_formatter_android.so",
        "function_calling_x86_64_libjni_llama_formatter_android.so",
    ],
)
