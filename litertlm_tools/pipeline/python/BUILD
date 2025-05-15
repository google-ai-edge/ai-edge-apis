# Copyright 2025 The LiteRT LM Tools Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

load("@ai_edge_apis_pip_deps//:requirements.bzl", "requirement")
load("//local_agents/core/proto:build_config.bzl", "ai_edge_proto_library")

package(default_visibility = ["//visibility:public"])

ai_edge_proto_library(
    name = "llm_parameters_proto",
    srcs = ["llm_parameters.proto"],
)

py_library(
    name = "task_file_processor",
    srcs = ["task_file_processor.py"],
    deps = [
        ":llm_parameters_py_pb2",
        ":prompt_template",
    ],
)

py_library(
    name = "litertlm_lib",
    srcs = [
        "__init__.py",
        "version.py",
    ],
    deps = [
        ":pipeline",
    ],
)

py_library(
    name = "prompt_template",
    srcs = ["prompt_template.py"],
)

py_library(
    name = "pipeline",
    srcs = ["pipeline.py"],
    deps = [
        ":model_downloader",
        ":prompt_template",
        ":task_file_processor",
        ":tokenizer",
        requirement("numpy"),
        requirement("transformers"),
        requirement("sentencepiece"),
        requirement("ai-edge-litert"),
    ],
)

py_library(
    name = "tokenizer",
    srcs = ["tokenizer.py"],
    deps = [
        ":prompt_template",
        requirement("sentencepiece"),
    ],
)

py_library(
    name = "model_downloader",
    srcs = ["model_downloader.py"],
    deps = [
        requirement("huggingface_hub"),
    ],
)
