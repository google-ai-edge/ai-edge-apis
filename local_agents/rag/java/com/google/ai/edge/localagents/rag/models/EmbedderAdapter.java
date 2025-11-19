package com.google.ai.edge.localagents.rag.models;

import static com.google.common.collect.ImmutableList.toImmutableList;

import com.google.common.collect.ImmutableList;
import com.google.common.util.concurrent.ListenableFuture;

/** An adapter for using {@code Embedder<String>} as {@code Embedder<Part>}. */
public class EmbedderAdapter implements Embedder<Part> {
  public final Embedder<String> delegate;

  public EmbedderAdapter(Embedder<String> delegate) {
    this.delegate = delegate;
  }

  @Override
  public ListenableFuture<ImmutableList<Float>> getEmbeddings(EmbeddingRequest<Part> request) {

    return delegate.getEmbeddings(
        EmbeddingRequest.create(
            request.getEmbedData().stream()
                .map(
                    it -> {
                      if (it.getData().getKind() == Part.Kind.TEXT) {
                        return EmbedData.create(it.getData().text(), it.getTask());
                      } else {
                        throw new IllegalArgumentException(
                            "Unsupported request data type for text only embedding model");
                      }
                    })
                .collect(toImmutableList())));
  }

  @Override
  public ListenableFuture<ImmutableList<ImmutableList<Float>>> getBatchEmbeddings(
      EmbeddingRequest<Part> request) {
    return delegate.getBatchEmbeddings(
        EmbeddingRequest.create(
            request.getEmbedData().stream()
                .map(
                    it -> {
                      if (it.getData().getKind() == Part.Kind.TEXT) {
                        return EmbedData.create(it.getData().text(), it.getTask());
                      } else {
                        throw new IllegalArgumentException(
                            "Unsupported request data type for text only embedding model");
                      }
                    })
                .collect(toImmutableList())));
  }
}
