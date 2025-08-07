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
        sha256 = "6c8420f7bb5347d002982332f6d649904f600baabe0317bc7d4641da1898741d",
        urls = ["https://storage.googleapis.com/mediapipe-assets/rag_pipeline/x86_64/libtext_chunker_jni.so?generation=1754586489020324"],
    )

    http_file(
        name = "ai_edge_apis_rag_pipeline_android_arm64_libtext_chunker_jni_so",
        sha256 = "f047ccffebfc04a2ba878e821e7e99bb19b15c02533c25a8d1b9ecfe0120b9e9",
        urls = ["https://storage.googleapis.com/mediapipe-assets/rag_pipeline/android_arm64/libtext_chunker_jni.so?generation=1754586489410465"],
    )

    http_file(
        name = "ai_edge_apis_rag_pipeline_x86_64_libsqlite_vector_store_jni_so",
        sha256 = "2498f252ca3800ece6f462906ccecbd37cff317f75ffa704b7828ee9edf6ebe1",
        urls = ["https://storage.googleapis.com/mediapipe-assets/rag_pipeline/x86_64/libsqlite_vector_store_jni.so?generation=1754586489444986"],
    )

    http_file(
        name = "ai_edge_apis_rag_pipeline_android_arm64_libsqlite_vector_store_jni_so",
        sha256 = "e1e30444e1194cfa9e20913309d8e80810b24ecd2eb3f922330304734ad348c0",
        urls = ["https://storage.googleapis.com/mediapipe-assets/rag_pipeline/android_arm64/libsqlite_vector_store_jni.so?generation=1754586489386964"],
    )

    http_file(
        name = "ai_edge_apis_rag_pipeline_x86_64_libgecko_embedding_model_jni_so",
        sha256 = "c87bcd87d44f8839afc9028008f5dbc7e3a78053183ba9ef1513468d490440f0",
        urls = ["https://storage.googleapis.com/mediapipe-assets/rag_pipeline/x86_64/libgecko_embedding_model_jni.so?generation=1754586489684884"],
    )

    http_file(
        name = "ai_edge_apis_rag_pipeline_android_arm64_libgecko_embedding_model_jni_so",
        sha256 = "7beca7a000c2751f4ee80a7cc37524532a09cb3e4fa5cf98f2e7afe2622dee27",
        urls = ["https://storage.googleapis.com/mediapipe-assets/rag_pipeline/android_arm64/libgecko_embedding_model_jni.so?generation=1754586489531355"],
    )
