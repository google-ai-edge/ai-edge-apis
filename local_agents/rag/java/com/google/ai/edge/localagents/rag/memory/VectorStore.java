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
package com.google.ai.edge.localagents.rag.memory;

import java.util.List;

/** An interface for the data store holding {@link VectorStoreRecord}s. */
public interface VectorStore<T> {
  /**
   * Inserts a new record into the vector store.
   *
   * @param record The record to insert.
   */
  public void insert(VectorStoreRecord<T> record);

  /**
   * Retrieves the top K elements from the vector store that are most semantically similar to the
   * given query.
   *
   * @param queryEmbeddings The query's embeddings.
   * @param topK The number of top elements to retrieve.
   * @param minSimilarityScore The minimum similarity score for the retrieved elements.
   * @return A list of the top K elements from the vector store that are most semantically similar
   *     to the given query.
   */
  public List<VectorStoreRecord<T>> getNearestRecords(
      List<Float> queryEmbeddings, int topK, float minSimilarityScore);
}
