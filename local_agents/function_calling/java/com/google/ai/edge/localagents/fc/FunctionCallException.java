package com.google.ai.edge.localagents.fc;

import com.google.ai.edge.localagents.core.proto.FunctionCall;
import org.jspecify.annotations.Nullable;

/**
 * Exception that represents an error during function call processing. It encapsulates the {@link
 * FunctionCall} that caused the error and the {@link FunctionCallStatus} indicating the type of
 * error.
 */
public final class FunctionCallException extends Exception {
  /** Enum representing whether a function call is valid or the reason why it is invalid. */
  public enum FunctionCallStatus {
    VALID,
    PARSE_ERROR,
    INVALID_FUNCTION_NAME,
    INVALID_PARAMETER_NAME,
    MISSING_REQUIRED_PARAMETER
  }

  private final @Nullable FunctionCall functionCall;
  private final FunctionCallStatus status;

  public FunctionCallException(@Nullable FunctionCall functionCall, FunctionCallStatus status) {
    this.functionCall = functionCall;
    this.status = status;
  }

  public FunctionCallException(
      @Nullable FunctionCall functionCall, FunctionCallStatus status, Throwable cause) {
    super(cause);
    this.functionCall = functionCall;
    this.status = status;
  }

  public @Nullable FunctionCall getFunctionCall() {
    return functionCall;
  }

  public FunctionCallStatus getStatus() {
    return status;
  }
}
