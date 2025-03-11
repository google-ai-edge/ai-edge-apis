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

import com.google.auto.value.AutoValue;

/** SQLite table column configuration. */
@AutoValue
public abstract class ColumnConfig {
  /** The type of key this column is. */
  public enum KeyType {
    DEFAULT_NOT_KEY,
    PRIMARY_KEY,
  }

  /** Returns the name of the column. */
  public abstract String getName();

  /**
   * Returns the type of this column (should be a type supported by SQLite or the available
   * extensions).
   */
  public abstract String getSqlType();

  /** Returns whether this column is a key for this table. */
  public abstract KeyType getKeyType();

  /** If true, this value should be auto-incremented. Only applicable to corresponding types. */
  public abstract boolean getAutoIncrement();

  /** If true, this value may be null. */
  public abstract boolean getIsNullable();

  public static Builder builder() {
    return new AutoValue_ColumnConfig.Builder();
  }

  public static ColumnConfig create(String name, String sqlType) {
    return ColumnConfig.create(
        name,
        sqlType,
        KeyType.DEFAULT_NOT_KEY,
        /* autoIncrement= */ false,
        /* isNullable= */ false);
  }

  public static ColumnConfig create(
      String name, String sqlType, KeyType keyType, boolean autoIncrement, boolean isNullable) {
    return builder()
        .setName(name)
        .setSqlType(sqlType)
        .setKeyType(keyType)
        .setAutoIncrement(autoIncrement)
        .setIsNullable(isNullable)
        .build();
  }

  /** Auto Builder. */
  @AutoValue.Builder
  public abstract static class Builder {
    public abstract Builder setName(String name);

    public abstract Builder setSqlType(String sqlType);

    public abstract Builder setKeyType(KeyType keyType);

    public abstract Builder setAutoIncrement(boolean autoIncrement);

    public abstract Builder setIsNullable(boolean isNullable);

    public abstract ColumnConfig build();
  }
}
