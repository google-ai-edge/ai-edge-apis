# AI Edge On-device RAG SDK

The AI Edge on-device RAG SDK provides fundamental components for constructing a
RAG (Retrieval Augmented Generation) pipeline on device. The SDK's modular
architecture offers easy-to-use abstractions and a variety of concrete
implementations for its key building blocks. The SDK is currently available in
Java.

## Key Modules

The SDK provides the following key modules and APIs for the RAG pipeline:

- `Language Models`: The LLM models with open-prompt API, either local (on-device) or server-based. Its API is based on the [LanguageModel](https://github.com/google-ai-edge/ai-edge-apis/tree/main/local_agents/rag/java/com/google/ai/edge/localagents/rag/models/LanguageModel.java) interface.
- `Text Embedding Models`: Convert structured/unstructured texts to embedding vectors for semantic search. Its API is based on the [Embedder](https://github.com/google-ai-edge/ai-edge-apis/tree/main/local_agents/rag/java/com/google/ai/edge/localagents/rag/models/Embedder.java) interface.
- `Vector Stores`: The vector store holds the embeddings and metadata derived from data chunks. It can be queried to get similar chunks or exact matches. Its API is based on the [VectorStore](https://github.com/google-ai-edge/ai-edge-apis/tree/main/local_agents/rag/java/com/google/ai/edge/localagents/rag/memory/VectorStore.java) interface.
- `Semantic Memory`: Serve as a semantic retriever for retrieving top k relevant chunks given a query. Its API is based on the [SemanticMemory](https://github.com/google-ai-edge/ai-edge-apis/tree/main/local_agents/rag/java/com/google/ai/edge/localagents/rag/memory/SemanticMemory.java) interface.
- `Chunking`: Splits user data into smaller pieces to facilitate indexing.
- `Chains`: Combine several components mentioned a above or other chains in a single pipeline. Orchestrate retrieval and querying of models. Its API is based on the [Chain](https://github.com/google-ai-edge/ai-edge-apis/tree/main/local_agents/rag/java/com/google/ai/edge/localagents/rag/chains/Chain.java) interface. Here are some examples, [RetrievalAndInferenceChain](https://github.com/google-ai-edge/ai-edge-apis/tree/main/local_agents/rag/java/com/google/ai/edge/localagents/rag/chains/RetrievalAndInferenceChain.java), [RetrievalChain](https://github.com/google-ai-edge/ai-edge-apis/tree/main/local_agents/rag/java/com/google/ai/edge/localagents/rag/chains/RetrievalChain.java).

## Demos

TODO(ypang): add sample app link.

Try our sample android app for a quick demo.

## How to set up an on-device RAG Pipeline

We'll now demonstrate a naive RAG pipeline implementation using our SDK.

### Java/Kotlin

The pipeline is configured using [`ChainConfig`](https://github.com/google-ai-edge/ai-edge-apis/tree/main/local_agents/rag/java/com/google/ai/edge/localagents/rag/chains/ChainConfig.java). One can configure the pipeline with the following instructions:

1.  Choose the chain you want to use. We'll use [`RetrievalAndInferenceChain`](https://github.com/google-ai-edge/ai-edge-apis/tree/main/local_agents/rag/java/com/google/ai/edge/localagents/rag/chains/RetrievalAndInferenceChain.java) in this example. This chain firstly retrieves the top k most relevant text chunks (if any) and addes them to the prompt. The augmented prompt is then used to generate a response from the LLM. You can also build your custom chain with the modules in [`ChainConfig`](https://github.com/google-ai-edge/ai-edge-apis/tree/main/local_agents/rag/java/com/google/ai/edge/localagents/rag/chains/ChainConfig.java).

2.  Instantiate the necessary pipeline modules:

```
// Configure LLM. Here we're running models on-device via the MediaPipe LLM Inference API.
val modelPath = "your_model_path"
val val mediapipe = MediaPipeLlmBackend(
                      application.applicationContext,
                      LlmInferenceOptions.builder()
                        .setModelPath(modelPath)
                        .setMaxTokens(1024)
                        .setMaxTopK(40)
                        .build(),
                    )

// Configure embedding model. Here we use the on-device Gecko embedding model.
val embeddingModelPath = "your_model_path"
val sentencepieceModelPath = "your_sentence_piece_model_path"
val gecko = GeckoEmbeddingModel(embeddingModelPath, Optional.of(sentencepieceModelPath), true)

// Configure the memory store.
val databasePath = "your_database_path"
val sqliteVectorStore = SqliteVectorStore(GECKO_DIMENSIONS, databasePath)

// Configure semantic text memory.
val semanticTextMemory = DefaultSemanticTextMemory(sqliteVectorStore, gecko)

// Create your prompt builder.
val promptTemplate = "your_prompt_template"
val promptBuilder = PromptBuilder(promptTemplate)
```

3.  Add the modules to the `ChainConfig`. Instantiate a Chain (e.g. `RetrievalAndReferenceChain`) and initialize it with the configured `ChainConfig`. {value=3}

```
val config = ChainConfig.create(mediapipe, promptBuilder, semanticTextMemory, gecko)
val retrievalAndInferenceChain = RetrievalAndInferenceChain(config)
```

4.  Store text memories and invoke the chain with user query. For example, the following code snippet shows how to invoke a `RetrievalAndReferenceChain`. {value=4}

```
// Record memory.
val unused =
      config.semanticMemory.getOrNull()?.recordBatchedMemoryItems(memoryChunks.toImmutableList())

// Invoke the chain
val retrievalRequest =
      RetrievalRequest.create(prompt, RetrievalConfig.create(10, 0.0f, TaskType.QUESTION_ANSWERING))
val response = retrievalAndInferenceChain.invoke(retrievalRequest, callback).await().text
```
