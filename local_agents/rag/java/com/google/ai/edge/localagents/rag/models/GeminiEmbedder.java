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

import static com.google.common.base.Verify.verify;

import android.util.Log;
import com.google.common.base.VerifyException;
import com.google.common.collect.ImmutableList;
import com.google.common.util.concurrent.Futures;
import com.google.common.util.concurrent.ListenableFuture;
import com.google.common.util.concurrent.ThreadFactoryBuilder;
import java.io.IOException;
import java.time.Duration;
import java.util.ArrayList;
import java.util.List;
import java.util.Objects;
import java.util.concurrent.Executor;
import java.util.concurrent.Executors;
import okhttp3.HttpUrl;
import okhttp3.MediaType;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;
import org.checkerframework.checker.nullness.qual.NonNull;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

/** The Gemini embedding API. */
public final class GeminiEmbedder implements Embedder<String> {
  private static final String TAG = GeminiEmbedder.class.getSimpleName();
  private final String apiKey;
  private static final String BASE_URL = "https://generativelanguage.googleapis.com/v1beta/";
  private static final String BATCH_EMBED_TEXT = ":batchEmbedContents";
  private static final String EMBED_TEXT = ":embedContent";
  private final @NonNull String model;
  private static final Duration TIMEOUT = Duration.ofSeconds(60);
  private final OkHttpClient httpClient =
      new OkHttpClient.Builder()
          .connectTimeout(TIMEOUT)
          .readTimeout(TIMEOUT)
          .writeTimeout(TIMEOUT)
          .build();
  private final Executor workerExecutor;

  public GeminiEmbedder(@NonNull String model, @NonNull String apiKey) {
    this.model = model;
    this.apiKey = apiKey;
    workerExecutor =
        Executors.newSingleThreadExecutor(
            new ThreadFactoryBuilder()
                .setNameFormat("gemini-embedder-pool-%d")
                .setPriority(Thread.NORM_PRIORITY)
                .build());
  }

  @Override
  // Returns a list of embedding vectors. Sizes are adjustable (768 default).
  public ListenableFuture<ImmutableList<Float>> getEmbeddings(EmbeddingRequest<String> request) {
    ImmutableList<EmbedData<String>> embedData = request.getEmbedData();
    return Futures.submit(
        () -> {
          try {
            if (embedData.isEmpty()) {
              return ImmutableList.of();
            }
            Request httpRequest =
                createRequest(embedData.get(0).getData(), embedData.get(0).getTask());
            JSONObject response = post(httpRequest);
            JSONObject embedding = response.getJSONObject("embedding");
            JSONArray values = embedding.getJSONArray("values");
            ArrayList<Float> valuesList = new ArrayList<>();
            for (int j = 0; j < values.length(); j++) {
              valuesList.add(Float.valueOf((float) values.getDouble(j)));
            }
            return ImmutableList.copyOf(valuesList);
          } catch (JSONException | IOException e) {
            throw new VerifyException(e);
          }
        },
        workerExecutor);
  }

  @Override
  // Returns a list of embedding vectors. Sizes are adjustable (768 default).
  public ListenableFuture<ImmutableList<ImmutableList<Float>>> getBatchEmbeddings(
      EmbeddingRequest<String> request) {
    ImmutableList<EmbedData<String>> embedData = request.getEmbedData();
    return Futures.submit(
        () -> {
          try {
            if (embedData.isEmpty()) {
              return ImmutableList.of(ImmutableList.of());
            }
            List<String> texts = new ArrayList<>();
            for (EmbedData<String> embed : embedData) {
              texts.add(embed.getData());
            }
            List<EmbedData.TaskType> taskTypes = new ArrayList<>();
            for (EmbedData<String> embed : embedData) {
              taskTypes.add(embed.getTask());
            }
            Log.i(TAG, "Chunks: " + texts.size());
            Request httpRequest =
                createBatchRequest(ImmutableList.copyOf(texts), ImmutableList.copyOf(taskTypes));
            JSONObject response = post(httpRequest);
            JSONArray embeddings = response.getJSONArray("embeddings");
            ArrayList<ImmutableList<Float>> embeddingsList = new ArrayList<>();
            for (int i = 0; i < embeddings.length(); i++) {
              JSONObject embedding = embeddings.getJSONObject(i);
              JSONArray values = embedding.getJSONArray("values");
              ArrayList<Float> valuesList = new ArrayList<>();
              for (int j = 0; j < values.length(); j++) {
                valuesList.add(Float.valueOf((float) values.getDouble(j)));
              }
              embeddingsList.add(ImmutableList.copyOf(valuesList));
            }
            Log.i(TAG, "Embeddings: " + embeddingsList.size());
            return ImmutableList.copyOf(embeddingsList);
          } catch (JSONException | IOException e) {
            throw new VerifyException(e);
          }
        },
        workerExecutor);
  }

  private Request createRequest(String text, EmbedData.TaskType taskType) throws JSONException {
    HttpUrl url =
        Objects.requireNonNull(HttpUrl.parse(BASE_URL + model + EMBED_TEXT))
            .newBuilder()
            .addQueryParameter("key", apiKey)
            .build();
    final RequestBody body =
        RequestBody.create(
            createPayload(text, taskType).toString(),
            MediaType.parse("application/json; charset=utf-8"));
    return new Request.Builder()
        .url(url)
        .addHeader("Content-Type", "application/json")
        .post(body)
        .build();
  }

  private JSONObject createPayload(String text, EmbedData.TaskType taskType) throws JSONException {
    final JSONObject part = new JSONObject();
    part.put("text", text);
    final JSONArray partList = new JSONArray();
    partList.put(part);
    final JSONObject content = new JSONObject();
    content.put("parts", partList);
    final JSONObject payload = new JSONObject();
    payload.put("model", model);
    payload.put("content", content);
    payload.put("taskType", taskType.value());
    return payload;
  }

  private Request createBatchRequest(
      ImmutableList<String> texts, ImmutableList<EmbedData.TaskType> taskTypes)
      throws JSONException {
    final JSONArray requests = new JSONArray();
    verify(texts.size() == taskTypes.size());
    for (int i = 0; i < texts.size(); i++) {
      requests.put(createPayload(texts.get(i), taskTypes.get(i)));
    }
    final JSONObject requestData = new JSONObject();
    requestData.put("requests", requests);

    HttpUrl url =
        Objects.requireNonNull(HttpUrl.parse(BASE_URL + model + BATCH_EMBED_TEXT))
            .newBuilder()
            .addQueryParameter("key", apiKey)
            .build();
    final RequestBody body =
        RequestBody.create(
            requestData.toString(), MediaType.parse("application/json; charset=utf-8"));
    return new Request.Builder()
        .url(url)
        .addHeader("Content-Type", "application/json")
        .post(body)
        .build();
  }

  private JSONObject post(final Request request) throws IOException, JSONException {
    try (final Response response = httpClient.newCall(request).execute()) {
      final String responseBody = Objects.requireNonNull(response.body()).string();
      Log.i(TAG, "Response code: " + response.code());
      return new JSONObject(responseBody);
    }
  }
}
