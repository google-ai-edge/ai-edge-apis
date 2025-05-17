package com.google.sample.fcdemo.ui.screens

import android.R.attr.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.offset
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.SnackbarHost
import androidx.compose.material3.SnackbarHostState
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalView
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.core.graphics.luminance
import androidx.core.view.WindowInsetsControllerCompat
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.google.sample.fcdemo.R
import com.google.sample.fcdemo.navigation.MedicalFormNavigationActions
import com.google.sample.fcdemo.viewmodel.FormViewModel

@Composable
fun HomeScreen(
    viewModel: FormViewModel,
    snackbarHostState: SnackbarHostState,
    navigationActions: MedicalFormNavigationActions,
) {
    val view = LocalView.current
    val isLightTheme = background.luminance > 0.5
    val isCompleteAndValid by viewModel.isCompleteAndValid.collectAsStateWithLifecycle()
    // if the user has attempted audio on Fieldset1 then the form is considered partially complete
    val isPartiallyComplete by viewModel.hasRunOnce.collectAsStateWithLifecycle()

    LaunchedEffect(view, isLightTheme) {
        val window = (view.context as? android.app.Activity)?.window
        if (window != null) {
            val controller = WindowInsetsControllerCompat(window, view)
            controller.isAppearanceLightStatusBars = isLightTheme
        }
    }

    val onRestartDemo = {
        viewModel.resetForm()
        navigationActions.navigateToHome()
    }

    HomeScreenContent(
        onStartPressed = navigationActions.navigateToFieldset1,
        onBackPressed = navigationActions.navigateBack,
        onHomePressed = navigationActions.navigateToHome,
        onRestartDemo = onRestartDemo,
        exitApplication = navigationActions.exitApplication,
        isCompleteAndValid = isCompleteAndValid,
        isPartiallyComplete = isPartiallyComplete,
        snackbarHostState = snackbarHostState,
    )
}

@Composable
fun HomeScreenContent(
    onStartPressed: () -> Unit,
    onBackPressed: () -> Unit,
    onHomePressed: () -> Unit,
    onRestartDemo: () -> Unit,
    exitApplication: () -> Unit,
    isCompleteAndValid: Boolean,
    snackbarHostState: SnackbarHostState,
    isPartiallyComplete: Boolean,
) {
    Scaffold(
        snackbarHost = { SnackbarHost(
            hostState = snackbarHostState,
            modifier = Modifier.offset(y = (-60).dp),
        ) },
        containerColor = MaterialTheme.colorScheme.onPrimaryContainer,
    ) { innerPadding ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding),
            contentAlignment = Alignment.Center
        ) {
            Column(
                modifier = Modifier.fillMaxWidth(),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                Text(
                    text = "medly",
                    color = MaterialTheme.colorScheme.surface,
                    style = MaterialTheme.typography.headlineLarge
                )
                Spacer(modifier = Modifier.height(24.dp))
                Text(
                    text = if (isCompleteAndValid) {
                        "Pre-registration complete!"
                    } else {
                        "Complete your pre-registration"
                    },
                    color = MaterialTheme.colorScheme.surface,
                    style = MaterialTheme.typography.titleLarge
                )
                Spacer(modifier = Modifier.height(8.dp))
                Text(
                    text = when {
                        isCompleteAndValid -> "Thanks for your update!"
                        else -> "We need some information to prepare for your upcoming visit. Please complete your pre-appointment form"
                    },
                    modifier = Modifier.padding(start = 31.dp, end = 31.dp),
                    color = MaterialTheme.colorScheme.surface,
                    textAlign = TextAlign.Center,
                    style = MaterialTheme.typography.bodyLarge
                )
                Spacer(modifier = Modifier.height(32.dp))
                when {
                    isPartiallyComplete -> {
                        Button(onClick = { onStartPressed() },
                            modifier = Modifier
                                .height(52.dp)
                                .width(200.dp)
                        ) {
                            Text("Continue Form", fontSize = 18.sp)
                        }
                        Spacer(modifier = Modifier.height(8.dp))
                        Button(onClick = { onRestartDemo() },
                            modifier = Modifier
                                .height(52.dp)
                                .width(200.dp)
                        ) {
                            Text("Start Over", fontSize = 18.sp)
                        }
                    }

                    isCompleteAndValid -> {
                        Button(onClick = { onRestartDemo() },
                            modifier = Modifier
                                .height(52.dp)
                                .width(200.dp)
                        ) {
                            Text("Restart Demo", fontSize = 18.sp)
                        }
                    }

                    else -> {
                        Button(onClick = { onStartPressed() },
                            modifier = Modifier
                                .height(52.dp)
                                .width(200.dp)
                        ) {
                            Text(stringResource(R.string.complete_form), fontSize = 18.sp)
                        }

                    }
                }
            }
        }
    }
}

@Preview("Home Screen Preview")
@Composable
fun PreviewHomeScreenContent() {
    HomeScreenContent(
        onStartPressed = { },
        onBackPressed = { },
        onHomePressed = { },
        onRestartDemo = { },
        exitApplication = { },
        isCompleteAndValid = false,
        isPartiallyComplete = true,
        snackbarHostState = SnackbarHostState(),
    )
}
