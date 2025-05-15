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

import com.google.ai.edge.localagents.core.proto.Candidate;
import com.google.ai.edge.localagents.core.proto.Content;
import com.google.ai.edge.localagents.core.proto.GenerateContentResponse;
import com.google.ai.edge.localagents.core.proto.Part;
import com.google.ai.edge.localagents.fc.proto.ConstraintOptions;
import com.google.auto.value.AutoValue;
import com.google.common.collect.ImmutableList;
import com.google.common.collect.Iterables;
import java.util.List;
import java.util.concurrent.ExecutionException;
import org.jspecify.annotations.Nullable;

/**
 * A ChatSession represents a single conversation between a user and a generative AI model. It
 * maintains a history of messages sent and received, and provides methods for sending new messages,
 * rewinding the conversation, and accessing the last message sent or received.
 */
public final class ChatSession {
  private final GenerativeModel generativeModel;
  private final Session session;

  /**
   * Constructs a new ChatSession with the given Session.
   *
   * @param session The backend Session to use for the ChatSession.
   */
  ChatSession(GenerativeModel generativeModel, Session session) {
    this.generativeModel = generativeModel;
    this.session = session;
  }

  /**
   * Sends a message to the generative AI model.
   *
   * @param content The content of the message.
   * @return The response from the generative AI model.
   * @throws ExecutionException if the response future fails.
   * @throws FunctionCallException if the response contains invalid function calls.
   */
  public GenerateContentResponse sendMessage(Content content)
      throws ExecutionException, FunctionCallException {
    session.addMessage(content);
    List<Content> response;
    try {
      response = session.generateResponse().get();
    } catch (InterruptedException e) {
      throw new ExecutionException(e);
    }
    GenerateContentResponse.Builder responseBuilder = GenerateContentResponse.newBuilder();
    for (Content contentItem : response) {
      generativeModel.validateFunctionCalls(contentItem);
      responseBuilder.addCandidates(Candidate.newBuilder().setContent(contentItem));
    }
    return responseBuilder.build();
  }

  /**
   * Sends a text message to the generative AI model.
   *
   * @param text The text of the message.
   * @return The response from the generative AI model.
   * @throws ExecutionException if the response future fails.
   * @throws FunctionCallException if the response contains invalid function calls.
   */
  public GenerateContentResponse sendMessage(String text)
      throws ExecutionException, FunctionCallException {
    Content content =
        Content.newBuilder().setRole("user").addParts(Part.newBuilder().setText(text)).build();
    return sendMessage(content);
  }

  /**
   * Rewinds the conversation by the most recent user and model messages.
   *
   * @return A RewindResult containing the last sent and received messages, or null if there are
   *     fewer than two messages in the conversation.
   */
  public @Nullable RewindResult rewind() {
    var removedMessages = session.rewind();
    if (removedMessages.size() < 2) {
      return null;
    }
    var lastSent = removedMessages.get(0);
    var lastReceived = removedMessages.get(1);
    return RewindResult.create(lastSent, lastReceived);
  }

  /**
   * Gets the history of messages in the conversation.
   *
   * @return The history of messages.
   */
  public ImmutableList<Content> getHistory() {
    return session.getHistory();
  }

  /**
   * Gets the last message in the conversation.
   *
   * @return The last message, or null if there are no messages in the conversation.
   */
  public @Nullable Content getLast() {
    var history = session.getHistory();
    return history.isEmpty() ? null : Iterables.getLast(history);
  }

  /**
   * Clones the current ChatSession, creating a new session with the same history.
   *
   * @return A new ChatSession with the same history as the current one.
   */
  @Override
  public ChatSession clone() {
    return new ChatSession(generativeModel, session.clone());
  }

  /** Closes the session. */
  public void close() {
    session.close();
  }

  /**
   * A RewindResult represents the result of rewinding a conversation. It contains the last sent and
   * received messages.
   */
  @AutoValue
  public abstract static class RewindResult {
    /**
     * Constructs a new RewindResult with the given last sent and received messages.
     *
     * @param lastSent The last sent message.
     * @param lastReceived The last received message.
     */
    public static RewindResult create(Content lastSent, Content lastReceived) {
      return new AutoValue_ChatSession_RewindResult(lastSent, lastReceived);
    }

    /**
     * Gets the last sent message.
     *
     * @return The last sent message.
     */
    public abstract Content lastSent();

    /**
     * Gets the last received message.
     *
     * @return The last received message.
     */
    public abstract Content lastReceived();
  }

  /**
   * Enables constrained decoding for the session.
   *
   * @param options The options for the constraint.
   */
  public void enableConstraint(ConstraintOptions options) {
    session.enableConstrainedDecoding(options);
  }

  /** Disables constrained decoding for the session. */
  public void disableConstraint() {
    session.disableConstrainedDecoding();
  }
}
