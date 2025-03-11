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
package com.google.ai.edge.localagents.rag.models;

import static com.google.common.util.concurrent.Futures.immediateFuture;

import android.content.Context;
import android.util.Log;
import com.google.common.util.concurrent.Futures;
import com.google.common.util.concurrent.ListenableFuture;
import com.google.mediapipe.tasks.genai.llminference.LlmInference;
import com.google.mediapipe.tasks.genai.llminference.LlmInference.LlmInferenceOptions;
import com.google.mediapipe.tasks.genai.llminference.LlmInferenceSession;
import com.google.mediapipe.tasks.genai.llminference.LlmInferenceSession.LlmInferenceSessionOptions;
import com.google.mediapipe.tasks.genai.llminference.ProgressListener;
import java.io.Closeable;
import java.util.concurrent.Executor;
import java.util.concurrent.Executors;
import java.util.concurrent.atomic.AtomicReference;
import org.jspecify.annotations.Nullable;

/** The language model provided by MediaPipe. */
public final class MediaPipeLlmBackend implements LanguageModel, Closeable {
  private static final String TAG = MediaPipeLlmBackend.class.getSimpleName();
  private static final String NOT_INITIALIZED = "LLM inference is not initialized yet!";

  // The MediaPipe model instance.
  // Set once in the async initialize method and never changed.
  // Cleared when the model is closed.
  private final AtomicReference<@Nullable LlmInference> llmInference = new AtomicReference<>(null);

  // An implicit session for all request that do use the public session API. These sessions are
  // short-lived and are only kept for a single inference.
  private final AtomicReference<@Nullable LlmInferenceSession> implicitSession =
      new AtomicReference<>(null);

  private final Context context;
  private final Executor workerExecutor;
  private final LlmInferenceOptions options;
  private final LlmInferenceSessionOptions sessionOptions;

  /**
   * Creates a new MediaPipe model instance given the MediaPipe options.
   *
   * <p>If you set a streaming callback on the `options`, it will be supported.
   *
   * @param context The application context.
   * @param options The options for the MediaPipe model.
   * @param workerExecutor The executor to use for the initialization of MediaPipe LLM inference.
   */
  public MediaPipeLlmBackend(
      Context context,
      LlmInferenceOptions options,
      LlmInferenceSessionOptions sessionOptions,
      Executor workerExecutor) {
    Log.i(TAG, "Constructor.");
    this.workerExecutor = workerExecutor;
    this.context = context;
    this.options = options;
    this.sessionOptions = sessionOptions;
  }

  /**
   * Creates a new MediaPipe model instance given the MediaPipe options.
   *
   * <p>If you set a streaming callback on the `options`, it will be supported.
   *
   * @param context The application context.
   * @param options The options for the MediaPipe model.
   */
  public MediaPipeLlmBackend(
      Context context, LlmInferenceOptions options, LlmInferenceSessionOptions sessionOptions) {
    this(context, options, sessionOptions, Executors.newSingleThreadExecutor());
  }

  /** Initialize is expected to be to an asynchronous boolean like AICore. */
  public ListenableFuture<Boolean> initialize() {
    return Futures.submit(
        () -> {
          // Construct and initialize the MediaPipe graph. Slow.
          try {
            Log.i(TAG, "Initializing.");
            llmInference.set(LlmInference.createFromOptions(context, options));
            Log.i(TAG, "Initialized.");
            return true;
          } catch (Throwable t) {
            Log.e(TAG, "Failed to initialize MediaPipe model.", t);
            return false;
          }
        },
        workerExecutor);
  }

  @Override
  public ListenableFuture<LanguageModelResponse> generateResponse(
      LanguageModelRequest request, Executor executor) {
    return generateResponse(request, executor, null);
  }

  @Override
  public ListenableFuture<LanguageModelResponse> generateResponse(
      LanguageModelRequest request,
      Executor executor,
      @Nullable AsyncProgressListener<LanguageModelResponse> asyncProgressListener) {
    ProgressListener<String> mpCallback = wrapCallback(asyncProgressListener);

    // If the model is not initialized, immediately log and return a placeholder response.
    // This is congruent with the behavior of the AiCoreModel implementation.
    var model = llmInference.get();
    LlmInferenceSession session = resetImplicitSession();
    if (model == null || session == null) {
      Log.w(TAG, NOT_INITIALIZED);
      mpCallback.run(NOT_INITIALIZED, /* done= */ true);
      return immediateFuture(LanguageModelResponse.create(NOT_INITIALIZED));
    }

    // On the UI thread, send the prompt to the MediaPipe graph and return a settable future.
    var prompt = request.getPrompt();
    Log.d(TAG, "Prompt: " + prompt);
    session.addQueryChunk(prompt);
    return Futures.transform(
        session.generateResponseAsync(mpCallback), LanguageModelResponse::create, executor);
  }

  @Override
  public void close() {
    LlmInferenceSession session = implicitSession.get();
    implicitSession.set(null);
    if (session != null) {
      session.close();
    }
    // The model can only initialize in the constructor.  Once closed, always closed.
    // If you try to use it again for inference, you'll get the NOT_INITIALIZED response.
    var model = llmInference.get();
    llmInference.set(null);
    if (model != null) {
      // If you try to close it while it's running, it will IllegalStateException, yes.
      model.close();
    }
  }

  private ProgressListener<String> wrapCallback(
      @Nullable AsyncProgressListener<LanguageModelResponse> asyncProgressListener) {
    if (asyncProgressListener == null) {
      return (partialResult, done) -> {};
    } else {
      StringBuilder accumlatedResponse = new StringBuilder();
      return (partialResult, done) -> {
        accumlatedResponse.append(partialResult);
        asyncProgressListener.run(
            LanguageModelResponse.create(accumlatedResponse.toString()), done);
      };
    }
  }

  /** Closes the last implicit session and creates a new one without any existing context. */
  private @Nullable LlmInferenceSession resetImplicitSession() {
    LlmInferenceSession session = implicitSession.get();
    if (session != null) {
      session.close();
    }
    var model = llmInference.get();
    session = null;
    if (model != null) {
      session = LlmInferenceSession.createFromOptions(model, sessionOptions);
    }
    implicitSession.set(session);
    return session;
  }
}
