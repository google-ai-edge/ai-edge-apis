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
package com.google.ai.edge.localagents.fc.toolretrieval;

import com.google.common.collect.ImmutableMap;

import java.util.HashMap;
import java.util.Map;
import java.util.Optional;

/** Metadata class for a tool, containing metadata for its functions. */
public final class ToolMetadata {
  private final Map<String, FunctionMetadata> functionNameToMetadata;

  public ToolMetadata() {
    this.functionNameToMetadata = new HashMap<>();
  }

  /**
   * Adds metadata for a function.
   *
   * @param functionName The name of the function.
   * @param metadata The metadata for the function.
   * @return This ToolMetadata instance for method chaining.
   */
  public ToolMetadata addFunctionMetadata(String functionName, FunctionMetadata metadata) {
    if (functionName == null || metadata == null) {
      throw new IllegalArgumentException("Function name and metadata cannot be null.");
    }
    this.functionNameToMetadata.put(functionName, metadata);
    return this;
  }

  /**
   * Returns an immutable view of the function metadata map.
   *
   * @return An immutable map of function names to their metadata.
   */
  public ImmutableMap<String, FunctionMetadata> getFunctions() {
    return ImmutableMap.copyOf(functionNameToMetadata);
  }

  /**
   * Retrieves the metadata for a specific function.
   *
   * @param functionName The name of the function.
   * @return An Optional containing the FunctionMetadata if found, or an empty Optional otherwise.
   */
  public Optional<FunctionMetadata> getFunctionMetadata(String functionName) {
    return Optional.ofNullable(functionNameToMetadata.get(functionName));
  }

  /**
   * Removes the metadata for a specific function.
   *
   * @param functionName The name of the function.
   * @return An Optional containing the removed FunctionMetadata, or empty if the function was not
   *     found.
   */
  public Optional<FunctionMetadata> removeFunctionMetadata(String functionName) {
    return Optional.ofNullable(functionNameToMetadata.remove(functionName));
  }

  /** Metadata for a specific function within a tool. */
  public static class FunctionMetadata {
    private final Map<String, String> attributes;

    public FunctionMetadata() {
      this.attributes = new HashMap<>();
    }

    /**
     * Adds an attribute to the function metadata.
     *
     * @param key The attribute key.
     * @param value The attribute value.
     * @return This FunctionMetadata instance for method chaining.
     */
    public FunctionMetadata addAttribute(String key, String value) {
      if (key == null || value == null) {
        throw new IllegalArgumentException("Attribute key and value cannot be null.");
      }
      this.attributes.put(key, value);
      return this;
    }

    /**
     * Returns an immutable view of the attributes.
     *
     * @return An immutable map of attribute keys to values.
     */
    public ImmutableMap<String, String> getAttributes() {
      return ImmutableMap.copyOf(attributes);
    }

    /**
     * Retrieves the value of a specific attribute.
     *
     * @param key The attribute key.
     * @return An Optional containing the attribute value if found, or an empty Optional otherwise.
     */
    public Optional<String> getAttribute(String key) {
      return Optional.ofNullable(attributes.get(key));
    }

    /**
     * Removes an attribute from the metadata.
     *
     * @param key The key of the attribute to remove.
     * @return An Optional containing the removed attribute value, or empty if the key was not
     *     found.
     */
    public Optional<String> removeAttribute(String key) {
      return Optional.ofNullable(attributes.remove(key));
    }
  }
}
