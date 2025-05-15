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

import static com.google.common.util.concurrent.Futures.immediateFuture;

import com.google.ai.edge.localagents.core.proto.Content;
import com.google.ai.edge.localagents.core.proto.Tool;
import com.google.ai.edge.localagents.fc.proto.ConstraintOptions;
import com.google.common.collect.ImmutableList;
import com.google.common.util.concurrent.ListenableFuture;
import com.google.mediapipe.tasks.genai.llminference.LlmInference;
import com.google.mediapipe.tasks.genai.llminference.LlmInferenceSession;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

/**
 * A session for interacting with the LLM inference backend.
 *
 * <p>This class provides an implementation of the {@link Session} interface, using the {@link
 * LlmInferenceSession} as the underlying backend.
 */
final class LlmInferenceBackendSession implements Session {
  private final LlmInferenceSession llmInferenceSession;
  private final LlmInference llmInference;
  private final ModelFormatter formatter;
  private Content systemInstruction;
  private List<Tool> tools;
  private List<Content> history = new ArrayList<>();
  private final Optional<ConstraintProvider> constraintProvider;
  private ConstraintProvider.Constraint constraint;

  LlmInferenceBackendSession(
      LlmInferenceSession llmInferenceSession,
      LlmInference llmInference,
      ModelFormatter formatter,
      Optional<ConstraintProvider> constraintProvider) {
    this.llmInferenceSession = llmInferenceSession;
    this.llmInference = llmInference;
    this.formatter = formatter;
    this.constraintProvider = constraintProvider;
  }

  /**
   * Adds a system message to the session.
   *
   * @param systemInstruction The system instruction to add.
   * @param tools The tools available to the model.
   */
  @Override
  public void addSystemMessage(Content systemInstruction, List<Tool> tools) {
    this.systemInstruction = systemInstruction;
    this.tools = new ArrayList<>(tools);
    var systemMessage = formatter.formatSystemMessage(systemInstruction, tools);
    llmInferenceSession.addQueryChunk(systemMessage);
  }

  /**
   * Adds a message to the session.
   *
   * @param content The content to add.
   */
  @Override
  public void addMessage(Content content) {
    history.add(content);
    var queryChunk = formatter.formatContent(content);
    llmInferenceSession.addQueryChunk(queryChunk);
  }

  /**
   * Generates a response from the backend.
   *
   * @return A future containing the list of content candidates.
   */
  @Override
  public ListenableFuture<List<Content>> generateResponse() throws FunctionCallException {
    // LLM Inference backend does not allow empty input.
    if (!formatter.startModelTurn().isEmpty()) {
      llmInferenceSession.addQueryChunk(formatter.startModelTurn());
    }
    var responseString = llmInferenceSession.generateResponse();
    var generateContentResponse = formatter.parseResponse(responseString);
    var candidateContents = new ArrayList<Content>();
    if (generateContentResponse != null) {
      for (var candidate : generateContentResponse.getCandidatesList()) {
        candidateContents.add(candidate.getContent());
      }
    }
    if (!candidateContents.isEmpty()) {
      history.add(candidateContents.get(0));
    }
    return immediateFuture(candidateContents);
  }

  /**
   * Gets the history of content added to the session.
   *
   * @return A list of content representing the message history of the session.
   */
  @Override
  public ImmutableList<Content> getHistory() {
    return ImmutableList.copyOf(history);
  }

  /**
   * Creates a clone of the session.
   *
   * <p>This method creates a new session with the same system instruction, tools, and history.
   *
   * @return A new session with the same system instruction, tools, and history.
   */
  @Override
  public Session clone() {
    try {
      var clone =
          new LlmInferenceBackendSession(
              llmInferenceSession.cloneSession(),
              this.llmInference,
              formatter,
              this.constraintProvider);
      clone.history = new ArrayList<>(history);
      return clone;
    } catch (Throwable t) {
      // The underlying LlmInferenceSession does not support cloning. So we need to create a new
      // session and manually copy the history.
      var clone =
          new LlmInferenceBackendSession(
              LlmInferenceSession.createFromOptions(
                  this.llmInference, llmInferenceSession.getSessionOptions()),
              this.llmInference,
              formatter,
              this.constraintProvider);
      clone.addSystemMessage(systemInstruction, tools);
      for (var content : history) {
        clone.addMessage(content);
      }
      return clone;
    }
  }

  /** LlmInferenceSession does not support rewinding. */
  @Override
  public ImmutableList<Content> rewind() {
    throw new UnsupportedOperationException(
        "Rewind is not supported by LlmInferenceBackendSession.");
  }

  /** Closes the session. */
  @Override
  public void close() {
    llmInferenceSession.close();
  }

  @Override
  public void enableConstrainedDecoding(ConstraintOptions options) {
    if (!this.constraintProvider.isPresent()) {
      throw new IllegalStateException("Constrained decoding is not supported by this model.");
    }
    this.constraint = constraintProvider.get().createConstraint(this.tools, options);
    llmInferenceSession.updateSessionOptions(
        (optionsBuilder) ->
            optionsBuilder.setConstraintHandle(this.constraint.getConstraintHandle()).build());
  }

  @Override
  public void disableConstrainedDecoding() {
    llmInferenceSession.updateSessionOptions(
        (optionsBuilder) -> optionsBuilder.setConstraintHandle(0).build());
  }
}
