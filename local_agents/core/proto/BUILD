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
    name = "content_proto",
    srcs = ["content.proto"],
    deps = [
        "@protobuf//:struct_proto",
    ],
)

ai_edge_proto_library(
    name = "generative_service_proto",
    srcs = ["generative_service.proto"],
    deps = [":content_proto"],
)
