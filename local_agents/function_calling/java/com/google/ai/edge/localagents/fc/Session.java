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
import com.google.ai.edge.localagents.core.proto.Tool;
import com.google.ai.edge.localagents.fc.proto.ConstraintOptions;
import com.google.common.collect.ImmutableList;
import com.google.common.util.concurrent.ListenableFuture;
import java.util.List;

/** Represents a backend session for interacting with an LLM. */
public interface Session {
  /**
   * Adds a system message to the session history based on the system instruction and available
   * tools.
   */
  public void addSystemMessage(Content systemInstruction, List<Tool> tools);

  /** Adds a message to the session. */
  public void addMessage(Content content);

  /**
   * Generates a response based on the current session history.
   *
   * @return A ListenableFuture that will resolve to a list of Content objects representing the
   *     generated response.
   */
  public ListenableFuture<List<Content>> generateResponse() throws FunctionCallException;

  /**
   * Gets the current session history.
   *
   * @return A list of Content objects representing the current session history.
   */
  public ImmutableList<Content> getHistory();

  /**
   * Rewinds the session's history by removing the last pair of messages.
   *
   * @return The removed messages or an empty list if there are fewer than two messages.
   */
  public ImmutableList<Content> rewind();

  /** Creates a new session with the same configuration and history as the current session. */
  public Session clone();

  /** Closes the session. */
  public void close();

  /** Enables constrained decoding for the session. */
  public void enableConstrainedDecoding(ConstraintOptions options);

  /** Disables constrained decoding for the session. */
  public void disableConstrainedDecoding();
}
