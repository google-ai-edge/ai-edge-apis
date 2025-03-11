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
import static com.google.common.collect.ImmutableMap.toImmutableMap;

import com.google.ai.edge.localagents.rag.memory.proto.KeyValuePair;
import com.google.ai.edge.localagents.rag.memory.proto.MemoryRecord;
import com.google.ai.edge.localagents.rag.memory.proto.Metadata;
import com.google.ai.edge.localagents.rag.memory.proto.TableConfig.ColumnConfig.KeyType;
import com.google.common.collect.ImmutableList;
import com.google.common.collect.ImmutableMap;
import com.google.common.primitives.Floats;
import com.google.protobuf.ExtensionRegistryLite;
import com.google.protobuf.InvalidProtocolBufferException;
import java.util.List;
import java.util.Map;

/** A vector store implementation wrapping the SQLite JNI with vector extension. */
public final class SqliteVectorStore implements VectorStore<String> {
  public static final String DEFAULT_DATABASE_PATH = ""; // Default is ephemeral.
  public static final String DEFAULT_TABLE_NAME = "rag_vector_store";
  public static final String DEFAULT_TEXT_COLUMN_NAME = "text";
  public static final String DEFAULT_EMBEDDINGS_COLUMN_NAME = "embeddings";
  public static final com.google.ai.edge.localagents.rag.memory.TableConfig DEFAULT_TABLE_CONFIG =
      TableConfig.create(
          DEFAULT_TABLE_NAME,
          ImmutableList.of(
              ColumnConfig.create(
                  "ROWID", "INTEGER", ColumnConfig.KeyType.PRIMARY_KEY, true, false),
              ColumnConfig.create(DEFAULT_TEXT_COLUMN_NAME, "TEXT"),
              ColumnConfig.create(DEFAULT_EMBEDDINGS_COLUMN_NAME, "REAL")));

  private final long jniHandle;

  static {
    System.loadLibrary("sqlite_vector_store_jni");
  }

  /**
   * Creates a new ephemeral vector store with a default table format.
   *
   * @param numEmbeddingDimensions The number of embedding dimensions.
   */
  public SqliteVectorStore(int numEmbeddingDimensions) {
    this(numEmbeddingDimensions, DEFAULT_DATABASE_PATH);
  }

  /**
   * Creates a new persisted vector store with a default table format.
   *
   * @param numEmbeddingDimensions The number of embedding dimensions.
   * @param databasePath The path to the persisted database file.
   */
  public SqliteVectorStore(int numEmbeddingDimensions, String databasePath) {
    this(
        numEmbeddingDimensions,
        databasePath,
        DEFAULT_TEXT_COLUMN_NAME,
        DEFAULT_EMBEDDINGS_COLUMN_NAME,
        DEFAULT_TABLE_CONFIG);
  }

  /**
   * Creates a new persisted vector store with a bespoke table format.
   *
   * @param numEmbeddingDimensions The number of embedding dimensions.
   * @param databasePath The path to the persisted database file.
   * @param textColumnName The name of the text column.
   * @param embeddingColumnName The name of the embedding column.
   * @param tableConfig The table configuration.
   */
  public SqliteVectorStore(
      int numEmbeddingDimensions,
      String databasePath,
      String textColumnName,
      String embeddingColumnName,
      com.google.ai.edge.localagents.rag.memory.TableConfig tableConfig) {
    jniHandle =
        nativeCreateSqliteVectorStore(
            numEmbeddingDimensions,
            databasePath,
            textColumnName,
            embeddingColumnName,
            toTableConfigProtoBytes(tableConfig));
  }

  /**
   * Inserts a record into the vector store.
   *
   * @param record The record to insert.
   */
  @Override
  public void insert(VectorStoreRecord<String> record) {
    nativeInsert(jniHandle, toMemoryRecordProtoBytes(record));
  }

  /**
   * Returns the nearest records to the given query embedding.
   *
   * @param queryEmbeddings The query embeddings.
   * @param topK The maximum number of records to return.
   * @param minSimilarityScore The minimum similarity score to return.
   * @return The nearest records to the query embeddings.
   */
  @Override
  public ImmutableList<VectorStoreRecord<String>> getNearestRecords(
      List<Float> queryEmbeddings, int topK, float minSimilarityScore) {
    return toVectorStoreRecordList(
        nativeGetNearestRecords(
            jniHandle, Floats.toArray(queryEmbeddings), topK, minSimilarityScore));
  }

  /**
   * Executes a SQL query on the vector store.
   *
   * @param query The SQL query to execute.
   */
  public void sqlQuery(String query) {
    nativeSqlQuery(jniHandle, query);
  }

  private static byte[] toTableConfigProtoBytes(
      com.google.ai.edge.localagents.rag.memory.TableConfig tableConfig) {
    var builder =
        com.google.ai.edge.localagents.rag.memory.proto.TableConfig.newBuilder()
            .setName(tableConfig.getName());
    for (var columnConfig : tableConfig.getColumns()) {
      var column =
          com.google.ai.edge.localagents.rag.memory.proto.TableConfig.ColumnConfig.newBuilder()
              .setName(columnConfig.getName())
              .setSqlType(columnConfig.getSqlType())
              .setKeyType(toKeyTypeEnum(columnConfig.getKeyType()))
              .setAutoIncrement(columnConfig.getAutoIncrement())
              .setIsNullable(columnConfig.getIsNullable())
              .build();
      builder.addColumns(column);
    }
    return builder.build().toByteArray();
  }

  private static byte[] toMemoryRecordProtoBytes(VectorStoreRecord<String> record) {
    return MemoryRecord.newBuilder()
        .setText(record.getData())
        .addAllEmbeddings(record.getEmbeddings())
        .setMetadata(toMetadataProto(record.getMetadata()))
        .build()
        .toByteArray();
  }

  private static Metadata toMetadataProto(Map<String, Object> metadata) {
    var builder = Metadata.newBuilder();
    for (var keyValuePair : metadata.entrySet()) {
      builder.addKeyValuePairs(
          KeyValuePair.newBuilder()
              .setKey(keyValuePair.getKey())
              .setValue(keyValuePair.getValue().toString())
              .build());
    }
    return builder.build();
  }

  private static KeyType toKeyTypeEnum(ColumnConfig.KeyType keyType) {
    switch (keyType) {
      case PRIMARY_KEY:
        return KeyType.PRIMARY_KEY;
      case DEFAULT_NOT_KEY:
        return KeyType.DEFAULT_NOT_KEY;
    }
    throw new IllegalArgumentException("Unknown key type: " + keyType);
  }

  private static ImmutableList<VectorStoreRecord<String>> toVectorStoreRecordList(
      List<byte[]> memoryRecords) {
    return memoryRecords.stream()
        .map(SqliteVectorStore::toVectorStoreRecord)
        .collect(toImmutableList());
  }

  private static VectorStoreRecord<String> toVectorStoreRecord(byte[] memoryRecordBytes) {
    try {
      // TODO(mrschmidt): We should add ExtensionRegistryLite.getGeneratedRegistry() for the 1P
      // ExtensionRegistryLite.getEmptyRegistry() for the 3P build, but we currently use the
      // same build target for both 1P and 3P.
      var memoryRecord =
          MemoryRecord.parseFrom(memoryRecordBytes, ExtensionRegistryLite.getEmptyRegistry());
      var metadata = toMetadataMap(memoryRecord.getMetadata());
      return VectorStoreRecord.create(
          memoryRecord.getText(), ImmutableList.copyOf(memoryRecord.getEmbeddingsList()), metadata);
    } catch (InvalidProtocolBufferException e) {
      throw new IllegalArgumentException("Failed to parse memory record", e);
    }
  }

  private static ImmutableMap<String, Object> toMetadataMap(Metadata metadata) {
    return metadata.getKeyValuePairsList().stream()
        .collect(toImmutableMap(KeyValuePair::getKey, KeyValuePair::getValue));
  }

  private static native long nativeCreateSqliteVectorStore(
      int numEmbeddingDimensions,
      String databasePath,
      String textColumnName,
      String embeddingColumnName,
      byte[] tableConfigBytes);

  private static native void nativeInsert(long jniHandle, byte[] memoryRecordBytes);

  private static native List<byte[]> nativeGetNearestRecords(
      long jniHandle, float[] queryEmbeddings, int topK, float minSimilarityScore);

  private static native void nativeSqlQuery(long jniHandle, String query);
}
