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

import com.google.auto.value.AutoValue;
import com.google.common.collect.ImmutableList;

import java.util.List;

/** Class for embedding request. */
@AutoValue
public abstract class EmbeddingRequest<T> {
  public abstract ImmutableList<EmbedData<T>> getEmbedData();

  public static <T> Builder<T> builder() {
    return new AutoValue_EmbeddingRequest.Builder<T>();
  }

  public static <T> EmbeddingRequest<T> create(List<EmbedData<T>> embedData) {
    return EmbeddingRequest.<T>builder().setEmbedData(ImmutableList.copyOf(embedData)).build();
  }

  /** Auto Builder. */
  @AutoValue.Builder
  public abstract static class Builder<T> {
    protected abstract ImmutableList.Builder<EmbedData<T>> embedDataBuilder();

    public abstract Builder<T> setEmbedData(ImmutableList<EmbedData<T>> embedData);

    public Builder<T> addEmbedData(EmbedData<T> embedData) {
      embedDataBuilder().add(embedData);
      return this;
    }

    public abstract EmbeddingRequest<T> build();
  }
}
