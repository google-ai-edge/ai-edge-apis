"""Static files for the ai_edge_apis module."""

load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive", "http_jar")
load("//:function_calling.bzl", "function_calling_files")
load("//:rag_pipeline.bzl", "rag_pipeline_files")

def _non_module_dependencies_impl(_ctx):
    rag_pipeline_files()
    function_calling_files()

non_module_dependencies = module_extension(
    implementation = _non_module_dependencies_impl,
)

def _http_archive_impl(_ctx):
    http_archive(
        name = "rules_antlr",
        sha256 = "26e6a83c665cf6c1093b628b3a749071322f0f70305d12ede30909695ed85591",
        strip_prefix = "rules_antlr-0.5.0",
        urls = ["https://github.com/marcohu/rules_antlr/archive/0.5.0.tar.gz"],
    )

    http_archive(
        name = "antlr4",
        sha256 = "4d0714f441333a63e50031c9e8e4890c78f3d21e053d46416949803e122a6574",
        strip_prefix = "antlr4-4.7.1",
        urls = ["https://github.com/antlr/antlr4/archive/4.7.1.tar.gz"],
        build_file_content = """
cc_library(
    name = "cpp",
    srcs = glob(["runtime/Cpp/runtime/src/**/*.cpp"]),
    hdrs = glob(["runtime/Cpp/runtime/src/**/*.h"]),
    includes = ["runtime/Cpp/runtime/src"],
    visibility = ["//visibility:public"],
)
""",
    )

http_archive_dependencies = module_extension(
    implementation = _http_archive_impl,
)

def _http_jar_impl(_ctx):
    http_jar(
        name = "antlr4_tool",
        url = "https://jcenter.bintray.com/org/antlr/antlr4/4.7/antlr4-4.7.jar",
        sha256 = "7867257028b3373af011dee7b6ce9b587a8fd5c7a0b25f68b2ff4cb90be8aa07",
    )

    http_jar(
        name = "javax_json",
        url = "https://jcenter.bintray.com/org/glassfish/javax.json/1.0.4/javax.json-1.0.4.jar",
        sha256 = "0e1dec40a1ede965941251eda968aeee052cc4f50378bc316cc48e8159bdbeb4",
    )

    http_jar(
        name = "stringtemplate4",
        url = "https://jcenter.bintray.com/org/antlr/ST4/4.0.8/ST4-4.0.8.jar",
        sha256 = "58caabc40c9f74b0b5993fd868e0f64a50c0759094e6a251aaafad98edfc7a3b",
    )

    http_jar(
        name = "antlr3_runtime",
        url = "https://jcenter.bintray.com/org/antlr/antlr-runtime/3.5.2/antlr-runtime-3.5.2.jar",
        sha256 = "ce3fc8ecb10f39e9a3cddcbb2ce350d272d9cd3d0b1e18e6fe73c3b9389c8734",
    )

    http_jar(
        name = "antlr4_runtime",
        url = "https://repo1.maven.org/maven2/org/antlr/antlr4-runtime/4.7.1/antlr4-runtime-4.7.1.jar",
        sha256 = "43516d19beae35909e04d06af6c0c58c17bc94e0070c85e8dc9929ca640dc91d",
    )

http_jar_dependencies = module_extension(
    implementation = _http_jar_impl,
)
