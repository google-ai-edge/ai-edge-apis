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
package com.google.ai.edge.localagents.rag.shared;

import com.google.auto.value.AutoValue;
import com.google.common.collect.ImmutableList;
import java.util.List;

/** Class for a list of key value pairs. */
@AutoValue
public abstract class Metadata {
  public abstract ImmutableList<KeyValuePair> getKeyValuePairs();

  public static Builder newBuilder() {
    return new AutoValue_Metadata.Builder();
  }

  public static Metadata of(List<KeyValuePair> keyValuePairs) {
    return newBuilder().setKeyValuePairs(ImmutableList.copyOf(keyValuePairs)).build();
  }

  /** Auto Builder. */
  @AutoValue.Builder
  public abstract static class Builder {
    protected abstract ImmutableList.Builder<KeyValuePair> keyValuePairsBuilder();

    public abstract Builder setKeyValuePairs(List<KeyValuePair> keyValuePairs);

    public Builder addKeyValuePair(KeyValuePair keyValuePair) {
      keyValuePairsBuilder().add(keyValuePair);
      return this;
    }

    public abstract Metadata build();
  }
}
