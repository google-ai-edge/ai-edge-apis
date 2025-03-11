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

import static com.google.common.base.Preconditions.checkNotNull;

import com.google.ai.edge.localagents.rag.memory.SemanticMemory;
import com.google.ai.edge.localagents.rag.models.AsyncProgressListener;
import com.google.ai.edge.localagents.rag.models.LanguageModelRequest;
import com.google.ai.edge.localagents.rag.models.LanguageModelResponse;
import com.google.ai.edge.localagents.rag.retrieval.RetrievalRequest;
import com.google.ai.edge.localagents.rag.retrieval.RetrievalResponse;
import com.google.common.util.concurrent.Futures;
import com.google.common.util.concurrent.ListenableFuture;
import java.util.concurrent.Executor;
import java.util.concurrent.Executors;
import org.jspecify.annotations.Nullable;

/**
 * A simple retrieval and inference chain. It retrieves the top K elements from memory, augments the
 * prompt, and then uses a language model to generate a response.
 */
public final class RetrievalAndInferenceChain
    implements Chain<RetrievalRequest<String>, LanguageModelResponse> {
  private final ChainConfig<String> config;
  private final Executor workerExecutor;

  public RetrievalAndInferenceChain(ChainConfig<String> config) {
    this.config = config;
    this.workerExecutor = Executors.newSingleThreadExecutor();
  }

  @Override
  public ListenableFuture<LanguageModelResponse> invoke(RetrievalRequest<String> retrievalRequest) {
    // Underlying language models may have different code paths based on whether or not a progress
    // listener is provided.
    return invoke(retrievalRequest, null);
  }

  /**
   * Invokes the retrieval and inference chain.
   *
   * @param retrievalRequest The retrieval request.
   * @param asyncProgressListener The streaming response callback.
   * @return A future that resolves to the language model response.
   */
  @Override
  public ListenableFuture<LanguageModelResponse> invoke(
      RetrievalRequest<String> retrievalRequest,
      @Nullable AsyncProgressListener<LanguageModelResponse> asyncProgressListener) {
    SemanticMemory<String> memory = config.getSemanticMemory().get(); // Or throw.
    checkNotNull(memory, "semantic text memory is null");
    ListenableFuture<RetrievalResponse<String>> responseFuture =
        memory.retrieveResults(retrievalRequest);
    return Futures.transformAsync(
        responseFuture,
        response -> {
          StringBuilder memoryStringBuilder = new StringBuilder();
          response
              .getEntities()
              .forEach(entity -> memoryStringBuilder.append(entity.getData()).append("\n"));
          String memoryString = memoryStringBuilder.toString();
          String prompt =
              config
                  .getPromptBuilder()
                  .get() // Or throw.
                  .buildPrompt(memoryString, retrievalRequest.getQuery());
          LanguageModelRequest languageModelRequest =
              LanguageModelRequest.builder().setPrompt(prompt).build();
          return config
              .getLanguageModel()
              .get() // Or throw.
              .generateResponse(languageModelRequest, workerExecutor, asyncProgressListener);
        },
        workerExecutor);
  }
}
