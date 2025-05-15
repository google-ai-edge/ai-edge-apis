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
package com.google.ai.edge.localagents.fc;

import com.google.ai.edge.localagents.core.proto.Content;
import com.google.ai.edge.localagents.core.proto.GenerateContentRequest;
import com.google.ai.edge.localagents.core.proto.GenerateContentResponse;
import com.google.ai.edge.localagents.core.proto.Tool;
import java.util.List;
import org.jspecify.annotations.Nullable;

/** Interface for formatting requests and responses to and from the Generative AI model. */
public interface ModelFormatter {
  /**
   * Formats a system message and tools into a string that can be sent to the inference backend.
   *
   * @param systemInstruction The system instruction to format.
   * @param tools The tools to format.
   * @return The formatted system message string.
   */
  String formatSystemMessage(Content systemInstruction, List<Tool> tools);

  /** Formats a {@link Content} into a string that can be sent to the inference backend. */
  String formatContent(Content content);

  /** Returns a string that indicates the start of a model turn. */
  String startModelTurn();

  /**
   * Formats a {@link GenerateContentRequest} into a string that can be sent to the Generative AI
   * model.
   */
  String formatRequest(GenerateContentRequest request);

  /**
   * Parses a response string from the inference backend into a {@link GenerateContentResponse}.
   *
   * @param response The response string to parse.
   * @return The parsed response, or null if the response could not be parsed.
   */
  @Nullable GenerateContentResponse parseResponse(String response) throws FunctionCallException;
}
