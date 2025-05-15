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
import com.google.ai.edge.localagents.rag.retrieval.RetrievalEntity;
import com.google.ai.edge.localagents.rag.retrieval.RetrievalResponse;
import com.google.ai.edge.localagents.rag.retrieval.SemanticDataEntry;
import com.google.common.collect.ImmutableList;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Optional;

/**
 * A default implementation of {@link ToolFormatter} that formats function declarations and text
 * entries into a {@link SemanticDataEntry} for retrieval.
 *
 * <p>This formatter extracts the name and description from the {@link FunctionDeclaration} and
 * formats them into a string for retrieval. It also extracts examples from the provided {@link
 * ToolMetadata.FunctionMetadata} if available. For text entries, it simply stores the text and
 * associated metadata.
 */
public final class DefaultToolFormatter implements ToolFormatter {
  private static final String NAME_METADATA_KEY = "name";
  private static final String EXAMPLES_METADATA_KEY = "examples";

  /** Constructs a new {@link DefaultToolFormatter}. */
  public DefaultToolFormatter() {}

  /**
   * Formats a {@link FunctionDeclaration} into a {@link SemanticDataEntry}.
   *
   * <p>The formatted entry includes the function name, description, and examples (if provided).
   *
   * @param functionDeclaration The function declaration to format.
   * @param formattingMetadata Optional metadata for the function.
   * @return A {@link SemanticDataEntry} containing the formatted function information.
   */
  @Override
  public SemanticDataEntry<String> formatFunctionDeclaration(
      FunctionDeclaration functionDeclaration,
      Optional<ToolMetadata.FunctionMetadata> formattingMetadata) {
    SemanticDataEntry.Builder<String> dataEntry = SemanticDataEntry.builder();
    StringBuilder description = new StringBuilder();
    description.append("Name: ").append(functionDeclaration.getName()).append("\n");
    description.append("Description: ").append(functionDeclaration.getDescription()).append("\n");
    if (formattingMetadata.isPresent()) {
      if (formattingMetadata.get().getAttribute(EXAMPLES_METADATA_KEY).isPresent()) {
        description
            .append("Examples: ")
            .append(formattingMetadata.get().getAttribute(EXAMPLES_METADATA_KEY).get());
      }
    }
    return dataEntry
        .setData(description.toString())
        .addMetadata(NAME_METADATA_KEY, functionDeclaration.getName())
        .build();
  }

  /**
   * Extracts a list of tool names from a {@link RetrievalResponse}.
   *
   * <p>It iterates through the retrieved entities and extracts the tool name from the metadata.
   *
   * @param response The retrieval response containing the entities.
   * @return A list of tool names.
   */
  @Override
  public ImmutableList<String> getToolNames(RetrievalResponse<String> response) {
    List<String> toolNames = new ArrayList<>();
    for (RetrievalEntity<String> entity : response.getEntities()) {
      String name = (String) entity.getMetadata().get(NAME_METADATA_KEY);
      if (name != null) {
        toolNames.add(name);
      }
    }
    return ImmutableList.copyOf(toolNames);
  }

  /**
   * Formats a text entry and its metadata into a {@link SemanticDataEntry}.
   *
   * <p>The formatted entry includes the text and all provided metadata.
   *
   * @param text The text entry.
   * @param metadata A map of metadata associated with the text entry.
   * @return A {@link SemanticDataEntry} containing the text and metadata.
   */
  @Override
  public SemanticDataEntry<String> formatTextEntry(String text, Map<String, String> metadata) {
    SemanticDataEntry.Builder<String> dataEntry = SemanticDataEntry.builder();
    dataEntry.setData(text);
    for (Map.Entry<String, String> entry : metadata.entrySet()) {
      dataEntry.addMetadata(entry.getKey(), entry.getValue());
    }
    return dataEntry.build();
  }
}
