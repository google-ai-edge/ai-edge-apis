# ODML On-device RAG SDK

The ODML on-device RAG SDK provides fundamental components for constructing a
RAG (Retrieval Augmented Generation) pipeline on device. The SDK's modular
architecture offers easy-to-use abstractions and a variety of concrete
implementations for its key building blocks. The SDK is currently available in
[Java](https://github.com/google-ai-edge/ai-edge-apis/tree/main/local_agents/rag/java/com/google/ai/edge/localagents/rag/).

## Key Modules

The SDK provides the following key modules and APIs for the RAG pipeline:

- `Language Models`: The LLM models with open-prompt API, either local
(on-device) or server-based. Its API is based on the `LanguageModel`
[Java API](https://github.com/google-ai-edge/ai-edge-apis/tree/main/local_agents/rag/java/com/google/ai/edge/localagents/rag/models/LanguageModel.java)
interface.
- `Text Embedding Models`: Convert structured/unstructured texts to embedding
vectors for semantic search. Its API is based on the `TextEmbeddingModel`
[Java API](https://github.com/google-ai-edge/ai-edge-apis/tree/main/local_agents/rag/java/com/google/ai/edge/localagents/rag/models/Embedder.java)
interface.
- `Vector Stores`: The vector store holds the embeddings and metadata derived
from data chunks. It can be queried to get similar chunks or exact matches. Its
API is based on the `VectorStore` [Java API](https://github.com/google-ai-edge/ai-edge-apis/tree/main/local_agents/rag/java/com/google/ai/edge/localagents/rag/memory/VectorStore.java)
interface.
- `Semantic Memory`: Serve as a semantic retriever for retrieving top k relevant
chunks given a query. Its API is based on the `SemanticMemory` [Java API](https://github.com/google-ai-edge/ai-edge-apis/tree/main/local_agents/rag/java/com/google/ai/edge/localagents/rag/memory/SemanticMemory.java)
interface.
- `Chunking`: Splits user data into smaller pieces to facilitate indexing.
- `Chains`: Combine several components mentioned a above or other chains in a
single pipeline. Orchestrate retrieval and querying of models. Its API is based
on the [Java API](https://github.com/google-ai-edge/ai-edge-apis/tree/main/local_agents/rag/java/com/google/ai/edge/localagents/rag/chains/Chain.java) interface. Here are some examples,
[RetrievalAndInferenceChain](https://github.com/google-ai-edge/ai-edge-apis/tree/main/local_agents/rag/java/com/google/ai/edge/localagents/rag/chains/RetrievalAndInferenceChain.java),
[RetrievalChain](https://github.com/google-ai-edge/ai-edge-apis/tree/main/local_agents/rag/java/com/google/ai/edge/localagents/rag/chains/RetrievalChain.java)

## Demos

Try our [sample app](https://github.com/google-ai-edge/ai-edge-apis/tree/main/examples/local_agents/rag)
for a quick demo.

## Guide

See our [public documentation](https://ai.google.dev/edge/mediapipe/solutions/genai/rag/android)
for more details on the SDK's usage.
