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
import com.google.sample.fcdemo.ui.components.DemoRadioGroupList
import com.google.sample.fcdemo.ui.components.DemoSegmentedButton
import com.google.sample.fcdemo.ui.components.DemoTopAppBar
import com.google.sample.fcdemo.utilities.SpeechRecognitionResult
import com.google.sample.fcdemo.viewmodel.FormViewModel
import com.google.sample.fcdemo.viewmodel.fetchFlow

@Composable
fun Fieldset2Screen(
    viewModel: FormViewModel,
    snackbarHostState: SnackbarHostState,
    navigationActions: MedicalFormNavigationActions,
) {
    val isProcessing by viewModel.isProcessing.collectAsStateWithLifecycle()

    val sex by viewModel.formData.fetchFlow("sex").collectAsStateWithLifecycle()
    val maritalStatus by viewModel.formData.fetchFlow("maritalStatus").collectAsStateWithLifecycle()
    val recognizedSpeech by viewModel.recognizedSpeech.collectAsStateWithLifecycle("")
    val onRecognizedSpeechChanged: (String) -> Unit =  viewModel::updateRecognizedSpeech

    val onSexChanged: (String?) -> Unit = viewModel::updateSex
    val onMaritalStatusChanged: (String?) -> Unit = viewModel::updateMaritalStatus

    var listeningState by remember { mutableStateOf(false) }
    val onlListeningStateChanged: (Boolean) -> Unit = { listeningState = it }

    val onVoiceRecognitionSuccess: (SpeechRecognitionResult.Success) -> Unit = { result ->
        viewModel.processVoiceInput(result.text, Destination.Fieldset2)
    }

    val onVoiceRecognitionError: (SpeechRecognitionResult.Error) -> Unit = { result ->
        viewModel.onVoiceRecognitionError(result.message)
    }

    Fieldset2Content(
        sex = sex?.toString(),
        maritalStatus = maritalStatus?.toString(),
        onSexChanged = onSexChanged,
        onMaritalStatusChanged = onMaritalStatusChanged,
        listeningState = listeningState,
        isProcessing = isProcessing,
        onlListeningStateChanged = onlListeningStateChanged,
        recognizedSpeech = recognizedSpeech,
        onRecognizedSpeechChanged = onRecognizedSpeechChanged,
        onVoiceRecognitionSuccess = onVoiceRecognitionSuccess,
        onVoiceRecognitionError = onVoiceRecognitionError,
        onContinuePressed = navigationActions.navigateToFieldset3,
        onBackPressed = navigationActions.navigateBack,
        onHomePressed = navigationActions.navigateToHome,
        snackbarHostState = snackbarHostState,
    )
}

@Composable
internal fun Fieldset2Content(
    sex: String?,
    onSexChanged: (String?) -> Unit,
    maritalStatus: String?,
    onMaritalStatusChanged: (String?) -> Unit,
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
    val fieldsetIsCompleteAndValid = !sex.isNullOrEmpty() && !maritalStatus.isNullOrEmpty()

    Scaffold(
        topBar = {
            DemoTopAppBar(
                destination = Destination.Fieldset2,
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
                    text = stringResource(R.string.what_is_your_sex_and_marital_status),
                    style = MaterialTheme.typography.headlineMedium
                )

                Spacer(modifier = Modifier.height(16.dp))

                DemoSegmentedButton(
                    value = sex,
                    options = Tools.sexOptions,
                    onValueChange = onSexChanged,
                    label = stringResource(R.string.sex),
                )

                Spacer(modifier = Modifier.height(32.dp))

                DemoRadioGroupList(
                    value = maritalStatus,
                    options = Tools.maritalStatusOptions,
                    onValueChange = onMaritalStatusChanged,
                    label = stringResource(R.string.marital_status),
                )

                Spacer(Modifier.weight(1f))

                Text(text = recognizedSpeech)

                Spacer(Modifier.height(16.dp))

                DemoBottomButtonBar(
                    fieldsetIsCompleteAndValid = fieldsetIsCompleteAndValid,
                    listeningState = listeningState,
                    isProcessing = isProcessing,
                    onlListeningStateChanged = onlListeningStateChanged,
                    onRecognizedSpeechChanged =  onRecognizedSpeechChanged,
                    onVoiceRecognitionSuccess = onVoiceRecognitionSuccess,
                    onVoiceRecognitionError = onVoiceRecognitionError,
                    onContinuePressed = onContinuePressed
                )
            }
        }
    }
}

@Preview("Fieldset2 Preview")
@Composable
fun PreviewFieldset2Content() {
    Fieldset2Content(
        sex = null,
        onSexChanged = { },
        maritalStatus = null,
        onMaritalStatusChanged = { },
        listeningState = false,
        isProcessing = false,
        onlListeningStateChanged = { },
        recognizedSpeech = "I am a married man",
        onRecognizedSpeechChanged =  { },
        onVoiceRecognitionSuccess = { },
        onVoiceRecognitionError = { },
        onContinuePressed = { },
        onBackPressed = { },
        onHomePressed = { },
        snackbarHostState = SnackbarHostState(),
    )
}
