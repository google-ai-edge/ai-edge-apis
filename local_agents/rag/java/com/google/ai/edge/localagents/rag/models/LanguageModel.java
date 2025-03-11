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
package com.google.ai.edge.localagents.rag.models;

import com.google.common.util.concurrent.ListenableFuture;
import java.util.concurrent.Executor;
import org.jspecify.annotations.Nullable;

/** An interface for the language model. */
public interface LanguageModel {
  /**
   * Generates a response from the language model.
   *
   * @param request the request to generate a response.
   * @return a future of the response.
   */
  public ListenableFuture<LanguageModelResponse> generateResponse(
      LanguageModelRequest request, Executor executor);

  /**
   * Generates a response from the language model with a progress listener.
   *
   * @param request the request to generate a response.
   * @param progressListener the progress listener to receive the response.
   * @return a future of the response.
   */
  public ListenableFuture<LanguageModelResponse> generateResponse(
      LanguageModelRequest request,
      Executor executor,
      @Nullable AsyncProgressListener<LanguageModelResponse> progressListener);
}
