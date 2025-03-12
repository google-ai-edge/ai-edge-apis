# Google AI Edge RAG Sample Application

This directory contains a small sample application to showcase our RAG SDK. Both the sample app and
the SDK itself are under active development.

The SDK provides a RAG pipeline that focuses on text-to-text tasks. It handles embedding extraction,
storage and inference, with the possiblity to configure the backends for each of these tasks.

As we are still in active development, the current backends are limited to:

- `com.google.aiedge.rag.models.GeckoEmbeddingModel` for on-device text embedding extraction via the
  Gecko model
- `com.google.aiedge.rag.models.GeminiEmbedder` for on-device text embedding extraction via the
  Generative Language Cloud API
- `com.google.aiedge.rag.memory.SqliteVectorStore` for persistent vector storage via SQLite
- `com.google.aiedge.rag.memory.DefaultVectorStore` for non-persistent vector storage
- `com.google.aiedge.rag.models.MediaPipeLanguageModel` for LLM Inference via MediaPipe

The sample app is configured to use the `GeminiEmbedder` combined with the `SqliteVectorStore` and
the `MediaPipeLanguageModel` (see `com.google.aiedge.samples.rag.RagPipeline`) by default. If you
would like to use the Gecko model for on-device embedding extraction, you can remove
the `GeminiEmbedder` from the pipeline configuration and replace it with the provided instance of
the `GeckoEmbeddingMode`.

Steps to run the sample app:

1) Connect an Android phone to your workstation. We currently target higher end devices such as
   Pixel 8, Pixel 9, S23 and S24.

2) Download [Gemma3]https://huggingface.co/litert-community/Gemma3-1B-IT/resolve/main/gemma3-1b-it-int4.task?download=true) to your workstation and push to device:

```
adb push /tmp/gemma3-1b-it-int4.task /data/local/tmp/gemma3-1b-it-int4.task
```

3) If you want to use the `GeckoEmbeddingModel`, you need to push the tokenizer
   model (`sentencepiece.model`) and a Gecko embedding model to your device. We offer two different
   model versions that are optimized for either CPU or GPU execution. The sample app is currently
   configured to extraction embeddings via GPU (see `USE_GPU_FOR_EMBEDDINGS` in `RagPipeline.kt`).

   You can downlaod the Gecko model and the tokenizer from our [HuggingFace community](https://huggingface.co/litert-community/Gecko-110m-en)

   To push the tokenizer model and the `Gecko_256_quant.tflite` embedding model to your device, you
   can for example run:

```
adb push sentencepiece.model /data/local/tmp/sentencepiece.model
adb push Gecko_256_quant.tflite /data/local/tmp/gecko.tflite
```

6) If you want to use `GeminiEmbedder` and compute embeddings via the Gemini Cloud API, you need to
   generate an API key at https://aistudio.google.com/app/apikey and replace the `API_KEY` value in
   `RagPipeline.kt`. You also need to set `COMPUTE_EMBEDDINGS_LOCALLY` to `false`.

7) Clone https://github.com/google-ai-edge/ai-edge-apis and
   open https://github.com/google-ai-edge/ai-edge-apis//tree/main/examples/rag/android in Android
   Studio.

8) Run the sample app on the connected device.
