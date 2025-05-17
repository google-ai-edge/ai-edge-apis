package com.google.sample.fcdemo.ui.screens

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
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.google.sample.fcdemo.R
import com.google.sample.fcdemo.functioncalling.Tools
import com.google.sample.fcdemo.navigation.MedicalFormNavigationActions
import com.google.sample.fcdemo.navigation.Destination
import com.google.sample.fcdemo.ui.components.DemoBottomButtonBar
import com.google.sample.fcdemo.ui.components.DemoChipGroup
import com.google.sample.fcdemo.ui.components.DemoTopAppBar
import com.google.sample.fcdemo.utilities.SpeechRecognitionResult
import com.google.sample.fcdemo.viewmodel.FormViewModel
import com.google.sample.fcdemo.viewmodel.fetchFlow

@Composable
fun Fieldset3Screen(
    viewModel: FormViewModel,
    snackbarHostState: SnackbarHostState,
    navigationActions: MedicalFormNavigationActions,
) {
    val isProcessing by viewModel.isProcessing.collectAsStateWithLifecycle()
    val recognizedSpeech by viewModel.recognizedSpeech.collectAsStateWithLifecycle("")
    val onRecognizedSpeechChanged: (String) -> Unit =  viewModel::updateRecognizedSpeech

    val medicalConditions by  viewModel.formData.fetchFlow("medicalConditions").collectAsStateWithLifecycle()
    val onMedicalConditionChanged: (String, Boolean) -> Unit = viewModel::updateMedicalCondition

    var listeningState by remember { mutableStateOf(false) }
    val onlListeningStateChanged: (Boolean) -> Unit = { listeningState = it }

    val onVoiceRecognitionSuccess: (SpeechRecognitionResult.Success) -> Unit = { result ->
        viewModel.processVoiceInput(result.text, Destination.Fieldset3)
    }

    val onVoiceRecognitionError: (SpeechRecognitionResult.Error) -> Unit = { result ->
        viewModel.onVoiceRecognitionError(result.message)
    }

    @Suppress("UNCHECKED_CAST")
    Fieldset3Content(
        medicalConditions = medicalConditions as Map<String, Boolean>,
        onMedicalConditionChanged = onMedicalConditionChanged,
        listeningState = listeningState,
        isProcessing = isProcessing,
        onlListeningStateChanged = onlListeningStateChanged,
        recognizedSpeech = recognizedSpeech,
        onRecognizedSpeechChanged = onRecognizedSpeechChanged,
        onVoiceRecognitionSuccess = onVoiceRecognitionSuccess,
        onVoiceRecognitionError = onVoiceRecognitionError,
        onContinuePressed = navigationActions.navigateToSummary,
        onBackPressed = navigationActions.navigateBack,
        onHomePressed = navigationActions.navigateToHome,
        snackbarHostState = snackbarHostState,
    )
}

@Composable
internal fun Fieldset3Content(
    medicalConditions: Map<String, Boolean>,
    onMedicalConditionChanged: (String, Boolean) -> Unit,
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
    // it is possible the patient has none of the possible conditions
    val fieldsetIsCompleteAndValid = true

    Scaffold(
        topBar = {
            DemoTopAppBar(
                destination = Destination.Fieldset3,
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
                    text = stringResource(R.string.medical_conditions),
                    style = MaterialTheme.typography.headlineMedium
                )

                Spacer(modifier = Modifier.height(16.dp))

                DemoChipGroup(
                    label = "Say all that apply",
                    options = medicalConditions,
                    onValueChange = onMedicalConditionChanged,
                )

                Spacer(Modifier.weight(1f))

                Text(text = recognizedSpeech)

                Spacer(Modifier.height(16.dp))

                DemoBottomButtonBar(
                    fieldsetIsCompleteAndValid = fieldsetIsCompleteAndValid,
                    listeningState = listeningState,
                    isProcessing = isProcessing,
                    onlListeningStateChanged = onlListeningStateChanged,
                    onVoiceRecognitionSuccess = onVoiceRecognitionSuccess,
                    onRecognizedSpeechChanged =  onRecognizedSpeechChanged,
                    onVoiceRecognitionError = onVoiceRecognitionError,
                    onContinuePressed = onContinuePressed
                )
            }
        }
    }
}

@Preview("Fieldset3 Preview")
@Composable
fun PreviewFieldset3Content() {
    val medicalConditions = Tools.medicalConditionsOptions.fold(mutableMapOf<String, Boolean>()) { outmap, condition ->
        outmap[condition] = ("Asthma-Migraines-Kidney Disease".contains(condition))
        outmap
    }
    Fieldset3Content(
        medicalConditions = medicalConditions,
        onMedicalConditionChanged = { _, _ -> },
        listeningState = false,
        isProcessing = false,
        onlListeningStateChanged = { },
        recognizedSpeech = "I have been diagnosed with Heart Disease",
        onRecognizedSpeechChanged = { },
        onVoiceRecognitionSuccess = { },
        onVoiceRecognitionError = { },
        onContinuePressed = { },
        onBackPressed = { },
        onHomePressed = { },
        snackbarHostState = SnackbarHostState(),
    )
}
