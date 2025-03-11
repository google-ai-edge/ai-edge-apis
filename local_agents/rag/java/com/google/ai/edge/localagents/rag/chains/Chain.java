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

import com.google.ai.edge.localagents.rag.models.AsyncProgressListener;
import com.google.common.util.concurrent.ListenableFuture;
import org.jspecify.annotations.Nullable;

/** A chain is a sequence of operations that may be configured and invoked. */
interface Chain<I, O> {
  /**
   * Invokes the chain with the given request.
   *
   * @param request the request to invoke the chain with
   * @return a {@link ListenableFuture} that will be completed when the chain has finished
   *     executing.
   */
  ListenableFuture<O> invoke(I request);

  /**
   * Invokes the chain with the given request and a listener that receives partial results until it
   * is invoked with `done` set to {@code true}.
   *
   * @param request the request to invoke the chain with
   * @param listener the listener to receive partial results
   * @return a {@link ListenableFuture} that will be completed when the chain has finished
   *     executing.
   */
  ListenableFuture<O> invoke(I request, @Nullable AsyncProgressListener<O> listener);
}
