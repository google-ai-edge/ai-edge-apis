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
package com.google.ai.edge.localagents.rag.retrieval;

import com.google.common.util.concurrent.ListenableFuture;

/** The interface for retriever. */
public interface BaseRetriever<T> {
  /**
   * Retrieves results.
   *
   * @param request The retrieval request.
   * @return A future that resolves to the retrieval response.
   */
  public ListenableFuture<RetrievalResponse<T>> retrieveResults(RetrievalRequest<T> request);
}
