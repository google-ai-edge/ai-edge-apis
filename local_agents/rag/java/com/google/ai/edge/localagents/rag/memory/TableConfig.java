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
import com.google.common.collect.ImmutableList;

/** SQLite table configuration. */
@AutoValue
public abstract class TableConfig {
  /** The name of the table. */
  public abstract String getName();

  /** The column configs of the table. */
  public abstract ImmutableList<ColumnConfig> getColumns();

  public abstract Builder toBuilder();

  public static Builder builder() {
    return new AutoValue_TableConfig.Builder();
  }

  public static TableConfig create(String name, ImmutableList<ColumnConfig> columns) {
    return builder().setName(name).setColumns(columns).build();
  }

  /** Auto Builder. */
  @AutoValue.Builder
  public abstract static class Builder {
    protected abstract ImmutableList.Builder<ColumnConfig> columnsBuilder();

    public abstract Builder setName(String name);

    public abstract Builder setColumns(ImmutableList<ColumnConfig> columns);

    public Builder addColumn(ColumnConfig column) {
      columnsBuilder().add(column);
      return this;
    }

    public abstract TableConfig build();
  }
}
