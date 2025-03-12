package com.google.ai.edge.samples.rag

import android.app.Application
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.toMutableStateList
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.google.ai.edge.localagents.rag.models.LanguageModelResponse
import com.google.ai.edge.localagents.rag.models.AsyncProgressListener
import java.util.concurrent.Executor
import java.util.concurrent.Executors
import kotlinx.coroutines.asCoroutineDispatcher
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

/** Instantiates the View Model for the chat view. */
class ChatViewModel constructor(private val application: Application) :
    AndroidViewModel(application) {
    private val ragPipeline = RagPipeline(application)
    internal val messages = emptyList<MessageData>().toMutableStateList()
    internal val statistics = mutableStateOf("")
    private val executorService = Executors.newSingleThreadExecutor()
    private val backgroundExecutor: Executor = Executors.newSingleThreadExecutor()

    fun memorizeChunks(filename: String) {
        ragPipeline.memorizeChunks(application.getApplicationContext(), filename)
    }

    @SuppressWarnings("FutureReturnValueIgnored")
    fun requestResponse(prompt: String) {
        appendMessage(MessageOwner.User, prompt)
        executorService.submit { viewModelScope.launch { requestResponseFromModel(prompt) } }
    }

    suspend fun requestResponseFromModel(prompt: String) =
        withContext(backgroundExecutor.asCoroutineDispatcher()) {
            ragPipeline.generateResponse(
                prompt,
                object : AsyncProgressListener<LanguageModelResponse> {
                    override fun run(response: LanguageModelResponse, done: Boolean) {
                        updateLastMessage(MessageOwner.Model, response.text)
                    }
                },
            )

        }

    private fun appendMessage(role: MessageOwner, message: String) {
        messages.add(MessageData(role, message))
    }

    private fun updateLastMessage(role: MessageOwner, message: String) {
        if (messages.isNotEmpty() && messages[messages.lastIndex].owner == role) {
            messages[messages.lastIndex] = MessageData(role, message)
        } else {
            appendMessage(role, message)
        }
    }

}

enum class MessageOwner {
    User,
    Model,
}

data class MessageData(val owner: MessageOwner, val message: String)