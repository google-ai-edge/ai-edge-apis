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
import com.google.common.collect.ImmutableMap;

import java.util.Map;
import java.util.Optional;

/** The memory record entity. */
@AutoValue
public abstract class SemanticDataEntry<T> {
  public abstract T getData();

  /** Metadata associated with this entry, may be empty. */
  public abstract ImmutableMap<String, Object> getMetadata();

  /** Custom data for which to get embeddings. If not set, the data field will be used. */
  public abstract Optional<T> getCustomEmbeddingData();

  public abstract Builder<T> toBuilder();

  public static <T> Builder<T> builder() {
    // Initialize metadata to an empty map.
    return new AutoValue_SemanticDataEntry.Builder<T>().setMetadata(ImmutableMap.of());
  }

  public static <T> SemanticDataEntry<T> create(T data) {
    return create(data, ImmutableMap.of());
  }

  public static <T> SemanticDataEntry<T> create(T data, Map<String, Object> metadata) {
    return create(data, metadata, Optional.empty());
  }

  public static <T> SemanticDataEntry<T> create(
      T data, Map<String, Object> metadata, Optional<T> customEmbeddingData) {
    return SemanticDataEntry.<T>builder()
        .setData(data)
        .setMetadata(metadata)
        .setCustomEmbeddingData(customEmbeddingData)
        .build();
  }

  /** Auto Builder. */
  @AutoValue.Builder
  public abstract static class Builder<T> {
    protected abstract ImmutableMap.Builder<String, Object> metadataBuilder();

    public abstract Builder<T> setData(T data);

    public abstract Builder<T> setMetadata(Map<String, Object> metadata);

    public Builder<T> addMetadata(String key, Object value) {
      metadataBuilder().put(key, value);
      return this;
    }

    public abstract Builder<T> setCustomEmbeddingData(T customEmbeddingData);

    public abstract Builder<T> setCustomEmbeddingData(Optional<T> customEmbeddingData);

    public abstract SemanticDataEntry<T> build();
  }
}
