FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        gcc g++ \
        curl \
        lsb-release \
        software-properties-common \
        gnupg \
        zip \
        unzip \
        wget \
        openjdk-21-jdk && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

ENV JAVA_HOME=/usr/lib/jvm/java-1.21.0-openjdk-amd64

# Install Clang 18
RUN wget https://apt.llvm.org/llvm.sh && \
    chmod +x llvm.sh && \
    ./llvm.sh 18 && \
    ln -sf /usr/bin/clang-18 /usr/bin/clang && \
    ln -sf /usr/bin/clang++-18 /usr/bin/clang++ && \
    ln -sf /usr/bin/clang-format-18 /usr/bin/clang-format

# Install Android SDK
RUN mkdir /root/android-sdk && \
    mkdir /tmp/android_sdk/ && \
    curl https://dl.google.com/android/repository/commandlinetools-linux-7583922_latest.zip -o /tmp/android_sdk/android_sdk.zip && \
    unzip -q /tmp/android_sdk/android_sdk.zip -d /tmp/android_sdk/ && \
    /tmp/android_sdk/cmdline-tools/bin/sdkmanager --update --sdk_root=/root/android-sdk && \
    yes | /tmp/android_sdk/cmdline-tools/bin/sdkmanager "build-tools;30.0.3" "platform-tools" "platforms;android-30" "extras;android;m2repository" --sdk_root=/root/android-sdk >/dev/null
ENV ANDROID_HOME=/root/android-sdk

# Install Android NDK
ARG ANDROID_NDK_VERSION=r28
RUN wget -q "https://dl.google.com/android/repository/android-ndk-${ANDROID_NDK_VERSION}-linux.zip" && \
    unzip -q "android-ndk-${ANDROID_NDK_VERSION}-linux.zip" && \
    mv "android-ndk-${ANDROID_NDK_VERSION}" "/root/android-ndk-${ANDROID_NDK_VERSION}" && \
    rm "android-ndk-${ANDROID_NDK_VERSION}-linux.zip"

ENV ANDROID_NDK_HOME=/root/android-ndk-r28

# Install bazel
ARG BAZEL_VERSION=8.1.1
RUN mkdir /bazel && \
    wget --no-check-certificate -O /bazel/installer.sh "https://github.com/bazelbuild/bazel/releases/download/${BAZEL_VERSION}/bazel-${BAZEL_VERSION}-installer-linux-x86_64.sh" && \
    wget --no-check-certificate -O  /bazel/LICENSE.txt "https://raw.githubusercontent.com/bazelbuild/bazel/master/LICENSE" && \
    chmod +x /bazel/installer.sh && \
    /bazel/installer.sh  && \
    rm -f /bazel/installer.sh
