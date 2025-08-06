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

/** Retrieval configuration. */
@AutoValue
public abstract class RetrievalConfig {
  /** The type of retrieval task. */
  public enum TaskType {
    TASK_UNSPECIFIED,
    RETRIEVAL_QUERY,
    QUESTION_ANSWERING,
    FACT_VERIFICATION,
    CODE_RETRIEVAL,
  }

  /** This is the number of top K elements to retrieve. */
  public abstract int getTopK();

  /** The minimum similarity score to retrieve. Optional. Default = 0.0f. */
  public abstract float getMinSimilarityScore();

  /** The type of retrieval task. */
  public abstract TaskType getTask();

  public abstract Builder toBuilder();

  public static Builder builder() {
    return new AutoValue_RetrievalConfig.Builder().setMinSimilarityScore(0.0f);
  }

  public static RetrievalConfig create(int topK, TaskType taskType) {
    return builder().setTopK(topK).setTask(taskType).build();
  }

  public static RetrievalConfig create(int topK, float minSimilarityScore, TaskType taskType) {
    return builder()
        .setTopK(topK)
        .setMinSimilarityScore(minSimilarityScore)
        .setTask(taskType)
        .build();
  }

  /** Auto Builder. */
  @AutoValue.Builder
  public abstract static class Builder {
    public abstract Builder setTopK(int topK);

    public abstract Builder setMinSimilarityScore(float minSimilarityScore);

    public abstract Builder setTask(TaskType task);

    public abstract RetrievalConfig build();
  }
}
