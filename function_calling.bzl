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
        sha256 = "57b71a50dfb33aba58691866602839155933b759edcc42684e686884926158b9",
        urls = ["https://storage.googleapis.com/mediapipe-assets/function_calling/android_arm64/libjni_gemma_formatter_android.so?generation=1744306485953090"],
    )

    http_file(
        name = "ai_edge_apis_function_calling_x86_64_libjni_gemma_formatter_android_so",
        sha256 = "d3f25fd1e2a3e7614994b536651eb345a925f6a7855fec29c57b8b068b1c9baa",
        urls = ["https://storage.googleapis.com/mediapipe-assets/function_calling/x86_64/libjni_gemma_formatter_android.so?generation=1744306486061153"],
    )

    http_file(
        name = "ai_edge_apis_function_calling_android_arm64_libjni_llama_formatter_android_so",
        sha256 = "c4348f6b52f2e3df0bb05a4036de309fed662070c9d8c8a013af7d06ae8e3e8c",
        urls = ["https://storage.googleapis.com/mediapipe-assets/function_calling/android_arm64/libjni_llama_formatter_android.so?generation=1744306485965264"],
    )

    http_file(
        name = "ai_edge_apis_function_calling_x86_64_libjni_llama_formatter_android_so",
        sha256 = "3800e9802b48b6c7e9472c6bfb5618004c0af814cdc1f6cbad52d57d36e55d11",
        urls = ["https://storage.googleapis.com/mediapipe-assets/function_calling/x86_64/libjni_llama_formatter_android.so?generation=1744306486035400"],
    )

    http_file(
        name = "ai_edge_apis_function_calling_android_arm64_libjni_fst_constraint_android_so",
        sha256 = "5b72313d0f3441e22a2659e5577d15c0b24d87a87ccb4bcc226ee7d967196d58",
        urls = ["https://storage.googleapis.com/mediapipe-assets/function_calling/android_arm64/libjni_fst_constraint_android.so?generation=1744306486033832"],
    )

    http_file(
        name = "ai_edge_apis_function_calling_x86_64_libjni_fst_constraint_android_so",
        sha256 = "a83534acc4de24de100238a12fde2601e650289986429729ebbf0766b77fbe68",
        urls = ["https://storage.googleapis.com/mediapipe-assets/function_calling/x86_64/libjni_fst_constraint_android.so?generation=1744306486369401"],
    )
