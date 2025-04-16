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
        sha256 = "196576f1f698b7d55aa3f532e6344688ab4b7de676fd26db2a015076ab373f6a",
        urls = ["https://storage.googleapis.com/mediapipe-assets/function_calling/android_arm64/libjni_gemma_formatter_android.so?generation=1744670376194320"],
    )

    http_file(
        name = "ai_edge_apis_function_calling_android_arm64_libjni_llama_formatter_android_so",
        sha256 = "52100c5aab1ce630bc09a0dbd95bf8636aebf8802034de05a650d4cf12f2491e",
        urls = ["https://storage.googleapis.com/mediapipe-assets/function_calling/android_arm64/libjni_llama_formatter_android.so?generation=1744670376171806"],
    )

    http_file(
        name = "ai_edge_apis_function_calling_android_arm64_libjni_hammer_formatter_android_so",
        sha256 = "7739ba665bb1286acfb8629b08643db57d1df2faf54478ca09bd98d25f8c9876",
        urls = ["https://storage.googleapis.com/mediapipe-assets/function_calling/android_arm64/libjni_hammer_formatter_android.so?generation=1744670376274267"],
    )

    http_file(
        name = "ai_edge_apis_function_calling_android_arm64_libjni_fst_constraint_android_so",
        sha256 = "d2315d98dc3039b38a6bfaa8ed602b432a312de16a684f0e0887e1cf12374193",
        urls = ["https://storage.googleapis.com/mediapipe-assets/function_calling/android_arm64/libjni_fst_constraint_android.so?generation=1744670376262793"],
    )

    http_file(
        name = "ai_edge_apis_function_calling_x86_64_libjni_gemma_formatter_android_so",
        sha256 = "6a09313fee20ad48b37dfca2e2996bf5746dcf44bb92adffa3fa9694934f06c7",
        urls = ["https://storage.googleapis.com/mediapipe-assets/function_calling/x86_64/libjni_gemma_formatter_android.so?generation=1744670376311316"],
    )

    http_file(
        name = "ai_edge_apis_function_calling_x86_64_libjni_llama_formatter_android_so",
        sha256 = "414ebc87134f66aec45166c8b018a31ed63f4d88c01b1de5f6311d08f572ea16",
        urls = ["https://storage.googleapis.com/mediapipe-assets/function_calling/x86_64/libjni_llama_formatter_android.so?generation=1744670376271522"],
    )

    http_file(
        name = "ai_edge_apis_function_calling_x86_64_libjni_hammer_formatter_android_so",
        sha256 = "1c86919e0fabcdcfdc261791c98240194b8710ef90d10b6b62c440562380c919",
        urls = ["https://storage.googleapis.com/mediapipe-assets/function_calling/x86_64/libjni_hammer_formatter_android.so?generation=1744670376419386"],
    )

    http_file(
        name = "ai_edge_apis_function_calling_x86_64_libjni_fst_constraint_android_so",
        sha256 = "11271f22e03824679d6f184422254d40d8f12f58a50c675b6ca6152fe806082e",
        urls = ["https://storage.googleapis.com/mediapipe-assets/function_calling/x86_64/libjni_fst_constraint_android.so?generation=1744670376546569"],
    )
