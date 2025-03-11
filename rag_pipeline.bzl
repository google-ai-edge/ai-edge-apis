"""
Pre-compiled static libraries for AI Edge's RAG pipeline.

This file is auto-generated.
"""

load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_file")

# buildifier: disable=unnamed-macro
def rag_pipeline_files():
    """Pre-compiled static libraries for AI Edge's RAG pipeline."""

    http_file(
        name = "ai_edge_apis_rag_pipeline_x86_64_libtext_chunker_jni_so",
        sha256 = "caccb3265e40ea44f3859a9c02426d5325ff0d77836dabfe874753c69e3b2984",
        urls = ["https://storage.googleapis.com/mediapipe-assets/rag_pipeline/x86_64/libtext_chunker_jni.so?generation=1738795222988903"],
    )

    http_file(
        name = "ai_edge_apis_rag_pipeline_android_arm64_libtext_chunker_jni_so",
        sha256 = "0ef76176519e564075ceae2aa950339f742aba3a518dc0ae67abbcb73b4fff7f",
        urls = ["https://storage.googleapis.com/mediapipe-assets/rag_pipeline/android_arm64/libtext_chunker_jni.so?generation=1738795222900208"],
    )

    http_file(
        name = "ai_edge_apis_rag_pipeline_x86_64_libsqlite_vector_store_jni_so",
        sha256 = "937a333d0780bf34387068c3a86c8d499209975dc6289288277ca0a96e6d6dfd",
        urls = ["https://storage.googleapis.com/mediapipe-assets/rag_pipeline/x86_64/libsqlite_vector_store_jni.so?generation=1738795222761940"],
    )

    http_file(
        name = "ai_edge_apis_rag_pipeline_android_arm64_libsqlite_vector_store_jni_so",
        sha256 = "751a2b43b9c7c3c78d2b70b3b8236e8cc5eed45193710ee4ac36fd3cd96cce84",
        urls = ["https://storage.googleapis.com/mediapipe-assets/rag_pipeline/android_arm64/libsqlite_vector_store_jni.so?generation=1738795222760405"],
    )

    http_file(
        name = "ai_edge_apis_rag_pipeline_x86_64_libgecko_embedding_model_jni_so",
        sha256 = "b75a838fcddb3fdb6b6dc5b1d2508a0e78811288c1437a66ba3098579bb6289d",
        urls = ["https://storage.googleapis.com/mediapipe-assets/rag_pipeline/x86_64/libgecko_embedding_model_jni.so?generation=1738795223171264"],
    )

    http_file(
        name = "ai_edge_apis_rag_pipeline_android_arm64_libgecko_embedding_model_jni_so",
        sha256 = "d7ca28c2e995188b1d1d80b24f687655ed7de4b51bd49af81510b300eb0a48e0",
        urls = ["https://storage.googleapis.com/mediapipe-assets/rag_pipeline/android_arm64/libgecko_embedding_model_jni.so?generation=1738795222914389"],
    )
