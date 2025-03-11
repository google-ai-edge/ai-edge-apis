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
package com.google.ai.edge.localagents.rag.shared;

import java.util.List;

/** Utility class for vector operations. */
public final class VectorOperations {

  public static float cosineSimilarity(List<Float> x, List<Float> y) {
    if (x.size() != y.size()) {
      throw new IllegalArgumentException("Vectors lengths must be equal");
    }

    float dotProduct = dot(x, y);
    float normX = dot(x, x);
    float normY = dot(y, y);

    if (normX == 0 || normY == 0) {
      throw new IllegalArgumentException("Vectors cannot have zero norm");
    }

    return dotProduct / (float) (Math.sqrt(normX) * Math.sqrt(normY));
  }

  public static float dot(List<Float> x, List<Float> y) {
    if (x.size() != y.size()) {
      throw new IllegalArgumentException("Vectors lengths must be equal");
    }

    float result = 0;
    for (int i = 0; i < x.size(); ++i) {
      result += x.get(i) * y.get(i);
    }

    return result;
  }

  private VectorOperations() {}
}
