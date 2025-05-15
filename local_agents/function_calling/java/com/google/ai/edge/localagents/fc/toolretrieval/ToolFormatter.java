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
import com.google.ai.edge.localagents.rag.retrieval.RetrievalResponse;
import com.google.ai.edge.localagents.rag.retrieval.SemanticDataEntry;
import com.google.common.collect.ImmutableList;
import java.util.Map;
import java.util.Optional;

/**
 * An interface for formatting different types of tool data into a {@link SemanticDataEntry}. This
 * interface is used to format function declarations and text entries into a common format for
 * retrieval and use in the LLM.
 */
public interface ToolFormatter {

  /**
   * Formats a {@link FunctionDeclaration} into a {@link SemanticDataEntry}.
   *
   * @param functionDeclaration The function declaration to format.
   * @param metadata Optional metadata for the function.
   * @return A {@link SemanticDataEntry} containing the formatted function declaration.
   */
  public SemanticDataEntry<String> formatFunctionDeclaration(
      FunctionDeclaration functionDeclaration, Optional<ToolMetadata.FunctionMetadata> metadata);

  /**
   * Extracts a list of tool names from a {@link RetrievalResponse}.
   *
   * @param response The retrieval response containing tool data.
   * @return An {@link ImmutableList} of tool names.
   */
  public ImmutableList<String> getToolNames(RetrievalResponse<String> response);

  /**
   * Formats a text entry with metadata into a {@link SemanticDataEntry}.
   *
   * @param text The text to format.
   * @param metadata A map of metadata associated with the text.
   * @return A {@link SemanticDataEntry} containing the formatted text and metadata.
   */
  public SemanticDataEntry<String> formatTextEntry(String text, Map<String, String> metadata);
}
