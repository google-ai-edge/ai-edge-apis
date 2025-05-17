package com.google.sample.fcdemo.utilities

import android.content.Intent
import android.os.Bundle
import android.speech.RecognitionListener
import android.speech.RecognizerIntent
import android.speech.SpeechRecognizer
import android.util.Log
import androidx.compose.animation.animateColorAsState
import androidx.compose.animation.core.FastOutSlowInEasing
import androidx.compose.animation.core.animateDpAsState
import androidx.compose.animation.core.tween
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Star
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableFloatStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberUpdatedState
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Alignment.Companion.CenterVertically
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalInspectionMode
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.LifecycleEventObserver
import androidx.lifecycle.compose.LocalLifecycleOwner
import com.airbnb.lottie.compose.LottieAnimation
import com.airbnb.lottie.compose.LottieCompositionSpec
import com.airbnb.lottie.compose.LottieConstants
import com.airbnb.lottie.compose.animateLottieCompositionAsState
import com.airbnb.lottie.compose.rememberLottieComposition
import com.google.sample.fcdemo.R
import com.google.sample.fcdemo.utilities.CurrentlyProcessing
import kotlinx.coroutines.delay

const val TAG = "SpeechRecognition"

// Define data classes for results and errors
sealed class SpeechRecognitionResult {
    data class Success(val text: String) : SpeechRecognitionResult()
    data class Error(val message: String) : SpeechRecognitionResult()
}

@Composable
fun SpeechRecognitionLauncher(
    onResult: (SpeechRecognitionResult) -> Unit,
    modifier: Modifier = Modifier,
    fieldsetIsCompleteAndValid: Boolean,
    listeningState: Boolean,
    onlListeningStateChanged: (Boolean) -> Unit,
    onRecognizedSpeechChanged: (String) -> Unit,
    isProcessing: Boolean,
) {
    if (LocalInspectionMode.current) {
        // We are in screen preview mode, compose a dummy button for preview and exit
        SpeechListenerButton(
            modifier = modifier,
            listeningState = listeningState,
            onlListeningStateChanged = { },
            fieldsetIsCompleteAndValid = false,
            currentRms = 0f,
            isProcessing = false,
        )
        return
    }
    val context = LocalContext.current
    val currentOnResult by rememberUpdatedState(onResult)
    // current detected volume level: OK to keep local as this is a completely transient state
    var currentRms by remember { mutableFloatStateOf(0f) }

    var speechRecognizer: SpeechRecognizer? by remember { mutableStateOf(null) }
    val speechRecognizerIntent = remember {
        Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
            putExtra(
                RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM
            )
            putExtra(RecognizerIntent.EXTRA_PREFER_OFFLINE, true)
            putExtra(RecognizerIntent.EXTRA_PARTIAL_RESULTS, true)
            // Optionally specify locale default language: putExtra(RecognizerIntent.EXTRA_LANGUAGE, Locale.getDefault())
        }
    }

    LaunchedEffect(listeningState) {
        if (listeningState) {
            Log.d(TAG, "START LISTENING")
            speechRecognizer?.startListening(speechRecognizerIntent)
        } else {
            Log.d(TAG, "STOP LISTENING")
            currentRms = 0f // Reset RMS when not listening
            speechRecognizer?.stopListening()
        }
    }

    LaunchedEffect(isProcessing) {
        if (!isProcessing) {
            Log.d(TAG, "STOP PROCESSING")
            onRecognizedSpeechChanged("")
        }
    }

    val speechRecognitionListener = object : RecognitionListener {
        override fun onReadyForSpeech(params: Bundle?) {
            Log.d(TAG, "onReadyForSpeech")
        }

        override fun onBeginningOfSpeech() {
            Log.d(TAG, "onBeginningOfSpeech")
        }

        override fun onRmsChanged(rmsdB: Float) {
            currentRms = rmsdB
        }

        override fun onBufferReceived(buffer: ByteArray?) {
            Log.d(TAG, "onBufferReceived")
        }

        override fun onEndOfSpeech() {
            Log.d(TAG, "onEndOfSpeech")
        }

        override fun onError(error: Int) {
            if (!listeningState && error == SpeechRecognizer.ERROR_CLIENT) return
            val errorMessage = recognitionListenerErrorText(error)
            Log.e(TAG, "onError: $errorMessage")
            currentOnResult(SpeechRecognitionResult.Error(errorMessage))
            onlListeningStateChanged(false)
        }

        override fun onResults(results: Bundle?) {
            onlListeningStateChanged(false)
            val matches = results?.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)
            val match = matches?.get(0)
            if (!match.isNullOrEmpty()) {
                Log.d(TAG, "onResults: >$match<")
                onRecognizedSpeechChanged(match)
                currentOnResult(SpeechRecognitionResult.Success(match))
            } else {
                Log.d(TAG, "onResults: error no results")
                currentOnResult(SpeechRecognitionResult.Error(context.getString(R.string.no_speech_recognized)))
            }
        }

        override fun onPartialResults(partialResults: Bundle?) {
            val matches = partialResults?.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)
            val match = matches?.get(0)
            match?.length?.let {
                if (it > 0) {
                    onRecognizedSpeechChanged(match)
                    Log.d(TAG, "onPartialResults: >$match<")
                }
            }
        }

        override fun onEvent(eventType: Int, params: Bundle?) {
            Log.d(TAG, "onEvent")
        }
    }

    // create the SpeechRecognizer
    if (speechRecognizer == null) {
        speechRecognizer = SpeechRecognizer.createSpeechRecognizer(context)
        speechRecognizer?.setRecognitionListener(speechRecognitionListener)
    }

    // Lifecycle handling to destroy the recognizer when the composable is destroyed
    val lifecycleOwner = LocalLifecycleOwner.current
    DisposableEffect(lifecycleOwner) {
        val observer = LifecycleEventObserver { _, event ->
            if (event == Lifecycle.Event.ON_DESTROY) {
                speechRecognizer?.destroy()
            }
        }
        lifecycleOwner.lifecycle.addObserver(observer)
        onDispose {
            lifecycleOwner.lifecycle.removeObserver(observer)
        }
    }

    // button to start/stop listening
    SpeechListenerButton(
        modifier = modifier,
        listeningState = listeningState,
        isProcessing = isProcessing,
        onlListeningStateChanged = onlListeningStateChanged,
        fieldsetIsCompleteAndValid = fieldsetIsCompleteAndValid,
        currentRms = currentRms, // Pass RMS to the button and content
    )
}

@Composable
fun SpeechListenerButton(
    modifier: Modifier,
    listeningState: Boolean,
    onlListeningStateChanged: (Boolean) -> Unit,
    fieldsetIsCompleteAndValid: Boolean,
    currentRms: Float,
    isProcessing: Boolean,
) {
    Button(
        onClick = {
            if (listeningState || isProcessing) {
                // take no action whilst receiving voice input or processing
            } else {
                onlListeningStateChanged(true)
            }
        },
        modifier = modifier,

        colors = ButtonDefaults.buttonColors(
            containerColor = when {
                isProcessing ->
                    MaterialTheme.colorScheme.primary

                fieldsetIsCompleteAndValid || listeningState ->
                    MaterialTheme.colorScheme.secondaryContainer

                else ->
                    MaterialTheme.colorScheme.primary
            }
        )
    ) {
        Row {
            when {
                listeningState -> {
                    CurrentlyListening(
                        modifier = modifier,
                        currentRms = currentRms,
                    )
                }

                isProcessing -> {
                    CurrentlyProcessing()
                }

                fieldsetIsCompleteAndValid -> {
                    Icon(
                        painter = painterResource(R.drawable.baseline_mic_24),
                        contentDescription = "Navigate home",
                        tint = MaterialTheme.colorScheme.onSecondaryContainer
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Box(modifier = Modifier.align(alignment = CenterVertically)) {
                        Text(
                            "Edit",
                            color = MaterialTheme.colorScheme.onSecondaryContainer,
                            fontSize = 16.sp
                        )
                    }
                }

                else -> {
                    Icon(
                        painter = painterResource(R.drawable.baseline_mic_24),
                        contentDescription = "Start listening for audio"
                    )
                }
            }
        }
    }
}

@Composable
fun CurrentlyListening(
    modifier: Modifier = Modifier,
    currentRms: Float,
) {
    val endElementWidth = 26.dp
    Row(
        modifier = modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.SpaceBetween
    ) {
        Row(
            modifier = Modifier
                .width(endElementWidth)
                .align(CenterVertically)
        ) {
            Icon(
                painter = painterResource(R.drawable.baseline_mic_24),
                contentDescription = "Microphone icon",
                modifier = Modifier
                    .weight(1f)
                    .size(endElementWidth),
                tint = MaterialTheme.colorScheme.onSecondaryContainer
            )
        }
        Box(
            modifier = Modifier
                .size(280.dp)
                .height(40.dp)
        ) {
            AnimatedAudioFeedback(
                modifier = Modifier.align(Alignment.Center),
                isPlaying = currentRms > 0 // true if we are receiving audio
            )
        }

        // This spacer should match the width of the microphone icon so that the 3 row elements
        // are evenly arranged left/center/middle
        Spacer(modifier = Modifier.width(endElementWidth))
    }
}

@Composable
fun CurrentlyProcessing(
    modifier: Modifier = Modifier,
) {
    Row(
        modifier = modifier
            .fillMaxWidth()
            .background(MaterialTheme.colorScheme.primary),
        horizontalArrangement = Arrangement.SpaceBetween
    ) {
        Box(
            modifier = Modifier
                .fillMaxSize(),
            contentAlignment = Alignment.Center
        ) {
            CircularProgressIndicator(
                modifier = Modifier.size(24.dp),
                color = MaterialTheme.colorScheme.onPrimary,
                strokeWidth = 2.dp
            )
        }
    }
}

@Composable
fun AnimatedAudioFeedback(
    modifier: Modifier = Modifier,
    isPlaying: Boolean,
) {
    val composition by rememberLottieComposition(
        LottieCompositionSpec.Asset("audio_feedback.json")
    )

    var animateLottie by remember { mutableStateOf(false) }

    LaunchedEffect(isPlaying) {
        if (isPlaying) {
            delay(250) // Delay the start of the animation by 250 milliseconds
            animateLottie = true
        } else {
            animateLottie = false
        }
    }

    // Animate progress only when isPlaying is true
    val animatedProgress by animateLottieCompositionAsState(
        composition,
        iterations = LottieConstants.IterateForever,
        restartOnPlay = true,
        isPlaying = isPlaying
    )

    // Use animatedProgress when isPlaying is true, otherwise use 0f
    val currentProgress = if (isPlaying) animatedProgress else 0f

    LottieAnimation(
        composition = composition,
        progress = currentProgress, // Use the determined progress
        modifier = modifier,
        contentScale = ContentScale.FillWidth
    )
}

@Composable
fun AnimatedStarIcon() {
    var isLiked by remember { mutableStateOf(false) }

    val iconColor by animateColorAsState(
        targetValue = if (isLiked) Color.Red else Color.Gray,
        animationSpec = tween(durationMillis = 500, easing = FastOutSlowInEasing),
        label = "StarColorAnimation"
    )

    val iconSize by animateDpAsState(
        targetValue = if (isLiked) 48.dp else 32.dp,
        animationSpec = tween(durationMillis = 500, easing = FastOutSlowInEasing),
        label = "StarSizeAnimation"
    )


    Column(
        modifier = Modifier
            .padding(8.dp)
            .clickable { isLiked = !isLiked }
    ) {
        Icon(
            imageVector = Icons.Default.Star,
            contentDescription = null,
            tint = iconColor,
            modifier = Modifier
                .size(iconSize)
                .padding(4.dp)
        )
    }
}

fun recognitionListenerErrorText(errorCode: Int): String {
    return when (errorCode) {
        1 -> "ERROR_NETWORK_TIMEOUT"
        2 -> "ERROR_NETWORK"
        3 -> "ERROR_AUDIO"
        4 -> "ERROR_SERVER"
        5 -> "ERROR_CLIENT"
        6 -> "ERROR_SPEECH_TIMEOUT"
        7 -> "Unrecognized speech. Please try again."
        8 -> "ERROR_RECOGNIZER_BUSY"
        9 -> "ERROR_INSUFFICIENT_PERMISSIONS"
        10 -> "ERROR_TOO_MANY_REQUESTS"
        11 -> "ERROR_SERVER_DISCONNECTED"
        12 -> "ERROR_LANGUAGE_NOT_SUPPORTED"
        13 -> "ERROR_LANGUAGE_UNAVAILABLE"
        14 -> "ERROR_CANNOT_CHECK_SUPPORT"
        15 -> "ERROR_CLIENT_ERROR"
        16 -> "ERROR_SERVER_ERROR"
        17 -> "ERROR_SERVER_TIMEOUT"
        18 -> "ERROR_CLIENT_TIMEOUT"
        19 -> "ERROR_NO_MATCH"
        20 -> "ERROR_RECOGNIZER_BUSY"
        21 -> "ERROR_INSUFFICIENT_PERMISSIONS"
        22 -> "ERROR_TOO_MANY_REQUESTS"
        23 -> "ERROR_SERVER_DISCONNECTED"
        24 -> "ERROR_LANGUAGE_NOT_SUPPORTED"
        25 -> "ERROR_LANGUAGE_UNAVAILABLE"
        26 -> "ERROR_CANNOT_CHECK_SUPPORT"
        else -> "Unknown error"
    }
}