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
package com.google.ai.edge.localagents.rag.chains;

import com.google.ai.edge.localagents.rag.memory.SemanticMemory;
import com.google.ai.edge.localagents.rag.models.AsyncProgressListener;
import com.google.ai.edge.localagents.rag.retrieval.RetrievalRequest;
import com.google.ai.edge.localagents.rag.retrieval.RetrievalResponse;
import com.google.common.util.concurrent.Futures;
import com.google.common.util.concurrent.ListenableFuture;
import java.util.concurrent.Executor;
import java.util.concurrent.Executors;
import org.checkerframework.checker.nullness.qual.NonNull;
import org.jspecify.annotations.Nullable;

/** A simple retrieval-only chain. It retrieves the top K elements from memory given a query. */
public final class RetrievalChain<T extends @NonNull Object>
    implements Chain<RetrievalRequest<T>, RetrievalResponse<T>> {
  private final ChainConfig<T> config;
  private final Executor workerExecutor;

  public RetrievalChain(ChainConfig<T> config) {
    this.config = config;
    this.workerExecutor = Executors.newSingleThreadExecutor();
  }

  /**
   * Invokes the retrieval-only chain.
   *
   * @param retrievalRequest The retrieval request.
   * @return A future that resolves to the language model response.
   */
  @Override
  public ListenableFuture<RetrievalResponse<T>> invoke(RetrievalRequest<T> retrievalRequest) {
    return invoke(retrievalRequest, null);
  }

  /**
   * Calls the memory to retrieve results, calls the progress listener once if provided.
   *
   * @param retrievalRequest The retrieval request.
   * @param asyncProgressListener The response callback.
   * @return A future that resolves to the retrieval response.
   */
  @Override
  public ListenableFuture<RetrievalResponse<T>> invoke(
      RetrievalRequest<T> retrievalRequest,
      @Nullable AsyncProgressListener<RetrievalResponse<T>> asyncProgressListener) {
    SemanticMemory<T> memory = config.getSemanticMemory().get(); // Or throw.

    return Futures.transform(
        memory.retrieveResults(retrievalRequest),
        (RetrievalResponse<T> response) -> {
          if (asyncProgressListener != null) {
            asyncProgressListener.run(response, true);
          }
          return response;
        },
        workerExecutor);
  }
}
