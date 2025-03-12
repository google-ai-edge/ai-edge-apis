workspace(name = "ai_edge_apis")

load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")

http_archive(
    name = "com_google_protobuf",
    sha256 = "87407cd28e7a9c95d9f61a098a53cf031109d451a7763e7dd1253abf8b4df422",
    strip_prefix = "protobuf-3.19.1",
    urls = ["https://github.com/protocolbuffers/protobuf/archive/v3.19.1.tar.gz"],
)

http_archive(
    name = "rules_python",
    sha256 = "9d04041ac92a0985e344235f5d946f71ac543f1b1565f2cdbc9a2aaee8adf55b",
    strip_prefix = "rules_python-0.26.0",
    url = "https://github.com/bazelbuild/rules_python/releases/download/0.26.0/rules_python-0.26.0.tar.gz",
)

load("@rules_python//python:repositories.bzl", "py_repositories", "python_register_toolchains")

py_repositories()

python_register_toolchains(
    name = "python",
    ignore_root_user_error = True,
    python_version = "3.10",
)

http_archive(
    name = "rules_java",
    sha256 = "c73336802d0b4882e40770666ad055212df4ea62cfa6edf9cb0f9d29828a0934",
    url = "https://github.com/bazelbuild/rules_java/releases/download/5.3.5/rules_java-5.3.5.tar.gz",
)

http_archive(
    name = "rules_android_ndk",
    sha256 = "d230a980e0d3a42b85d5fce2cb17ec3ac52b88d2cff5aaf86bae0f05b48adc55",
    strip_prefix = "rules_android_ndk-d5c9d46a471e8fcd80e7ec5521b78bb2df48f4e0",
    url = "https://github.com/bazelbuild/rules_android_ndk/archive/d5c9d46a471e8fcd80e7ec5521b78bb2df48f4e0.zip",
)

load("@rules_android_ndk//:rules.bzl", "android_ndk_repository")

http_archive(
    name = "build_bazel_rules_android",
    sha256 = "cd06d15dd8bb59926e4d65f9003bfc20f9da4b2519985c27e190cddc8b7a7806",
    strip_prefix = "rules_android-0.1.1",
    urls = ["https://github.com/bazelbuild/rules_android/archive/v0.1.1.zip"],
)

load("@build_bazel_rules_android//android:rules.bzl", "android_sdk_repository")

# Maven dependencies.
RULES_JVM_EXTERNAL_TAG = "4.0"

RULES_JVM_EXTERNAL_SHA = "31701ad93dbfe544d597dbe62c9a1fdd76d81d8a9150c2bf1ecf928ecdf97169"

http_archive(
    name = "rules_jvm_external",
    sha256 = RULES_JVM_EXTERNAL_SHA,
    strip_prefix = "rules_jvm_external-%s" % RULES_JVM_EXTERNAL_TAG,
    url = "https://github.com/bazelbuild/rules_jvm_external/archive/%s.zip" % RULES_JVM_EXTERNAL_TAG,
)

load("@rules_jvm_external//:defs.bzl", "maven_install")

maven_install(
    artifacts = [
        "androidx.annotation:annotation:1.9.1",
        "com.google.android:android:4.1.1.4",
        "com.google.guava:guava:33.3.1-android",
        "com.google.mediapipe:tasks-genai:0.10.22",
        "com.squareup.okhttp3:okhttp:4.12.0",
        "org.checkerframework:checker-qual:3.20.0",
        "org.json:json:20250107",
        "org.jspecify:jspecify:1.0.0",
    ],
    fetch_sources = True,
    repositories = [
        "https://maven.google.com",
        "https://dl.google.com/dl/android/maven2",
        "https://repo1.maven.org/maven2",
        "https://jcenter.bintray.com",
    ],
    version_conflict_policy = "pinned",
)

# ABSL on 2023-10-18
http_archive(
    name = "com_google_absl",
    sha256 = "f841f78243f179326f2a80b719f2887c38fe226d288ecdc46e2aa091e6aa43bc",
    strip_prefix = "abseil-cpp-9687a8ea750bfcddf790372093245a1d041b21a3",
    urls = ["https://github.com/abseil/abseil-cpp/archive//9687a8ea750bfcddf790372093245a1d041b21a3.tar.gz"],
)

http_archive(
    name = "zlib",
    build_file = "@//third_party:zlib.bazel",
    sha256 = "b3a24de97a8fdbc835b9833169501030b8977031bcb54b3b3ac13740f846ab30",
    strip_prefix = "zlib-1.2.13",
    url = "http://zlib.net/fossils/zlib-1.2.13.tar.gz",
)

load("rag_pipeline.bzl", "rag_pipeline_files")

rag_pipeline_files()

android_sdk_repository(
    name = "androidsdk",
)

android_ndk_repository(
    name = "androidndk",
    api_level = 21,
)

bind(
    name = "android/crosstool",
    actual = "@androidndk//:toolchain",
)
