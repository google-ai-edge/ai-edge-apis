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

import androidx.annotation.VisibleForTesting;

/** The embedding data processor for Gecko text embedding model. */
public final class GeckoEmbeddingDataProcessor implements EmbeddingDataProcessor<String> {
  public static final String TITLE_KEY = "title";

  @VisibleForTesting public static final String DOCUMENT_TEMPLATE = "title: %s | text: %s";

  @VisibleForTesting public static final String QUERY_TEMPLATE = "task: %s | query: %s";

  public GeckoEmbeddingDataProcessor() {}

  @Override
  public EmbedData<String> process(EmbedData<String> embedData) {
    String text;
    switch (embedData.getTask()) {
      case EmbedData.TaskType.RETRIEVAL_DOCUMENT -> {
        text = formatDocument(embedData);
      }
      case EmbedData.TaskType.RETRIEVAL_QUERY -> {
        text = formatQuery(embedData);
      }
      case EmbedData.TaskType.QUESTION_ANSWERING,
          EmbedData.TaskType.FACT_VERIFICATION,
          EmbedData.TaskType.CODE_RETRIEVAL -> {
        text = embedData.getIsQuery() ? formatQuery(embedData) : formatDocument(embedData);
      }
      case EmbedData.TaskType.SEMANTIC_SIMILARITY,
          EmbedData.TaskType.CLASSIFICATION,
          EmbedData.TaskType.CLUSTERING -> {
        text = formatQuery(embedData);
      }
      default -> {
        text = formatQuery(embedData);
      }
    }
    return embedData.toBuilder().setData(text).build();
  }

  private String formatQuery(EmbedData<String> embedData) {
    String task =
        switch (embedData.getTask()) {
          case EmbedData.TaskType.RETRIEVAL_QUERY -> "search result";
          case EmbedData.TaskType.RETRIEVAL_DOCUMENT -> "";
          case EmbedData.TaskType.SEMANTIC_SIMILARITY -> "sentence similarity";
          case EmbedData.TaskType.CLASSIFICATION -> "classification";
          case EmbedData.TaskType.CLUSTERING -> "clustering";
          case EmbedData.TaskType.QUESTION_ANSWERING -> "question answering";
          case EmbedData.TaskType.FACT_VERIFICATION -> "fact checking";
          case EmbedData.TaskType.CODE_RETRIEVAL -> "code retrieval";
          default -> "search result";
        };
    return String.format(QUERY_TEMPLATE, task, embedData.getData());
  }

  private String formatDocument(EmbedData<String> embedData) {
    String title =
        !embedData.getMetadata().containsKey(TITLE_KEY)
            ? "none"
            : (String) embedData.getMetadata().get(TITLE_KEY);
    return String.format(DOCUMENT_TEMPLATE, title, embedData.getData());
  }
}
