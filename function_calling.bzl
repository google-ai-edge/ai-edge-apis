"""
Pre-compiled static libraries for AI Edge's function calling SDK.

This file is auto-generated.
"""

load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_file")

# buildifier: disable=unnamed-macro
def function_calling_files():
    """Pre-compiled static libraries for AI Edge's function calling SDK."""

    http_file(
        name = "ai_edge_apis_function_calling_android_arm64_libjni_gemma_formatter_android_so",
        sha256 = "a563323e17c6b2bdbe78f3e14cd6d709b853eebf2f752b1fd1dd88e68033a554",
        urls = ["https://storage.googleapis.com/mediapipe-assets/function_calling/android_arm64/libjni_gemma_formatter_android.so?generation=1747334331724448"],
    )

    http_file(
        name = "ai_edge_apis_function_calling_android_arm64_libjni_llama_formatter_android_so",
        sha256 = "a8a35a3f74add0d8bcbeb503c860e747af2b238b5a2011a13e876e1c9b0193d8",
        urls = ["https://storage.googleapis.com/mediapipe-assets/function_calling/android_arm64/libjni_llama_formatter_android.so?generation=1747334331730804"],
    )

    http_file(
        name = "ai_edge_apis_function_calling_android_arm64_libjni_hammer_formatter_android_so",
        sha256 = "5257c03430f08c2edf911a51697ba372464671bdfe87f4cf4ef904093c492d89",
        urls = ["https://storage.googleapis.com/mediapipe-assets/function_calling/android_arm64/libjni_hammer_formatter_android.so?generation=1747334331734668"],
    )

    http_file(
        name = "ai_edge_apis_function_calling_android_arm64_libjni_fst_constraint_android_so",
        sha256 = "1939f67b69ae7ac76165a84256118d1b2f7dafe0e97760372fe9003383af3bbb",
        urls = ["https://storage.googleapis.com/mediapipe-assets/function_calling/android_arm64/libjni_fst_constraint_android.so?generation=1747334331724825"],
    )

    http_file(
        name = "ai_edge_apis_function_calling_x86_64_libjni_gemma_formatter_android_so",
        sha256 = "cd33e43dcfa60d690a76bff013c6d96f8d3e937f6f5d155e338909f4ebf2da6e",
        urls = ["https://storage.googleapis.com/mediapipe-assets/function_calling/x86_64/libjni_gemma_formatter_android.so?generation=1747334331748783"],
    )

    http_file(
        name = "ai_edge_apis_function_calling_x86_64_libjni_llama_formatter_android_so",
        sha256 = "ad0c82c2473f327adbb10d5f203a1f351550ca3da0406692f356feff5271c713",
        urls = ["https://storage.googleapis.com/mediapipe-assets/function_calling/x86_64/libjni_llama_formatter_android.so?generation=1747334331769484"],
    )

    http_file(
        name = "ai_edge_apis_function_calling_x86_64_libjni_hammer_formatter_android_so",
        sha256 = "0f529bdef5212a7e3991c1cd0dfe3ecbf911ff7f3bee4ac67e89ca2ceaa48a7b",
        urls = ["https://storage.googleapis.com/mediapipe-assets/function_calling/x86_64/libjni_hammer_formatter_android.so?generation=1747334331757450"],
    )

    http_file(
        name = "ai_edge_apis_function_calling_x86_64_libjni_fst_constraint_android_so",
        sha256 = "6f24abcbb7d3578d9892d032a5ab697809cd00c9ec2d4ace8759da2613ce0fac",
        urls = ["https://storage.googleapis.com/mediapipe-assets/function_calling/x86_64/libjni_fst_constraint_android.so?generation=1747334331992578"],
    )
