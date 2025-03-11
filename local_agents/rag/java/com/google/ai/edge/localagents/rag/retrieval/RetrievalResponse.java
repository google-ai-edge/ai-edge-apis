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
import java.util.List;

/** Retrieval response. */
@AutoValue
public abstract class RetrievalResponse<T> {
  /** The retrieved entities. */
  public abstract ImmutableList<RetrievalEntity<T>> getEntities();

  public abstract Builder<T> toBuilder();

  public static <T> Builder<T> builder() {
    return new AutoValue_RetrievalResponse.Builder<T>();
  }

  public static <T> RetrievalResponse<T> create(List<RetrievalEntity<T>> entities) {
    return RetrievalResponse.<T>builder().setEntities(ImmutableList.copyOf(entities)).build();
  }

  /** Auto Builder. */
  @AutoValue.Builder
  public abstract static class Builder<T> {
    protected abstract ImmutableList.Builder<RetrievalEntity<T>> entitiesBuilder();

    public abstract Builder<T> setEntities(ImmutableList<RetrievalEntity<T>> entities);

    public Builder<T> addEntity(RetrievalEntity<T> entity) {
      entitiesBuilder().add(entity);
      return this;
    }

    public abstract RetrievalResponse<T> build();
  }
}
