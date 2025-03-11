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

import com.google.ai.edge.localagents.rag.retrieval.BaseRetriever;
import com.google.ai.edge.localagents.rag.retrieval.RetrievalRequest;
import com.google.ai.edge.localagents.rag.retrieval.RetrievalResponse;
import com.google.ai.edge.localagents.rag.retrieval.SemanticDataEntry;
import com.google.common.collect.ImmutableList;
import com.google.common.util.concurrent.ListenableFuture;
import org.jspecify.annotations.NonNull;

/** An interface for semantic memory that creates and recalls memories associated with <T>. */
public interface SemanticMemory<T extends @NonNull Object> extends BaseRetriever<T> {
  /**
   * Retrieves results from memory.
   *
   * @param query The query to retrieve results for.
   * @return A future that resolves to the retrieval response.
   */
  @Override
  public ListenableFuture<RetrievalResponse<T>> retrieveResults(RetrievalRequest<T> query);

  /**
   * Records a memory.
   *
   * @param item The item to record.
   * @return A future that resolves to a boolean indicating whether the item is successfully stored
   *     in the vector store.
   */
  public ListenableFuture<Boolean> recordMemoryItem(T item);

  /**
   * Records a memory with metadata.
   *
   * @param entry The memory entry to record.
   * @return A future that resolves to a boolean indicating whether the memory entry is successfully
   *     stored in the vector store.
   */
  public ListenableFuture<Boolean> recordMemoryEntry(SemanticDataEntry<T> entry);

  /**
   * Records memories in batch.
   *
   * @param items The items to record.
   * @return A future that resolves to a boolean indicating whether the items are successfully
   *     stored in the vector store.
   */
  public ListenableFuture<Boolean> recordBatchedMemoryItems(ImmutableList<T> items);

  /**
   * Records memories in batch with metadata.
   *
   * @param entries The memory entries to record.
   * @return A future that resolves to a boolean indicating whether the memory entries are
   *     successfully stored in the vector store.
   */
  public ListenableFuture<Boolean> recordBatchedMemoryEntries(
      ImmutableList<SemanticDataEntry<T>> entries);
}
