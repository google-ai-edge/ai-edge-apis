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

import com.google.ai.edge.localagents.core.proto.Tool;
import com.google.common.collect.ImmutableList;
import java.util.List;
import java.util.Map;
import java.util.Optional;

/**
 * An interface for retrieving relevant tools based on a given query.
 *
 * <p>This interface defines methods for initializing a tool index, adding raw text entries,
 * retrieving tool names.
 */
public interface ToolRetrieval {

  /**
   * Retrieves a list of tool names relevant to the given query.
   *
   * @param query The user's query.
   * @return A list of tool names relevant to the query.
   */
  public ImmutableList<String> retrieveToolNames(String query);

  /**
   * Initializes the tool index with a given tool and its metadata.
   *
   * @param tool The tool to be indexed.
   * @param metadata The metadata associated with the tool.
   * @return True if the index was initialized successfully, false otherwise.
   */
  public Boolean initializeIndex(Tool tool, Optional<ToolMetadata> metadata);

  /**
   * Adds raw text entries and their corresponding metadata to the index.
   *
   * @param textEntries A list of text entries to be added to the index.
   * @param metadata A list of metadata associated with each text entry.
   * @return True if the text entries were added successfully, false otherwise.
   */
  public Boolean addRawText(List<String> textEntries, List<Map<String, String>> metadata);
}
