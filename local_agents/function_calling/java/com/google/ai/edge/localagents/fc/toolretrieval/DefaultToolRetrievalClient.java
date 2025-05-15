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
package com.google.ai.edge.localagents.fc.toolretrieval;

import com.google.ai.edge.localagents.core.proto.FunctionDeclaration;
import com.google.ai.edge.localagents.core.proto.Tool;
import com.google.ai.edge.localagents.rag.memory.SemanticMemory;
import com.google.ai.edge.localagents.rag.retrieval.RetrievalConfig;
import com.google.ai.edge.localagents.rag.retrieval.RetrievalRequest;
import com.google.common.collect.ImmutableList;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.ExecutionException;

/**
 * A default implementation of {@link ToolRetrieval} that uses a {@link SemanticMemory} to store and
 * retrieve tool information.
 *
 * <p>This client uses a {@link SemanticMemory} to store tool information, including function
 * declarations and raw text entries. It uses a {@link ToolFormatter} to format the tool information
 * into a searchable format.
 */
public final class DefaultToolRetrievalClient implements ToolRetrieval {
  private final SemanticMemory<String> memory;
  private final ToolFormatter toolFormatter;
  private final int topK;
  private final float minSimilarityScore;

  /**
   * Constructs a new {@link DefaultToolRetrievalClient}.
   *
   * @param memory the {@link SemanticMemory} to use for storing and retrieving tool information
   * @param toolFormatter the {@link ToolFormatter} to use for formatting tool information
   * @param topK the number of top results to retrieve
   * @param minSimilarityScore the minimum similarity score for a result to be considered
   */
  public DefaultToolRetrievalClient(
      SemanticMemory<String> memory,
      ToolFormatter toolFormatter,
      int topK,
      float minSimilarityScore) {
    this.toolFormatter = toolFormatter;
    this.memory = memory;
    this.topK = topK;
    this.minSimilarityScore = minSimilarityScore;
  }

  /**
   * Initializes the index for a given tool.
   *
   * @param tool the tool to initialize the index for
   * @param metadata the metadata for the tool
   * @return true if the index was initialized successfully, false otherwise
   */
  @Override
  public Boolean initializeIndex(Tool tool, Optional<ToolMetadata> metadata) {
    for (FunctionDeclaration functionDeclaration : tool.getFunctionDeclarationsList()) {
      Optional<ToolMetadata.FunctionMetadata> functionMetadata;
      if (metadata.isPresent()) {
        functionMetadata = metadata.get().getFunctionMetadata(functionDeclaration.getName());
      } else {
        functionMetadata = Optional.empty();
      }
      try {
        Boolean result =
            memory
                .recordMemoryEntry(
                    toolFormatter.formatFunctionDeclaration(functionDeclaration, functionMetadata))
                .get();
        if (result == null || !result) {
          return false;
        }
      } catch (ExecutionException | InterruptedException e) {
        return false;
      }
    }
    return true;
  }

  /**
   * Retrieves the names of tools that match the given query.
   *
   * @param query the query to search for
   * @return a list of tool names that match the query
   */
  @Override
  public ImmutableList<String> retrieveToolNames(String query) {
    try {
      return toolFormatter.getToolNames(
          memory
              .retrieveResults(
                  RetrievalRequest.create(
                      query,
                      RetrievalConfig.create(
                          topK, minSimilarityScore, RetrievalConfig.TaskType.RETRIEVAL_QUERY)))
              .get());
    } catch (ExecutionException | InterruptedException e) {
      return ImmutableList.of();
    }
  }

  /**
   * Adds raw text entries to the index.
   *
   * @param textEntries the list of text entries to add
   * @param metadata the list of metadata for each text entry
   * @return true if the text entries were added successfully, false otherwise
   */
  @Override
  public Boolean addRawText(List<String> textEntries, List<Map<String, String>> metadata) {
    if (textEntries == null || metadata == null || textEntries.size() != metadata.size()) {
      return false;
    }
    for (int i = 0; i < textEntries.size(); i++) {
      try {
        Boolean result =
            memory
                .recordMemoryEntry(
                    toolFormatter.formatTextEntry(textEntries.get(i), metadata.get(i)))
                .get();
        if (result == null || !result) {
          return false;
        }
      } catch (ExecutionException | InterruptedException e) {
        return false;
      }
    }
    return true;
  }
}
