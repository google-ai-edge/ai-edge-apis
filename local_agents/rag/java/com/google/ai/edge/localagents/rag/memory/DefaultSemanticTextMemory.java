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

import static com.google.common.collect.ImmutableList.toImmutableList;
import static com.google.common.util.concurrent.Futures.immediateFuture;

import com.google.ai.edge.localagents.rag.models.EmbedData;
import com.google.ai.edge.localagents.rag.models.Embedder;
import com.google.ai.edge.localagents.rag.models.EmbeddingRequest;
import com.google.ai.edge.localagents.rag.retrieval.RetrievalEntity;
import com.google.ai.edge.localagents.rag.retrieval.RetrievalRequest;
import com.google.ai.edge.localagents.rag.retrieval.RetrievalResponse;
import com.google.ai.edge.localagents.rag.retrieval.SemanticDataEntry;
import com.google.common.collect.ImmutableList;
import com.google.common.util.concurrent.Futures;
import com.google.common.util.concurrent.ListenableFuture;
import com.google.common.util.concurrent.ThreadFactoryBuilder;
import java.util.List;
import java.util.concurrent.Executor;
import java.util.concurrent.Executors;

/**
 * The default semantic text memory. It uses a vector store and embedding model for semantic
 * retrieval.
 */
public final class DefaultSemanticTextMemory implements SemanticMemory<String> {
  private final VectorStore<String> vectorStore;
  private final Embedder<String> embeddingModel;
  private final Executor workerExecutor;

  /**
   * Creates a new default semantic text memory.
   *
   * @param vectorStore The vector store for storing the text embeddings.
   * @param embeddingModel The embedding model to use for embedding the text.
   */
  public DefaultSemanticTextMemory(
      VectorStore<String> vectorStore, Embedder<String> embeddingModel) {
    this.vectorStore = vectorStore;
    this.embeddingModel = embeddingModel;
    this.workerExecutor =
        Executors.newSingleThreadExecutor(
            new ThreadFactoryBuilder()
                .setNameFormat("default-semantic-text-memory-pool-%d")
                .setPriority(Thread.NORM_PRIORITY)
                .build());
  }

  /**
   * Retrieves the top K elements from the memory that are most semantically similar to the given
   * query.
   *
   * @param request The retrieval request.
   * @return A future that resolves to the retrieval response.
   */
  @Override
  public ListenableFuture<RetrievalResponse<String>> retrieveResults(
      RetrievalRequest<String> request) {
    EmbedData.Builder<String> embedDataBuilder =
        EmbedData.<String>builder().setData(request.getQuery()).setIsQuery(true);
    switch (request.getConfig().getTask()) {
      case TASK_UNSPECIFIED:
      case RETRIEVAL_QUERY:
        embedDataBuilder.setTask(EmbedData.TaskType.RETRIEVAL_QUERY);
        break;
      case QUESTION_ANSWERING:
        embedDataBuilder.setTask(EmbedData.TaskType.QUESTION_ANSWERING);
        break;
      case FACT_VERIFICATION:
        embedDataBuilder.setTask(EmbedData.TaskType.FACT_VERIFICATION);
        break;
      case CODE_RETRIEVAL:
        embedDataBuilder.setTask(EmbedData.TaskType.CODE_RETRIEVAL);
        break;
    }
    EmbeddingRequest<String> embeddingRequest =
        EmbeddingRequest.<String>create(ImmutableList.of(embedDataBuilder.build()));
    return Futures.transform(
        embeddingModel.getEmbeddings(embeddingRequest),
        (embeddings) -> {
          List<VectorStoreRecord<String>> records =
              vectorStore.getNearestRecords(
                  embeddings,
                  request.getConfig().getTopK(),
                  request.getConfig().getMinSimilarityScore());
          ImmutableList<RetrievalEntity<String>> entities =
              records.stream()
                  .map(
                      record ->
                          RetrievalEntity.<String>builder()
                              .setData(record.getData())
                              .setEmbeddings(record.getEmbeddings())
                              .setMetadata(record.getMetadata())
                              .build())
                  .collect(toImmutableList());
          return RetrievalResponse.<String>create(entities);
        },
        workerExecutor);
  }

  /**
   * Stores the text memory and its embeddings in the vector store.
   *
   * @param text The text to record.
   * @return A future that resolves to a boolean indicating whether the item is successfully stored
   *     in the vector store.
   */
  @Override
  public ListenableFuture<Boolean> recordMemoryItem(String text) {
    SemanticDataEntry<String> dataEntry = SemanticDataEntry.create(text);
    return recordMemoryEntry(dataEntry);
  }

  /**
   * Stores the memory entry and its embeddings in the vector store.
   *
   * @param dataEntry The memory entry to record.
   * @return A future that resolves to a boolean indicating whether the memory entry is successfully
   *     stored in the vector store.
   */
  @Override
  public ListenableFuture<Boolean> recordMemoryEntry(SemanticDataEntry<String> dataEntry) {
    EmbedData<String> embedText =
        EmbedData.<String>builder()
            .setData(dataEntry.getCustomEmbeddingData().orElse(dataEntry.getData()))
            .setTask(EmbedData.TaskType.RETRIEVAL_DOCUMENT)
            .build();
    EmbeddingRequest<String> embeddingRequest =
        EmbeddingRequest.<String>create(ImmutableList.of(embedText));
    return Futures.transform(
        embeddingModel.getEmbeddings(embeddingRequest),
        (embeddings) -> {
          VectorStoreRecord<String> record =
              VectorStoreRecord.<String>builder()
                  .setData(dataEntry.getData())
                  .setEmbeddings(embeddings)
                  .setMetadata(dataEntry.getMetadata())
                  .build();
          vectorStore.insert(record);
          return true;
        },
        workerExecutor);
  }

  /**
   * Stores the text memories and their embeddings in the vector store.
   *
   * @param texts The texts to record.
   * @return A future that resolves to a boolean indicating whether the items are successfully
   *     stored in the vector store.
   */
  @Override
  public ListenableFuture<Boolean> recordBatchedMemoryItems(ImmutableList<String> texts) {
    return recordBatchedMemoryEntries(
        texts.stream().map(SemanticDataEntry::create).collect(toImmutableList()));
  }

  /**
   * Stores the memory entries and their embeddings in the vector store.
   *
   * @param dataEntries The memory entries to record.
   * @return A future that resolves to a boolean indicating whether the memory entries are
   *     successfully stored in the vector store.
   */
  @Override
  public ListenableFuture<Boolean> recordBatchedMemoryEntries(
      ImmutableList<SemanticDataEntry<String>> dataEntries) {
    if (dataEntries.isEmpty()) {
      return immediateFuture(false);
    }
    var entries =
        dataEntries.stream()
            .map(
                dataEntry ->
                    EmbedData.<String>builder()
                        .setData(dataEntry.getCustomEmbeddingData().orElse(dataEntry.getData()))
                        .setTask(EmbedData.TaskType.RETRIEVAL_DOCUMENT)
                        .build())
            .collect(toImmutableList());
    var request = EmbeddingRequest.create(entries);

    return Futures.transform(
        embeddingModel.getBatchEmbeddings(request),
        (embeddingsList) -> {
          if (embeddingsList.size() != dataEntries.size()) {
            throw new AssertionError(
                String.format(
                    "Embeddings list size is not equal to memory entries size, %d != %d",
                    embeddingsList.size(), dataEntries.size()));
          }

          for (int i = 0; i < embeddingsList.size(); i++) {
            VectorStoreRecord<String> record =
                VectorStoreRecord.<String>builder()
                    .setData(dataEntries.get(i).getData())
                    .setEmbeddings(embeddingsList.get(i))
                    .setMetadata(dataEntries.get(i).getMetadata())
                    .build();
            vectorStore.insert(record);
          }
          return true;
        },
        workerExecutor);
  }
}
