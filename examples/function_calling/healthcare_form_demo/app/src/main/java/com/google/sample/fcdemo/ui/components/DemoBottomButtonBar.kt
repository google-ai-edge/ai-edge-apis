@file:OptIn(ExperimentalMaterial3Api::class)

package com.google.sample.fcdemo.ui.components

import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.width
import androidx.compose.material3.Button
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.google.sample.fcdemo.utilities.SpeechRecognitionLauncher
import com.google.sample.fcdemo.utilities.SpeechRecognitionResult

@Composable
fun DemoBottomButtonBar(
    fieldsetIsCompleteAndValid: Boolean,
    listeningState: Boolean,
    isProcessing: Boolean,
    onlListeningStateChanged: (Boolean) -> Unit,
    onRecognizedSpeechChanged: (String) -> Unit,
    onVoiceRecognitionSuccess: (SpeechRecognitionResult.Success) -> Unit,
    onVoiceRecognitionError: (SpeechRecognitionResult.Error) -> Unit,
    onContinuePressed: () -> Unit,
) {
    Row {
        val recognizerWeight = when {
            isProcessing -> 1f
            fieldsetIsCompleteAndValid -> .3f
            else -> 1f
        }
        SpeechRecognitionLauncher(
            onResult = { result ->
                when (result) {
                    is SpeechRecognitionResult.Success -> {
                        onVoiceRecognitionSuccess(result)
                    }

                    is SpeechRecognitionResult.Error -> {
                        onVoiceRecognitionError(result)
                    }
                }
            },
            modifier = Modifier
                .weight(recognizerWeight)
                .height(52.dp),
            fieldsetIsCompleteAndValid = fieldsetIsCompleteAndValid,
            listeningState = listeningState,
            isProcessing = isProcessing,
            onlListeningStateChanged = onlListeningStateChanged,
            onRecognizedSpeechChanged = onRecognizedSpeechChanged,
        )
        if (!listeningState && !isProcessing && fieldsetIsCompleteAndValid) {
            Spacer(modifier = Modifier.width(8.dp))

            Button(
                onClick = { onContinuePressed() },
                modifier = Modifier
                    .weight(0.5f)
                    .height(52.dp)
            ) {
                Text("Continue", fontSize = 16.sp)
            }
        }
    }
}