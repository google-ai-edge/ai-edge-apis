# AI Edge On-Device APIs and SDKs

The AI Edge On-Device APIs and SDKs repository provide a set of libraries that
allow you to easily build end-to-end applications with Google AI Edge's GenAI
pipelines.

## Key Features

### On-Device RAG SDK

The AI Edge On-Device RAG SDK provides fundamental components for constructing a
RAG (Retrieval Augmented Generation) pipeline on device. The SDK's modular
architecture offers easy-to-use abstractions and a variety of concrete
implementations for its key building blocks. The SDK is currently available in
Java.

You can find the SDK on [GitHub](https://github.com/google-ai-edge/ai-edge-apis/tree/main/local_agents/rag)
or follow our [public documentation](https://ai.google.dev/edge/mediapipe/solutions/genai/rag/android)
to install directly from Maven. We have also published a
[sample app](https://github.com/google-ai-edge/ai-edge-apis/tree/main/examples/rag)
in this repository.

### On-Device Function Calling SDK

The AI Edge Function Calling SDK (FC SDK) enables developers to use function
calling with on-device LLMs. Function calling lets you connect models to
external tools and APIs, enabling models to call specific functions with the
necessary parameters to execute real-world actions.

Rather than just generating text, an LLM using the FC SDK can generate a
structured call to a function that executes an action, such as searching for
up-to-date information, setting alarms, or making reservations.

The AI Edge FC SDK is available for Android and can be run completely on-device
with the LLM Inference API. Start using the SDK by following the [Android guide](https://ai.google.dev/edge/mediapipe/solutions/genai/fc/android),
which walks you through a basic implementation of a sample application using
function calling.

You can find the SDK on [GitHub](https://github.com/google-ai-edge/ai-edge-apis/tree/main/local_agents/function_calling), along with a [sample app](https://github.com/google-ai-edge/ai-edge-apis/tree/main/examples/function_calling/healthcare_form_demo).
