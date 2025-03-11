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
package com.google.ai.edge.localagents.rag.memory;

import static com.google.common.collect.ImmutableList.toImmutableList;

import com.google.ai.edge.localagents.rag.shared.VectorOperations;
import com.google.common.collect.ImmutableList;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.atomic.AtomicInteger;
import org.jspecify.annotations.Nullable;

/** A simple non-persistent memory store using a hash map. */
public final class DefaultVectorStore<T> implements VectorStore<T> {
  private final Map<Integer, VectorStoreRecord<T>> store = new HashMap<>();

  private AtomicInteger nextId = new AtomicInteger(0);

  public DefaultVectorStore() {}

  @Override
  public void insert(VectorStoreRecord<T> record) {
    Integer id = nextId.getAndIncrement();
    store.put(id, record);
  }

  @Override
  public ImmutableList<VectorStoreRecord<T>> getNearestRecords(
      List<Float> queryEmbeddings, int topK, float minSimilarityScore) {
    List<Tuple<VectorStoreRecord<T>, Float>> nearestRecords = new ArrayList<>();
    store
        .values()
        .forEach(
            recored -> {
              float similarityScore =
                  VectorOperations.cosineSimilarity(queryEmbeddings, recored.getEmbeddings());
              if (similarityScore >= minSimilarityScore) {
                nearestRecords.add(
                    new Tuple<VectorStoreRecord<T>, Float>(recored, similarityScore));
              }
            });
    // descending order
    return nearestRecords.stream()
        .sorted(
            Comparator.comparing(
                Tuple::getSecond, (score1, score2) -> Float.compare(score2, score1)))
        .limit(topK)
        .map(Tuple::getFirst)
        .collect(toImmutableList());
  }

  /**
   * Just a function to get the records for testing.
   *
   * <p>TODO(b/373396829): Add VisibleForTesting annotation that is compatible with the 3P build.
   */
  @Nullable
  public VectorStoreRecord<T> get(Integer id) {
    return store.get(id);
  }

  static class Tuple<T1, T2> {
    final T1 first;
    final T2 second;

    Tuple(T1 first, T2 second) {
      this.first = first;
      this.second = second;
    }

    T1 getFirst() {
      return first;
    }

    T2 getSecond() {
      return second;
    }
  }
}
