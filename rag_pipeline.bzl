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
        sha256 = "cf4a75cff75434efdff7df1a6dfb1a48f1d15a0e9c3f418ccb95039da345f846",
        urls = ["https://storage.googleapis.com/mediapipe-assets/rag_pipeline/x86_64/libtext_chunker_jni.so?generation=1756928525133681"],
    )

    http_file(
        name = "ai_edge_apis_rag_pipeline_android_arm64_libtext_chunker_jni_so",
        sha256 = "7b539c8cbc0aa71eba8cb2cbe417b88b4f0c2bd09a686d1abca5955b010e4e95",
        urls = ["https://storage.googleapis.com/mediapipe-assets/rag_pipeline/android_arm64/libtext_chunker_jni.so?generation=1756928525133753"],
    )

    http_file(
        name = "ai_edge_apis_rag_pipeline_x86_64_libsqlite_vector_store_jni_so",
        sha256 = "2f0e4048764de76c67d88a73580d9dbc4d1d0beab54688a58c7a596011d1c71d",
        urls = ["https://storage.googleapis.com/mediapipe-assets/rag_pipeline/x86_64/libsqlite_vector_store_jni.so?generation=1756928525304337"],
    )

    http_file(
        name = "ai_edge_apis_rag_pipeline_android_arm64_libsqlite_vector_store_jni_so",
        sha256 = "7267b63291dc355b3fc9642a38bcab58fdb98c4d71a3ec740066e0663ddcc917",
        urls = ["https://storage.googleapis.com/mediapipe-assets/rag_pipeline/android_arm64/libsqlite_vector_store_jni.so?generation=1756928525332537"],
    )

    http_file(
        name = "ai_edge_apis_rag_pipeline_x86_64_libgecko_embedding_model_jni_so",
        sha256 = "b9a2138029d35699817cbfe64a78a50b8a50cdb4e2cb21dd242080beae81fc85",
        urls = ["https://storage.googleapis.com/mediapipe-assets/rag_pipeline/x86_64/libgecko_embedding_model_jni.so?generation=1756928525579655"],
    )

    http_file(
        name = "ai_edge_apis_rag_pipeline_android_arm64_libgecko_embedding_model_jni_so",
        sha256 = "c7776182625d8f3d1760c6f3a1b6a25bc5c47ceff51f121fc5e5b1a85c58f9e8",
        urls = ["https://storage.googleapis.com/mediapipe-assets/rag_pipeline/android_arm64/libgecko_embedding_model_jni.so?generation=1756928525481042"],
    )

    http_file(
        name = "ai_edge_apis_rag_pipeline_x86_64_libgemma_embedding_model_jni_so",
        sha256 = "03ab04cd8e781a7eaf339c9c70fcc36463abe679123768fc28e4bad67c3377a4",
        urls = ["https://storage.googleapis.com/mediapipe-assets/rag_pipeline/x86_64/libgemma_embedding_model_jni.so?generation=1756928525942414"],
    )

    http_file(
        name = "ai_edge_apis_rag_pipeline_android_arm64_libgemma_embedding_model_jni_so",
        sha256 = "42e226496bfe28bf94848dba5796a7bd0ed70086423cdfe1610fac8d5482e32c",
        urls = ["https://storage.googleapis.com/mediapipe-assets/rag_pipeline/android_arm64/libgemma_embedding_model_jni.so?generation=1756928525479325"],
    )
