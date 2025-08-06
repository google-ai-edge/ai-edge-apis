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
import com.google.common.collect.ImmutableMap;
import java.util.Map;

/** Class for data to be embedded. */
@AutoValue
public abstract class EmbedData<T> {

  // (-- LINT.IfChange --)
  /** The type of task for which the embedding will be used. */
  public enum TaskType {
    /** Unset value, which will default to one of the other enum values. */
    TASK_TYPE_UNSPECIFIED(0),

    /** Specifies the given text is a query in a search/retrieval setting. */
    RETRIEVAL_QUERY(1),

    /** Specifies the given text is a document from the corpus being searched. */
    RETRIEVAL_DOCUMENT(2),

    /** Specifies the given text will be used for STS. */
    SEMANTIC_SIMILARITY(3),

    /** Specifies that the given text will be classified. */
    CLASSIFICATION(4),

    /** Specifies that the embeddings will be used for clustering. */
    CLUSTERING(5),

    /** Specifies that the given text will be used for question answering. */
    QUESTION_ANSWERING(6),

    /** Specifies that the given text will be used for fact verification. */
    FACT_VERIFICATION(7),

    /** Specifies that the given text will be used for code retrieval. */
    CODE_RETRIEVAL(8);

    // Magic java proto enum values.
    TaskType(int value) {
      this.value = value;
    }

    private final int value;

    public int value() {
      return value;
    }
  }

  // (--
  // LINT.ThenChange(
  // //depot/https://github.com/google-ai-edge/ai-edge-apis/tree/main/local_agents/rag/core/protos/embedding_models.proto,
  // //depot/https://github.com/google-ai-edge/ai-edge-apis/tree/main/local_agents/rag/java/com/google/ai/edge/localagents/rag/models/GeckoEmbeddingModel.java
  // )
  // --)

  public abstract T getData();

  public abstract TaskType getTask();

  /**
   * Whether the data is a query. If true, the data will be used as a query when embedding.
   * Otherwise, the data will be used as a document.
   */
  public abstract boolean getIsQuery();

  /**
   * Optional identifier of the content. This may be prepended to the input or otherwise used within
   * a prompt, depending on the task-specific instruction format.
   */
  public abstract ImmutableMap<String, Object> getMetadata();

  public static <T> Builder<T> builder() {
    return new AutoValue_EmbedData.Builder<T>().setIsQuery(false).setMetadata(ImmutableMap.of());
  }

  public static <T> EmbedData<T> create(T data, TaskType taskType) {
    return EmbedData.<T>builder().setData(data).setTask(taskType).build();
  }

  public static <T> EmbedData<T> create(T data, TaskType taskType, boolean isQuery) {
    return EmbedData.<T>builder().setData(data).setTask(taskType).setIsQuery(isQuery).build();
  }

  public static <T> EmbedData<T> create(
      T data, TaskType taskType, boolean isQuery, ImmutableMap<String, Object> metadata) {
    return EmbedData.<T>builder()
        .setData(data)
        .setTask(taskType)
        .setIsQuery(isQuery)
        .setMetadata(metadata)
        .build();
  }

  public Builder<T> toBuilder() {
    return new AutoValue_EmbedData.Builder<T>()
        .setData(getData())
        .setTask(getTask())
        .setIsQuery(getIsQuery())
        .setMetadata(getMetadata());
  }

  /** Auto Builder. */
  @AutoValue.Builder
  public abstract static class Builder<T> {
    public abstract Builder<T> setData(T data);

    public abstract Builder<T> setTask(TaskType taskType);

    public abstract Builder<T> setIsQuery(boolean isQuery);

    public abstract Builder<T> setMetadata(Map<String, Object> additionalData);

    public abstract EmbedData<T> build();
  }
}
