package com.google.sample.fcdemo.ui.screens

import android.R.attr.background
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.offset
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.SnackbarHost
import androidx.compose.material3.SnackbarHostState
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalView
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.core.graphics.luminance
import androidx.core.view.WindowInsetsControllerCompat
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.google.sample.fcdemo.R
import com.google.sample.fcdemo.navigation.Destination
import com.google.sample.fcdemo.navigation.MedicalFormNavigationActions
import com.google.sample.fcdemo.ui.components.DemoBottomButtonBar
import com.google.sample.fcdemo.ui.components.DemoCalendarTextField
import com.google.sample.fcdemo.ui.components.DemoTopAppBar
import com.google.sample.fcdemo.ui.components.SpeechBubblePrompt
import com.google.sample.fcdemo.ui.components.DemoTextField
import com.google.sample.fcdemo.utilities.SpeechRecognitionResult
import com.google.sample.fcdemo.viewmodel.FormViewModel
import com.google.sample.fcdemo.viewmodel.fetchFlow


const val TAG = "Fieldset1Screen"

@Composable
fun Fieldset1Screen(
    viewModel: FormViewModel,
    snackbarHostState: SnackbarHostState,
    navigationActions: MedicalFormNavigationActions,
) {
    val view = LocalView.current
    val isLightTheme = background.luminance > 0.5

    LaunchedEffect(view, isLightTheme) {
        val window = (view.context as? android.app.Activity)?.window
        if (window != null) {
            val controller = WindowInsetsControllerCompat(window, view)
            controller.isAppearanceLightStatusBars = !isLightTheme
        }
    }

    var prompt by remember { mutableStateOf("") }
    val hasRunOnce by viewModel.hasRunOnce.collectAsStateWithLifecycle()
    val hasShownPrompt by viewModel.hasShownPrompt.collectAsStateWithLifecycle()
    val isProcessing by viewModel.isProcessing.collectAsStateWithLifecycle()
    val recognizedSpeech by viewModel.recognizedSpeech.collectAsStateWithLifecycle("")
    val onRecognizedSpeechChanged: (String) -> Unit = viewModel::updateRecognizedSpeech

    val onDismissPrompt = {
        prompt = ""
    }

    LaunchedEffect(hasShownPrompt) {
        if (!hasShownPrompt) {
            prompt = "Tap below and start speaking. We’ll fill out your form based on your answers."
        }
        viewModel.setHasShownPrompt()
    }

    if (recognizedSpeech.isNotBlank()) {
        prompt = ""
    }

    val firstName by viewModel.formData.fetchFlow("firstName").collectAsStateWithLifecycle()
    val lastName by viewModel.formData.fetchFlow("lastName").collectAsStateWithLifecycle()
    val dob by viewModel.formData.fetchFlow("dob").collectAsStateWithLifecycle()
    val occupation by viewModel.formData.fetchFlow("occupation").collectAsStateWithLifecycle()

    val onFirstNameChanged: (String) -> Unit = viewModel::updateFirstName
    val onLastNameChanged: (String) -> Unit = viewModel::updateLastName
    val onDobChanged: (String) -> Unit = viewModel::updateDob
    val onOccupationChanged: (String) -> Unit = viewModel::updateOccupation

    var listeningState by remember { mutableStateOf(false) }
    val onlListeningStateChanged: (Boolean) -> Unit = { listeningState = it }

    val onVoiceRecognitionSuccess: (SpeechRecognitionResult.Success) -> Unit = { result ->
        viewModel.processVoiceInput(result.text, Destination.Fieldset1)
    }

    val onVoiceRecognitionError: (SpeechRecognitionResult.Error) -> Unit = { result ->
        viewModel.onVoiceRecognitionError(result.message)
    }

    Fieldset1Content(
        firstName = firstName.toString(),
        lastName = lastName.toString(),
        dob = dob.toString(),
        occupation = occupation.toString(),
        onFirstNameChanged = onFirstNameChanged,
        onLastNameChanged = onLastNameChanged,
        onDobChanged = onDobChanged,
        onOccupationChanged = onOccupationChanged,
        prompt = prompt,
        onDismissPrompt = onDismissPrompt,
        hasRunOnce = hasRunOnce,
        listeningState = listeningState,
        isProcessing = isProcessing,
        onlListeningStateChanged = onlListeningStateChanged,
        recognizedSpeech = recognizedSpeech,
        onRecognizedSpeechChanged = onRecognizedSpeechChanged,
        onVoiceRecognitionSuccess = onVoiceRecognitionSuccess,
        onVoiceRecognitionError = onVoiceRecognitionError,
        onContinuePressed = navigationActions.navigateToFieldset2,
        onBackPressed = navigationActions.navigateBack,
        onHomePressed = navigationActions.navigateToHome,
        snackbarHostState = snackbarHostState,
    )
}

@Composable
internal fun Fieldset1Content(
    firstName: String,
    lastName: String,
    dob: String,
    occupation: String,
    onFirstNameChanged: (String) -> Unit,
    onLastNameChanged: (String) -> Unit,
    onDobChanged: (String) -> Unit,
    onOccupationChanged: (String) -> Unit,
    prompt: String,
    onDismissPrompt: () -> Unit,
    hasRunOnce: Boolean,
    listeningState: Boolean,
    isProcessing: Boolean,
    onlListeningStateChanged: (Boolean) -> Unit,
    recognizedSpeech: String,
    onRecognizedSpeechChanged: (String) -> Unit,
    onVoiceRecognitionSuccess: (SpeechRecognitionResult.Success) -> Unit,
    onVoiceRecognitionError: (SpeechRecognitionResult.Error) -> Unit,
    onContinuePressed: () -> Unit,
    onBackPressed: () -> Unit,
    onHomePressed: () -> Unit,
    snackbarHostState: SnackbarHostState,
) {
    val fieldsetIsCompleteAndValid =
        firstName.isNotBlank() && lastName.isNotBlank() && dob.isNotBlank() && occupation.isNotBlank()

    Scaffold(
        topBar = {
            DemoTopAppBar(
                destination = Destination.Fieldset1,
                title = stringResource(R.string.empty_field),
                onBackPressed = onBackPressed,
                onHomePressed = onHomePressed,
            )
        },
        snackbarHost = { SnackbarHost(
            hostState = snackbarHostState,
            modifier = Modifier.offset(y = (-60).dp),
        ) },
        containerColor = MaterialTheme.colorScheme.surface,
    ) { innerPadding ->
        Surface(
            modifier = Modifier.padding(innerPadding),
            color = MaterialTheme.colorScheme.surface,
        ) {
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(start = 20.dp, end = 20.dp, top = 8.dp, bottom = 8.dp),
            ) {
                Text(
                    text = stringResource(R.string.what_is_your_name_date_of_birth_and_occupation),
                    style = MaterialTheme.typography.headlineMedium
                )

                Spacer(modifier = Modifier.height(16.dp))

                DemoTextField(
                    value = firstName,
                    onValueChange = onFirstNameChanged,
                    label = { Text(stringResource(R.string.first_name)) },
                    listeningState = listeningState,
                    onlListeningStateChanged = onlListeningStateChanged,
                    hasRunOnce = hasRunOnce,
                )

                Spacer(modifier = Modifier.height(16.dp))

                DemoTextField(
                    value = lastName,
                    onValueChange = onLastNameChanged,
                    label = { Text(stringResource(R.string.last_name)) },
                    listeningState = listeningState,
                    onlListeningStateChanged = onlListeningStateChanged,
                    hasRunOnce = hasRunOnce,
                )

                Spacer(modifier = Modifier.height(16.dp))

                DemoCalendarTextField(
                    date = dob,
                    onValueChange = onDobChanged,
                    hasRunOnce = hasRunOnce,
                )

                Spacer(modifier = Modifier.height(16.dp))

                DemoTextField(
                    value = occupation,
                    onValueChange = onOccupationChanged,
                    label = { Text(stringResource(R.string.occupation)) },
                    listeningState = listeningState,
                    onlListeningStateChanged = onlListeningStateChanged,
                    hasRunOnce = hasRunOnce,
                )

                Spacer(Modifier.weight(1f))

                if (prompt.isNotBlank()) {
                    SpeechBubblePrompt(
                        prompt = prompt,
                        onDismiss = onDismissPrompt,
                    )
                }

                if (recognizedSpeech.isNotBlank()) {
                    Text(
                        text = recognizedSpeech,
                        modifier = Modifier.padding(bottom = 16.dp)
                    )
                }

                DemoBottomButtonBar(
                    fieldsetIsCompleteAndValid = fieldsetIsCompleteAndValid,
                    listeningState = listeningState,
                    isProcessing = isProcessing,
                    onlListeningStateChanged = onlListeningStateChanged,
                    onRecognizedSpeechChanged = onRecognizedSpeechChanged,
                    onVoiceRecognitionSuccess = onVoiceRecognitionSuccess,
                    onVoiceRecognitionError = onVoiceRecognitionError,
                    onContinuePressed = onContinuePressed
                )
            }
        }
    }
}

@Preview("Fieldset1 Preview Preview")
@Composable
fun PreviewFieldset1Content() {
    Fieldset1Content(
        firstName = "John",
        lastName = "Smith",
        dob = "",
        occupation = "bricklayer",
        onFirstNameChanged =  { },
        onLastNameChanged = { },
        onDobChanged = { },
        onOccupationChanged = { },
        prompt = "Tap below and start speaking. We’ll fill out your form based on your answers.",
        onDismissPrompt = { },
        hasRunOnce = true,
        listeningState = true,
        isProcessing = false,
        onlListeningStateChanged = { },
        recognizedSpeech = "", //"My name is John Smith",
        onRecognizedSpeechChanged = { },
        onVoiceRecognitionSuccess = { },
        onVoiceRecognitionError = { },
        onContinuePressed = { },
        onBackPressed = { },
        onHomePressed = { },
        snackbarHostState = SnackbarHostState(),
    )
}
