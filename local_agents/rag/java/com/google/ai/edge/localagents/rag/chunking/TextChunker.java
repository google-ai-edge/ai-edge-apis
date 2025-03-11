/**
 * Copyright 2025 The Google AI Edge Authors.
 *
 * <p>Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file
 * except in compliance with the License. You may obtain a copy of the License at
 *
 * <p>http://www.apache.org/licenses/LICENSE-2.0
 *
 * <p>Unless required by applicable law or agreed to in writing, software distributed under the
 * License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
 * express or implied. See the License for the specific language governing permissions and
 * limitations under the License.
 */
package com.google.ai.edge.localagents.rag.chunking;

import java.util.List;

/**
 * A simple text chunker. It supports two chunking methods: 1. Simply splits the text into chunks of
 * fixed size with an overlap. 2. Chunks the text on sentence boundaries.
 */
public final class TextChunker {

  static {
    System.loadLibrary("text_chunker_jni");
  }

  private final long jniHandle;

  public TextChunker() {
    this.jniHandle = nativeCreateTextChunker();
  }

  /**
   * Simply splits the text into chunks of fixed size with an overlap. The text is split into tokens
   * using whitespace as the delimiter.
   *
   * @param text The text to chunk.
   * @param chunkSize The size of each chunk.
   * @param chunkOverlap The overlap between chunks.
   * @return A list of chunks.
   */
  public List<String> chunk(String text, int chunkSize, int chunkOverlap) {
    return nativeChunk(jniHandle, text, chunkSize, chunkOverlap);
  }

  /**
   * Chunks the text on sentence boundaries. The text is split into sentences. This only supports
   * English at the moment. Each sentence is split into tokens using whitespace as the delimiter.
   *
   * @param text The text to chunk.
   * @param chunkSize The size of each chunk.
   * @return A list of chunks.
   */
  public List<String> chunkBySentences(String text, int chunkSize) {
    return nativeChunkBySentences(jniHandle, text, chunkSize);
  }

  private static native long nativeCreateTextChunker();

  private static native List<String> nativeChunk(
      long jniHandle, String text, int chunkSize, int chunkOverlap);

  private static native List<String> nativeChunkBySentences(
      long jniHandle, String text, int chunkSize);
}
