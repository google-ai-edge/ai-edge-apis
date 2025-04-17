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
        sha256 = "8fd0a838b6e3640c1aa4fb15ee9a65eae63ede268386ce05e70bbd7de2a6d019",
        urls = ["https://storage.googleapis.com/mediapipe-assets/function_calling/android_arm64/libjni_gemma_formatter_android.so?generation=1744920186934490"],
    )

    http_file(
        name = "ai_edge_apis_function_calling_android_arm64_libjni_llama_formatter_android_so",
        sha256 = "467391311598d5f550dbcbf9bbbb917bc87f8f70b8162fcc1d42c4abe70ba0fb",
        urls = ["https://storage.googleapis.com/mediapipe-assets/function_calling/android_arm64/libjni_llama_formatter_android.so?generation=1744920186941746"],
    )

    http_file(
        name = "ai_edge_apis_function_calling_android_arm64_libjni_hammer_formatter_android_so",
        sha256 = "4c1c71abd8f18f4fe1a3a732187382ff5371bd3dc573c24d8b1b011d2a56216a",
        urls = ["https://storage.googleapis.com/mediapipe-assets/function_calling/android_arm64/libjni_hammer_formatter_android.so?generation=1744920186928029"],
    )

    http_file(
        name = "ai_edge_apis_function_calling_android_arm64_libjni_fst_constraint_android_so",
        sha256 = "98f84c840b2e6bf643d7e51ec1ad4629def1405d3388b3ebd0c1d0ddd1625c5c",
        urls = ["https://storage.googleapis.com/mediapipe-assets/function_calling/android_arm64/libjni_fst_constraint_android.so?generation=1744920186954615"],
    )

    http_file(
        name = "ai_edge_apis_function_calling_x86_64_libjni_gemma_formatter_android_so",
        sha256 = "54abd4392da01918d04a3d5491f4a5b12b6a823a53e1e5130fe13f0d34af9df4",
        urls = ["https://storage.googleapis.com/mediapipe-assets/function_calling/x86_64/libjni_gemma_formatter_android.so?generation=1744920186884049"],
    )

    http_file(
        name = "ai_edge_apis_function_calling_x86_64_libjni_llama_formatter_android_so",
        sha256 = "9aa9220fc6674ddd60b4e4ae641d47722630b857b4404b3e765b9a47306d7fdf",
        urls = ["https://storage.googleapis.com/mediapipe-assets/function_calling/x86_64/libjni_llama_formatter_android.so?generation=1744920186871247"],
    )

    http_file(
        name = "ai_edge_apis_function_calling_x86_64_libjni_hammer_formatter_android_so",
        sha256 = "9ce862bddfa44031ff6074ec142bf56adc2b0f7e868dd7ae46fd833b190f87f6",
        urls = ["https://storage.googleapis.com/mediapipe-assets/function_calling/x86_64/libjni_hammer_formatter_android.so?generation=1744920186867436"],
    )

    http_file(
        name = "ai_edge_apis_function_calling_x86_64_libjni_fst_constraint_android_so",
        sha256 = "0e595bbe9836ce870e61eb27606fad7e8e01181ea7213689d34c0d7a0d0b3870",
        urls = ["https://storage.googleapis.com/mediapipe-assets/function_calling/x86_64/libjni_fst_constraint_android.so?generation=1744920187083552"],
    )
