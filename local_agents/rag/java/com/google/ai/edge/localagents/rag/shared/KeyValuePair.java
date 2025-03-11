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

/** Class for a string key and value. Used for metadata storage. */
@AutoValue
public abstract class KeyValuePair {
  public abstract String getKey();

  public abstract String getValue();

  public static Builder newBuilder() {
    return new AutoValue_KeyValuePair.Builder();
  }

  public static KeyValuePair of(String key, String value) {
    return newBuilder().setKey(key).setValue(value).build();
  }

  /** Auto Builder. */
  @AutoValue.Builder
  public abstract static class Builder {
    public abstract Builder setKey(String key);

    public abstract Builder setValue(String value);

    public abstract KeyValuePair build();
  }
}
