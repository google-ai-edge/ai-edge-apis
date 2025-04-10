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
        sha256 = "05ff0c84d7d85548d8002acd96d4e25b01f9dbd1aab3465253c96f63ab46610a",
        urls = ["https://storage.googleapis.com/mediapipe-assets/function_calling/android_arm64/libjni_gemma_formatter_android.so?generation=1744239171603919"],
    )

    http_file(
        name = "ai_edge_apis_function_calling_x86_64_libjni_gemma_formatter_android_so",
        sha256 = "24663568de58392dbf007d61d76875e5a34fc891b6b987f68ef40e3641a63535",
        urls = ["https://storage.googleapis.com/mediapipe-assets/function_calling/x86_64/libjni_gemma_formatter_android.so?generation=1744239171716834"],
    )

    http_file(
        name = "ai_edge_apis_function_calling_android_arm64_libjni_llama_formatter_android_so",
        sha256 = "cf54b63814fe063d5a9a498c3f43f5685181552e8ed89b9b8194336f8eff0163",
        urls = ["https://storage.googleapis.com/mediapipe-assets/function_calling/android_arm64/libjni_llama_formatter_android.so?generation=1744239171661359"],
    )

    http_file(
        name = "ai_edge_apis_function_calling_x86_64_libjni_llama_formatter_android_so",
        sha256 = "58f28cef72fe43d080fbb50108978433952422dc157af8bc6d7e2d5b26b70775",
        urls = ["https://storage.googleapis.com/mediapipe-assets/function_calling/x86_64/libjni_llama_formatter_android.so?generation=1744239171741345"],
    )

    http_file(
        name = "ai_edge_apis_function_calling_android_arm64_libjni_fst_constraint_android_so",
        sha256 = "9916be20ff2fc981380d540f4d3f026109ba33ba6f1fa2f6719cd4f3dd8ec0fa",
        urls = ["https://storage.googleapis.com/mediapipe-assets/function_calling/android_arm64/libjni_fst_constraint_android.so?generation=1744239171675235"],
    )

    http_file(
        name = "ai_edge_apis_function_calling_x86_64_libjni_fst_constraint_android_so",
        sha256 = "0e2799a5aa4e2854435ac4e4ec852c80049c37a4fc1d2f4e9323f30098d7f397",
        urls = ["https://storage.googleapis.com/mediapipe-assets/function_calling/x86_64/libjni_fst_constraint_android.so?generation=1744239171945388"],
    )
