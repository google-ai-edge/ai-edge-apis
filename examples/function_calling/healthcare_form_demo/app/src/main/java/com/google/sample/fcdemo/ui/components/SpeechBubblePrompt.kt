package com.google.sample.fcdemo.ui.components

import androidx.compose.animation.AnimatedVisibility
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
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.unit.dp
import kotlinx.coroutines.delay
import kotlin.time.Duration
import kotlin.time.Duration.Companion.seconds

// Custom shape for the speech bubble
private val BubbleShape = RoundedCornerShape(12.dp)

@Composable
fun SpeechBubblePrompt(
    prompt: String,
    onDismiss: () -> Unit,
    duration: Duration = 5.seconds,
    modifier: Modifier = Modifier,
) {
    var visible by remember { mutableStateOf(true) }

    LaunchedEffect(Unit) {
        delay(duration.inWholeMilliseconds)
        onDismiss()
    }

    // Enter/Exit animation for the whole message
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
                        modifier = Modifier.padding(12.dp),
                        verticalAlignment = Alignment.CenterVertically,
                    ) {
                        Text(
                            text = prompt,
                            color = MaterialTheme.colorScheme.onBackground,
                            style = MaterialTheme.typography.bodyLarge,
                        )
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
        )
    }
}

@Composable
private fun SpeechBubbleLayout(
    modifier: Modifier = Modifier,
    bubbleContent: @Composable () -> Unit,
    tailContent: @Composable () -> Unit,
) {
    // Use a Column to stack the bubble and tail vertically
    Column(
        modifier = modifier.offset(y = 20.dp),
        horizontalAlignment = Alignment.CenterHorizontally, // Center the bubble and tail
        verticalArrangement = Arrangement.Bottom
    ) {
        bubbleContent() // The main bubble content
        tailContent()   // The tail
    }
}