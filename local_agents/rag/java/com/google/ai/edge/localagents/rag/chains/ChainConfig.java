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

import com.google.ai.edge.localagents.rag.memory.SemanticMemory;
import com.google.ai.edge.localagents.rag.models.LanguageModel;
import com.google.ai.edge.localagents.rag.prompt.PromptBuilder;
import com.google.auto.value.AutoValue;
import java.util.Optional;
import org.checkerframework.checker.nullness.qual.NonNull;

/** The configuration for a chain. */
@AutoValue
public abstract class ChainConfig<T extends @NonNull Object> {
  /** Returns the language model to use for the chain. */
  public abstract Optional<LanguageModel> getLanguageModel();

  /** Returns the prompt builder to use for the chain. */
  public abstract Optional<PromptBuilder> getPromptBuilder();

  /** Returns the semantic memory to use for the chain. */
  public abstract Optional<SemanticMemory<T>> getSemanticMemory();

  public abstract Builder<T> toBuilder();

  public static <T extends @NonNull Object> Builder<T> builder() {
    return new AutoValue_ChainConfig.Builder<T>();
  }

  public static <T extends @NonNull Object> ChainConfig<T> create(
      LanguageModel languageModel, PromptBuilder promptBuilder, SemanticMemory<T> semanticMemory) {
    return ChainConfig.<T>builder()
        .setLanguageModel(languageModel)
        .setPromptBuilder(promptBuilder)
        .setSemanticMemory(semanticMemory)
        .build();
  }

  public static <T extends @NonNull Object> ChainConfig<T> create(
      SemanticMemory<T> semanticMemory) {
    return ChainConfig.<T>builder().setSemanticMemory(semanticMemory).build();
  }

  /** Auto Builder. */
  @AutoValue.Builder
  public abstract static class Builder<T extends @NonNull Object> {
    public abstract Builder<T> setLanguageModel(LanguageModel languageModel);

    public abstract Builder<T> setPromptBuilder(PromptBuilder promptBuilder);

    public abstract Builder<T> setSemanticMemory(SemanticMemory<T> semanticMemory);

    public abstract ChainConfig<T> build();
  }
}
