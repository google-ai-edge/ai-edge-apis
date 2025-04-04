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

load("//devtools/python/blaze:strict.bzl", "py_strict_binary", "py_strict_library")

package(default_visibility = [
    ":default_visibility",
])

package_group(
    name = "default_visibility",
    packages = [
        "//third_party/odml/...",
    ],
)

py_strict_library(
    name = "litertlm_lib",
    srcs = [
        "__init__.py",
        "version.py",
    ],
    deps = [
        ":pipeline",
    ],
)

py_strict_library(
    name = "pipeline",
    srcs = ["pipeline.py"],
    deps = [
        ":model_downloader",
        ":tokenizer",
        "//third_party/sentencepiece/src/python:sentencepiece_processor",
        "//third_party/tensorflow/lite/python:interpreter",
        "@litertlm_tools_pip_deps_numpy//:pkg",
        "@litertlm_tools_pip_deps_transformers//:pkg",
    ],
)

py_strict_library(
    name = "tokenizer",
    srcs = ["tokenizer.py"],
    deps = [
        "//third_party/sentencepiece/src/python:sentencepiece_processor",
    ],
)

py_strict_library(
    name = "model_downloader",
    srcs = ["model_downloader.py"],
    deps = [
        "@litertlm_tools_pip_deps_huggingface_hub//:pkg",
    ],
)
