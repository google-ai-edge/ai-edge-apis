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
import com.google.ai.edge.localagents.fc.FunctionCallException.FunctionCallStatus;
import com.google.protobuf.ExtensionRegistryLite;
import com.google.protobuf.InvalidProtocolBufferException;
import java.util.List;

/** Formats requests and parses responses for Llama. */
public final class LlamaFormatter implements ModelFormatter {
  private final ModelFormatterOptions formatterOptions;
  private final com.google.ai.edge.localagents.fc.proto.ModelFormatterOptions formatterOptionsProto;

  static {
    System.loadLibrary("jni_llama_formatter_android");
  }

  public LlamaFormatter() {
    this(ModelFormatterOptions.builder().build());
  }

  public LlamaFormatter(ModelFormatterOptions formatterOptions) {
    this.formatterOptions = formatterOptions;
    this.formatterOptionsProto = formatterOptions.toProto();
  }

  @Override
  public String formatSystemMessage(Content systemInstruction, List<Tool> tools) {
    GenerateContentRequest request =
        GenerateContentRequest.newBuilder()
            .setSystemInstruction(systemInstruction)
            .addAllTools(tools)
            .build();
    return nativeFormatSystemMessage(
        request.toByteArray(), this.formatterOptionsProto.toByteArray());
  }

  @Override
  public String formatContent(Content content) {
    return nativeFormatContent(content.toByteArray(), this.formatterOptionsProto.toByteArray());
  }

  @Override
  public String startModelTurn() {
    return nativeStartModelTurn(this.formatterOptionsProto.toByteArray());
  }

  @Override
  public String formatRequest(GenerateContentRequest request) {
    return nativeFormatRequest(request.toByteArray(), this.formatterOptionsProto.toByteArray());
  }

  @Override
  public GenerateContentResponse parseResponse(String response) throws FunctionCallException {
    byte[] responseBytes = nativeParseResponse(response);
    if (responseBytes == null) {
      throw new FunctionCallException(/* functionCall= */ null, FunctionCallStatus.PARSE_ERROR);
    }
    try {
      return GenerateContentResponse.parseFrom(
          responseBytes, ExtensionRegistryLite.getEmptyRegistry());
    } catch (InvalidProtocolBufferException e) {
      throw new FunctionCallException(/* functionCall= */ null, FunctionCallStatus.PARSE_ERROR, e);
    }
  }

  private static native String nativeFormatSystemMessage(byte[] requestBytes, byte[] options);

  private static native String nativeFormatContent(byte[] contentBytes, byte[] options);

  private static native String nativeStartModelTurn(byte[] options);

  private static native String nativeFormatRequest(byte[] requestBytes, byte[] options);

  private static native byte[] nativeParseResponse(String output);
}
