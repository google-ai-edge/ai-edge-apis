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

/** The language model inference response. */
@AutoValue
public abstract class LanguageModelResponse {
  /** The generated text. */
  public abstract String getText();

  public static LanguageModelResponse create(String text) {
    return builder().setText(text).build();
  }

  public static Builder builder() {
    return new AutoValue_LanguageModelResponse.Builder();
  }

  public abstract Builder toBuilder();

  /** Auto Builder. */
  @AutoValue.Builder
  public abstract static class Builder {
    public abstract Builder setText(String text);

    public abstract LanguageModelResponse build();
  }

  LanguageModelResponse() {}
}
