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
import com.google.ai.edge.localagents.core.proto.FunctionCall;
import com.google.ai.edge.localagents.core.proto.FunctionDeclaration;
import com.google.ai.edge.localagents.core.proto.GenerateContentResponse;
import com.google.ai.edge.localagents.core.proto.Part;
import com.google.ai.edge.localagents.core.proto.Tool;
import com.google.ai.edge.localagents.fc.FunctionCallException.FunctionCallStatus;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.concurrent.ExecutionException;

/**
 * A GenerativeModel is a wrapper around an inference backend that provides a simple interface for
 * generating content.
 */
public final class GenerativeModel {

  private final InferenceBackend backend;
  private final Content systemInstruction;
  private List<Tool> tools = new ArrayList<>();

  /**
   * Constructs a new GenerativeModel with the given backend and prompt formatter.
   *
   * @param backend The inference backend to use.
   */
  public GenerativeModel(InferenceBackend backend) {
    this.backend = backend;
    this.systemInstruction = Content.getDefaultInstance();
  }

  /**
   * Constructs a new GenerativeModel with the given backend, formatter, and system instruction.
   *
   * @param backend The inference backend to use.
   * @param systemInstruction The system instruction to use for all requests.
   */
  public GenerativeModel(InferenceBackend backend, Content systemInstruction) {
    this.backend = backend;
    this.systemInstruction = systemInstruction;
  }

  /**
   * Constructs a new GenerativeModel with the given backend, formatter, system instruction, and
   * tools.
   *
   * @param backend The inference backend to use.
   * @param systemInstruction The system instruction to use for all requests.
   * @param tools The tools to use for all requests.
   */
  public GenerativeModel(InferenceBackend backend, Content systemInstruction, List<Tool> tools) {
    this.backend = backend;
    this.systemInstruction = systemInstruction;
    this.tools = tools;
  }

  /**
   * Generates a model message from the given conversation.
   *
   * <p>This method is a stateless alternative to generate a response from the model.
   *
   * @param contents The conversation to use for generation.
   * @return The generated response from the model.
   * @throws FunctionCallException if the model predicts an invalid function call.
   */
  public GenerateContentResponse generateContent(List<Content> contents)
      throws InterruptedException, ExecutionException, FunctionCallException {
    Session session = this.backend.createSession();
    session.addSystemMessage(systemInstruction, tools);
    for (Content content : contents) {
      session.addMessage(content);
    }
    var responseContents = session.generateResponse().get();
    var response = GenerateContentResponse.newBuilder();
    for (Content responseContent : responseContents) {
      validateFunctionCalls(responseContent);
      response.addCandidates(Candidate.newBuilder().setContent(responseContent));
    }
    return response.build();
  }

  /**
   * Starts a new chat session with the model.
   *
   * @return A new chat session.
   */
  public ChatSession startChat() {
    Session session = this.backend.createSession();
    session.addSystemMessage(systemInstruction, tools);
    return new ChatSession(this, session);
  }

  /**
   * Validates the function calls in the given content by comparing it to the declared tools. Throws
   * a FunctionCallException if any function call is invalid.
   *
   * <p>Content parts that are not function calls are ignored.
   *
   * @param content The content to validate.
   * @throws FunctionCallException if the model predicts an invalid function call.
   */
  void validateFunctionCalls(Content content) throws FunctionCallException {
    for (Part part : content.getPartsList()) {
      if (part.hasFunctionCall()) {
        var status = validateFunctionCall(part.getFunctionCall());
        if (status != FunctionCallStatus.VALID) {
          throw new FunctionCallException(part.getFunctionCall(), status);
        }
      }
    }
  }

  /**
   * Validates the function call against the declared tools.
   *
   * @param functionCall The function call to validate.
   * @return An enum indicating if the function call is valid or the reason why it is invalid.
   */
  private FunctionCallStatus validateFunctionCall(FunctionCall functionCall) {
    Optional<FunctionDeclaration> matchingFunctionDeclaration =
        tools.stream()
            .flatMap(tool -> tool.getFunctionDeclarationsList().stream())
            .filter(
                functionDeclaration -> functionDeclaration.getName().equals(functionCall.getName()))
            .findFirst();

    if (!matchingFunctionDeclaration.isPresent()) {
      return FunctionCallStatus.INVALID_FUNCTION_NAME;
    }

    for (String arg : functionCall.getArgs().getFieldsMap().keySet()) {
      var parameters = matchingFunctionDeclaration.get().getParameters();
      if (!parameters.getPropertiesMap().containsKey(arg)) {
        return FunctionCallStatus.INVALID_PARAMETER_NAME;
      }
    }

    if (matchingFunctionDeclaration.get().getParameters().getRequiredList().stream()
        .anyMatch(
            requiredParam -> !functionCall.getArgs().getFieldsMap().containsKey(requiredParam))) {
      return FunctionCallStatus.MISSING_REQUIRED_PARAMETER;
    }

    return FunctionCallStatus.VALID;
  }
}
