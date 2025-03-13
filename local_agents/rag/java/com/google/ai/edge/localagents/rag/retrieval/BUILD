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
        "BaseRetriever.java",
        "RetrievalConfig.java",
        "RetrievalEntity.java",
        "RetrievalRequest.java",
        "RetrievalResponse.java",
        "SemanticDataEntry.java",
    ],
)

android_library(
    name = "retrieval",
    srcs = [
        "BaseRetriever.java",
    ],
    deps = [
        ":entities",
        "@maven//:androidx_annotation_annotation",
        "@maven//:com_google_guava_guava",
    ],
)

android_library(
    name = "entities",
    srcs = [
        "RetrievalConfig.java",
        "RetrievalEntity.java",
        "RetrievalRequest.java",
        "RetrievalResponse.java",
        "SemanticDataEntry.java",
    ],
    deps = [
        "//third_party:autovalue",
        "@maven//:com_google_guava_guava",
    ],
)
