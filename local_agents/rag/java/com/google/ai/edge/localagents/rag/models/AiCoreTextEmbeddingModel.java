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

import static com.google.common.collect.ImmutableList.toImmutableList;
import static com.google.common.util.concurrent.Futures.immediateFuture;

import android.content.Context;
import android.util.Log;
import androidx.annotation.VisibleForTesting;
import androidx.core.content.ContextCompat;
import com.google.android.apps.aicore.client.api.AiCoreClient;
import com.google.android.apps.aicore.client.api.AiCoreClientOptions;
import com.google.android.apps.aicore.client.api.AiFeature;
import com.google.android.apps.aicore.client.api.DownloadCallback;
import com.google.android.apps.aicore.client.api.textembedding.TextEmbeddingMessage;
import com.google.android.apps.aicore.client.api.textembedding.TextEmbeddingRequest;
import com.google.android.apps.aicore.client.api.textembedding.TextEmbeddingService;
import com.google.android.apps.aicore.client.api.textembedding.TextEmbeddingServiceOptions;
import com.google.common.collect.ImmutableList;
import com.google.common.primitives.Floats;
import com.google.common.util.concurrent.Futures;
import com.google.common.util.concurrent.ListenableFuture;
import java.util.concurrent.Executor;
import org.jspecify.annotations.Nullable;

/** The text embedding model provided by AICore. */
public final class AiCoreTextEmbeddingModel implements Embedder<String> {
  private static final String TAG = AiCoreTextEmbeddingModel.class.getSimpleName();
  private static final int EMBEDDING_FEATURE_TYPE = AiFeature.Type.TEXT_EMBEDDING;

  private final AiCoreClient aiCoreClient;
  private TextEmbeddingService textEmbeddingService;
  private final Executor workerExecutor;
  private final @Nullable EmbeddingDataProcessor<String> embeddingDataProcessor;

  public AiCoreTextEmbeddingModel(Context context) {
    this(context, ContextCompat.getMainExecutor(context), null);
  }

  public AiCoreTextEmbeddingModel(
      Context context,
      Executor workerExecutor,
      @Nullable EmbeddingDataProcessor<String> embeddingDataProcessor) {
    this.aiCoreClient = AiCoreClient.create(AiCoreClientOptions.builder(context).build());
    this.workerExecutor = workerExecutor;
    this.embeddingDataProcessor = embeddingDataProcessor;
  }

  @VisibleForTesting
  public AiCoreTextEmbeddingModel(
      AiCoreClient aiCoreClient,
      TextEmbeddingService textEmbeddingService,
      Executor workerExecutor,
      @Nullable EmbeddingDataProcessor<String> embeddingDataProcessor) {
    this.aiCoreClient = aiCoreClient;
    this.textEmbeddingService = textEmbeddingService;
    this.workerExecutor = workerExecutor;
    this.embeddingDataProcessor = embeddingDataProcessor;
  }

  public ListenableFuture<Boolean> initialize() {
    Log.i(TAG, "Initializing AICore.");
    if (aiCoreClient == null) {
      Log.i(TAG, "AICore client is null.");
      return immediateFuture(false);
    } else {
      Log.i(TAG, "AICore client created.");
    }
    return Futures.transform(
        aiCoreClient.listFeatures(),
        features -> {
          Log.i(TAG, "Received features, size: " + features.size());
          if (features.isEmpty()) {
            Log.i(TAG, "AiCore list-feature returned without any results.");
            return false;
          }
          for (AiFeature aiFeature : features) {
            if (aiFeature.getType() == EMBEDDING_FEATURE_TYPE) {
              Log.i(TAG, "create text embedding service with model " + aiFeature);
              if (textEmbeddingService == null) {
                textEmbeddingService =
                    TextEmbeddingService.create(
                        TextEmbeddingServiceOptions.builder(aiCoreClient)
                            .setFeature(aiFeature)
                            .setDownloadCallback(new DownloadCallback() {})
                            .build());
              }
              return textEmbeddingService != null;
            }
            Log.i(TAG, "got feature " + aiFeature);
          }
          return textEmbeddingService != null;
        },
        workerExecutor);
  }

  public ListenableFuture<Boolean> prepare() {
    return Futures.transform(
        textEmbeddingService.prepareInferenceEngine(),
        result -> {
          Log.i(TAG, "Prepare the inference engine succeed.");
          return true;
        },
        workerExecutor);
  }

  @Override
  public ListenableFuture<ImmutableList<Float>> getEmbeddings(EmbeddingRequest<String> request) {
    EmbedData<String> embedData = request.getEmbedData().get(0);
    if (embeddingDataProcessor != null) {
      embedData = embeddingDataProcessor.process(embedData);
    }
    ImmutableList<TextEmbeddingMessage> messages =
        ImmutableList.of(TextEmbeddingMessage.create(embedData.getData()));
    TextEmbeddingRequest aicoreRequest = TextEmbeddingRequest.builder(messages).build();
    return Futures.transform(
        textEmbeddingService.runInference(aicoreRequest),
        result -> {
          Log.i(TAG, "get text embedding response : " + result);
          float[] embedding = result.getResponses().get(0).getEmbedding();
          return ImmutableList.copyOf(Floats.asList(embedding));
        },
        workerExecutor);
  }

  @Override
  public ListenableFuture<ImmutableList<ImmutableList<Float>>> getBatchEmbeddings(
      EmbeddingRequest<String> request) {
    ImmutableList<TextEmbeddingMessage> messages =
        request.getEmbedData().stream()
            .map(
                embedData -> {
                  if (embeddingDataProcessor != null) {
                    embedData = embeddingDataProcessor.process(embedData);
                  }
                  return TextEmbeddingMessage.create(embedData.getData());
                })
            .collect(toImmutableList());
    TextEmbeddingRequest aicoreRequest = TextEmbeddingRequest.builder(messages).build();
    return Futures.transform(
        textEmbeddingService.runInference(aicoreRequest),
        result -> {
          Log.i(TAG, "get text embedding response : " + result);
          return result.getResponses().stream()
              .map(entry -> ImmutableList.copyOf(Floats.asList(entry.getEmbedding())))
              .collect(toImmutableList());
        },
        workerExecutor);
  }
}
