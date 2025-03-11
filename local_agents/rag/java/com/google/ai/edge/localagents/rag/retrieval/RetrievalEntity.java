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

import com.google.auto.value.AutoValue;
import com.google.common.collect.ImmutableList;
import com.google.common.collect.ImmutableMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;

/** Retrieval entity. */
@AutoValue
public abstract class RetrievalEntity<T> {
  /** The raw data associated with this entity. */
  public abstract T getData();

  /** The embeddings associated with this entity. */
  public abstract ImmutableList<Float> getEmbeddings();

  /** Metadata associated with this entity, may be empty. */
  public abstract ImmutableMap<String, Object> getMetadata();

  public abstract Builder<T> toBuilder();

  public static <T> Builder<T> builder() {
    // Initialize metadata to an empty map.
    return new AutoValue_RetrievalEntity.Builder<T>().setMetadata(ImmutableMap.of());
  }

  public static <T> RetrievalEntity<T> create(
      T data, List<Float> embeddings, Optional<ImmutableMap<String, Object>> metadata) {
    return RetrievalEntity.<T>builder()
        .setData(data)
        .setEmbeddings(ImmutableList.copyOf(embeddings))
        .setMetadata(metadata.orElse(ImmutableMap.of()))
        .build();
  }

  /** Auto Builder. */
  @AutoValue.Builder
  public abstract static class Builder<T> {
    protected abstract ImmutableMap.Builder<String, Object> metadataBuilder();

    public abstract Builder<T> setData(T data);

    public abstract Builder<T> setEmbeddings(ImmutableList<Float> embeddings);

    public abstract Builder<T> setMetadata(Map<String, Object> metadata);

    public Builder<T> addMetadata(String key, Object value) {
      metadataBuilder().put(key, value);
      return this;
    }

    public abstract RetrievalEntity<T> build();
  }
}
