package com.google.sample.fcdemo.ui.components

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.core.tween
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.offset
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.widthIn
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Info
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.SnackbarData
import androidx.compose.material3.SnackbarDuration
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.unit.Density
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch

@Composable
fun SpeechBubbleSnackbar(
    snackbarData: SnackbarData,
    modifier: Modifier = Modifier,
) {
    var visible by remember { mutableStateOf(false) }
    val density = LocalDensity.current
    val coroutineScope = rememberCoroutineScope()

    // Convert snackbarDuration to milliseconds
    val durationMillis = remember(snackbarData.visuals.duration) {
        getDurationMillis(snackbarData.visuals.duration)
    }

    // Function to show the Snackbar
    fun showSnackbar() {
        visible = true
        coroutineScope.launch {
            delay(durationMillis)
            visible = false
            snackbarData.dismiss()
        }
    }

    // Trigger showing the snackbar
    // Use message as key, so every new message will trigger showing.
    LaunchedEffect(snackbarData.visuals.message) {
        if (snackbarData.visuals.message.isNotBlank()) { // prevent showing when message is empty
            showSnackbar()
        }
    }

    // Enter/Exit animation for the whole snackbar
    AnimatedVisibility(
        visible = visible,
        enter = fadeIn(),
        exit = fadeOut(),
    ) {
        SpeechBubbleLayout(
            modifier = modifier,
            bubbleContent = {
                Surface(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(20.dp),
                    shape = BubbleShape,
                    color = MaterialTheme.colorScheme.primaryContainer, // background for the bubble
                ) {
                    Row(
                        modifier = Modifier.padding(16.dp),
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        Text(
                            text = snackbarData.visuals.message,
                            color = MaterialTheme.colorScheme.onPrimaryContainer,
                            style = MaterialTheme.typography.bodyMedium,
                            modifier = Modifier.weight(1f)
                        )
                        val actionLabel = snackbarData.visuals.actionLabel
                        if (actionLabel != null) {
                            TextButton(
                                onClick = {
                                    snackbarData.performAction()
                                    visible = false // Dismiss on action
                                    snackbarData.dismiss()
                                },
                            ) {
                                Text(
                                    text = actionLabel,
                                    color = MaterialTheme.colorScheme.tertiary,
                                    style = MaterialTheme.typography.bodyMedium,
                                )
                            }
                        }
                    }
                }
            },
            tailContent = {
                val tailColor = MaterialTheme.colorScheme.primaryContainer
                Canvas(
                    modifier = Modifier
                        .size(22.dp) // Size of the tail
                ) {
                    val tailPath = Path().apply {
                        // Draw a triangle pointing downwards
                        moveTo(size.width / 2f, 0f)
                        lineTo(0f, size.height * -1)
                        lineTo(size.width, size.height * -1)
                        close()
                    }
                    drawPath(
                        path = tailPath,
                        color = tailColor, // Match the bubble color
                    )
                }
            },
            density = density
        )
    }
}

@Composable
private fun SpeechBubbleLayout(
    modifier: Modifier = Modifier,
    bubbleContent: @Composable () -> Unit,
    tailContent: @Composable () -> Unit,
    density: Density,
) {
    // Use a Column to stack the bubble and tail vertically
    Column(
        modifier = modifier.offset(y = (-40).dp),
        horizontalAlignment = Alignment.CenterHorizontally, // Center the bubble and tail
        verticalArrangement = Arrangement.Bottom
    ) {
        bubbleContent() // The main bubble content
        tailContent()   // The tail
    }
}

// Custom shape for the speech bubble
private val BubbleShape = RoundedCornerShape(12.dp)

// Function to convert SnackbarDuration to milliseconds
private fun getDurationMillis(duration: SnackbarDuration): Long {
    return when (duration) {
        SnackbarDuration.Short -> 3000L // Short duration
        SnackbarDuration.Long -> 7000L  // Long duration
        SnackbarDuration.Indefinite -> Long.MAX_VALUE // Indefinite duration
    }
}