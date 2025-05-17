package com.google.sample.fcdemo.ui.screens

import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.offset
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.ButtonDefaults.buttonColors
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.SnackbarHost
import androidx.compose.material3.SnackbarHostState
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateMapOf
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.google.sample.fcdemo.R
import com.google.sample.fcdemo.navigation.MedicalFormNavigationActions
import com.google.sample.fcdemo.navigation.Destination
import com.google.sample.fcdemo.ui.components.DemoTopAppBar
import com.google.sample.fcdemo.viewmodel.FormViewModel
import com.google.sample.fcdemo.viewmodel.fetchFlow

const val NOT_PROVIDED = "Not provided"

@Composable
fun SummaryScreen(
    viewModel: FormViewModel,
    snackbarHostState: SnackbarHostState,
    navigationActions: MedicalFormNavigationActions,
) {
    val isSaving by viewModel.isSaving.collectAsStateWithLifecycle()
    val isCompleteAndValid by viewModel.isCompleteAndValid.collectAsStateWithLifecycle()

    LaunchedEffect(isCompleteAndValid) {
        if (isCompleteAndValid) {
            navigationActions.navigateToHome()
        }
    }

    val onFieldsetEdits = listOf(
        { navigationActions.reviseFieldset1() },
        { navigationActions.reviseFieldset2() },
        { navigationActions.reviseFieldset3() },
    )

    val fieldsetMaps = remember { mutableStateMapOf<String, MutableMap<String, String>>() }

    viewModel.formData.forEach { data ->
        val fieldsetName = data.fieldset
        val label = data.label
        val value = formDataValue(viewModel, data.name)

        // Get the map for the fieldset, or create a new one if it doesn't exist.
        val fieldsetMap = fieldsetMaps.getOrPut(fieldsetName) { mutableMapOf() }
        fieldsetMap[label] = value
    }

    val parseConditionString: (String) -> List<String> = viewModel::parseConditionString

    SummaryContent(
        fieldsetMaps = fieldsetMaps,
        onFieldsetEdits = onFieldsetEdits,
        onSubmitPressed = viewModel::submitForm,
        onBackPressed = navigationActions.navigateBack,
        onHomePressed = navigationActions.navigateToHome,
        parseConditionString = parseConditionString,
        isSaving = isSaving,
        snackbarHostState = snackbarHostState,
    )
}

@Composable
internal fun SummaryContent(
    fieldsetMaps: MutableMap<String, MutableMap<String, String>>,
    onFieldsetEdits: List<() -> Unit>,
    onSubmitPressed: () -> Unit,
    onBackPressed: () -> Unit,
    onHomePressed: () -> Unit,
    parseConditionString: (String) -> List<String>,
    isSaving: Boolean,
    snackbarHostState: SnackbarHostState,
) {
    var formIncomplete = false
    Scaffold(
        topBar = {
            DemoTopAppBar(
                destination = Destination.Summary,
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
                    .padding(start = 20.dp, end = 20.dp, top = 20.dp, bottom = 8.dp)
            ) {
                Text(
                    text = "You're all done! Please make sure your info is correct before submitting.",
                    style = MaterialTheme.typography.headlineMedium
                )
                Spacer(modifier = Modifier.height(12.dp))

                Column(
                    modifier = Modifier
                        .weight(1f)
                        .verticalScroll(rememberScrollState()),
                ) {
                    Spacer(modifier = Modifier.height(4.dp))
                    Column {
                        fieldsetMaps.toList().forEachIndexed { index, mapData ->
                            Card(
                                modifier = Modifier,
                                shape = RoundedCornerShape(size = 4.dp),
                                colors = CardDefaults.cardColors(
                                    containerColor = MaterialTheme.colorScheme.tertiaryContainer,
                                ),
                            ) {
                                Box(modifier = Modifier.fillMaxWidth()) {
                                    Column {
                                        Spacer(modifier = Modifier.height(4.dp))
                                        Column(
                                            modifier = Modifier
                                                .fillMaxWidth()
                                                .padding(
                                                    start = 12.dp,
                                                    end = 12.dp,
                                                    top = 8.dp,
                                                    bottom = 8.dp
                                                )
                                        ) {

                                            mapData.second.forEach { (label, value) ->
                                                Text(
                                                    text = label,
                                                    style = MaterialTheme.typography.labelLarge
                                                )
                                                // The data is a String map of values = true/false
                                                // We are only interested in the true ones
                                                if (value.startsWith('{') && value.endsWith('}')) {
                                                    Column {
                                                        parseConditionString(value).forEach { condition ->
                                                            Text(
                                                                text = condition,
                                                                style = MaterialTheme.typography.bodyLarge
                                                            )
                                                            if (condition.endsWith(",")) {
                                                                Spacer(
                                                                    modifier = Modifier.height(
                                                                        4.dp
                                                                    )
                                                                )
                                                            }
                                                        }
                                                    }
                                                } else {
                                                    // The data is a a single value
                                                    val displayValue = when {
                                                        value.isEmpty() || value.equals(
                                                            "null",
                                                            ignoreCase = true
                                                        ) -> NOT_PROVIDED

                                                        else -> value
                                                    }
                                                    Text(
                                                        text = displayValue,
                                                        color = if (displayValue == NOT_PROVIDED) {
                                                            formIncomplete = true
                                                            MaterialTheme.colorScheme.error
                                                        } else {
                                                            MaterialTheme.colorScheme.onSurface
                                                        },
                                                        style = MaterialTheme.typography.bodyLarge
                                                    )
                                                    Spacer(modifier = Modifier.height(4.dp))
                                                }
                                            }
                                        }
                                    }
                                    Button(
                                        onClick = {
                                            onFieldsetEdits[index]()
                                        },
                                        modifier = Modifier
                                            .padding(12.dp)
                                            .align(Alignment.TopEnd),
                                        colors = buttonColors(
                                            containerColor = MaterialTheme.colorScheme.secondaryContainer,
                                        ),
                                    ) {
                                        Text(
                                            "Edit",
                                            color = MaterialTheme.colorScheme.onSecondaryContainer,
                                            fontSize = 16.sp
                                        )
                                    }
                                }
                            }
                            Spacer(modifier = Modifier.height(8.dp))
                        }
                    }
                }
                Spacer(modifier = Modifier.height(12.dp))
                Row {
                    Button(
                        onClick = { onSubmitPressed() },
                        modifier = Modifier
                            .weight(1f)
                            .height(52.dp)
                            .fillMaxWidth(),
                        enabled = !isSaving,
                        colors = ButtonDefaults.buttonColors(
                            disabledContainerColor =
                                MaterialTheme.colorScheme.primary.copy(alpha = .7f),

                        )
                    ) {
                        if (isSaving) {
                            CircularProgressIndicator(
                                modifier = Modifier.size(24.dp),
                                color = MaterialTheme.colorScheme.onPrimary,
                                strokeWidth = 2.dp
                            )
                        } else {
                            Text("Submit", fontSize = 16.sp)
                        }
                    }
                }
            }
        }
    }
}

@Composable
fun formDataValue(viewModel: FormViewModel, label: String): String {
    val value by viewModel.formData.fetchFlow(label).collectAsStateWithLifecycle()
    return value.toString()
}

@Preview("Fieldset3 Preview")
@Composable
fun PreviewSummaryContent() {
    val fieldset1Map: MutableMap<String, String> = mutableMapOf(
        "First Name" to "John",
        "Last Name" to "Doe",
        "Date of Birth" to "1990-01-01",
        "Occupation" to "Doctor",
    )
    val fieldset2Map: MutableMap<String, String> = mutableMapOf(
        "Sex" to NOT_PROVIDED,
        "Marital Status" to "Divorced",
    )
    val fieldset3Map: MutableMap<String, String> = mutableMapOf(
        "Anemia" to "true",
        "Heart Murmur" to "false",
        "Migraines" to "true",
        "Toothache" to "false",
        "Diabetes" to "true",
    )
    val fieldsetMaps = mutableMapOf(
        "Fieldset1" to fieldset1Map,
        "Fieldset2" to fieldset2Map,
        "Fieldset3" to fieldset3Map,
    )
    val conditions = listOf("Anemia,", "Heart Murmur,", "Migraines")
    SummaryContent(
        fieldsetMaps = fieldsetMaps,
        onFieldsetEdits = listOf({ }, { }, { }),
        onSubmitPressed = { },
        onBackPressed = { },
        onHomePressed = { },
        parseConditionString = { _ -> conditions },
        isSaving = false,
        snackbarHostState = SnackbarHostState(),
    )
}
