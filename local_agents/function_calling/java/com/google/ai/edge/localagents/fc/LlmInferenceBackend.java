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

import android.util.Log;
import com.google.mediapipe.tasks.genai.llminference.LlmInference;
import com.google.mediapipe.tasks.genai.llminference.LlmInferenceSession;
import com.google.mediapipe.tasks.genai.llminference.LlmInferenceSession.LlmInferenceSessionOptions;
import java.util.Optional;

/**
 * An implementation of {@link InferenceBackend} that uses the MediaPipe {@link LlmInference} task
 * for Large Language Model inference.
 */
public final class LlmInferenceBackend implements InferenceBackend {
  private final LlmInference llmInference;
  private final LlmInferenceSessionOptions sessionOptions;
  private final ModelFormatter formatter;
  private final Optional<ConstraintProvider> constraintProvider;

  public LlmInferenceBackend(
      LlmInference llmInference, LlmInferenceSessionOptions options, ModelFormatter formatter) {
    this.llmInference = llmInference;
    this.sessionOptions = options;
    this.formatter = formatter;
    Optional<ConstraintProvider> tmpConstraintProvider = Optional.empty();
    // Only Gemma3 model support Fst constraints.
    try {
      tmpConstraintProvider =
          Optional.of(new FstConstraintProvider(llmInference.getSentencePieceProcessorHandle()));
      Log.i(
          this.getClass().getSimpleName(),
          "FST constraint provider created. Constrained decoding is supported by this model.");
    } catch (IllegalStateException e) {
      Log.i(
          this.getClass().getSimpleName(), "Constrained decoding is not supported by this model.");
    }
    this.constraintProvider = tmpConstraintProvider;
  }

  public LlmInferenceBackend(LlmInference llmInference, ModelFormatter formatter) {
    this(llmInference, LlmInferenceSessionOptions.builder().build(), formatter);
  }

  @Override
  public Session createSession() {
    var session = LlmInferenceSession.createFromOptions(llmInference, sessionOptions);
    return new LlmInferenceBackendSession(session, llmInference, formatter, constraintProvider);
  }

  @Override
  public void close() {
    llmInference.close();
  }
}
