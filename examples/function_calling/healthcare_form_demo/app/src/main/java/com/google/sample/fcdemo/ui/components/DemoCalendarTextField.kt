package com.google.sample.fcdemo.ui.components

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material3.Button
import androidx.compose.material3.DatePicker
import androidx.compose.material3.DatePickerDialog
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextFieldDefaults
import androidx.compose.material3.SelectableDates
import androidx.compose.material3.Text
import androidx.compose.material3.TextField
import androidx.compose.material3.rememberDatePickerState
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.focus.FocusRequester
import androidx.compose.ui.focus.focusRequester
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.tooling.preview.Preview
import java.time.LocalDate
import java.time.format.DateTimeFormatter
import java.util.Locale

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun DemoCalendarTextField(
    date: String,
    onValueChange: (String) -> Unit,
    hasRunOnce: Boolean,
) {
    var showDatePicker by remember { mutableStateOf(false) }
    val focusRequester = remember { FocusRequester() }
    val dateFormatter = DateTimeFormatter.ofPattern("MM/dd/yyyy", Locale.getDefault())


    val datePickerState = rememberDatePickerState(
        initialSelectedDateMillis = LocalDate.now()
            .toEpochDay() * 24 * 60 * 60 * 1000, // Today's date in millis
        yearRange = 1900..2100,
        selectableDates = object : SelectableDates {
//            override fun isSelectableDate(date: LocalDate): Boolean {
//                // Example: Disable dates before today
//                return date.isBefore(LocalDate.now()).not()
//            }
        }
    )

    if (showDatePicker) {
        DatePickerDialog(
            onDismissRequest = { showDatePicker = false },
            confirmButton = {
                Button(onClick = {
                    datePickerState.selectedDateMillis?.let {
                        val selectedDate = LocalDate.ofEpochDay(it / (24 * 60 * 60 * 1000))
                        onValueChange(dateFormatter.format(selectedDate))
                    }
                    showDatePicker = false
                }) {
                    Text("OK")
                }
            },
            dismissButton = {
                Button(onClick = { showDatePicker = false }) {
                    Text("Cancel")
                }
            }
        ) {
            DatePicker(state = datePickerState)
        }
    }

    LaunchedEffect(showDatePicker) {
        if (showDatePicker) {
            focusRequester.requestFocus()
        }
    }

    Box {
        TextField(
            value = date,
            onValueChange = { onValueChange(date) },
            label = { Text("Date of Birth") },
            isError = date.isEmpty() && hasRunOnce,
            modifier = Modifier
                .fillMaxWidth()
                .focusRequester(focusRequester),
            readOnly = true, // Make it read-only
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
            placeholder = { Text(text = "mm/dd/yyyy") },
            colors = OutlinedTextFieldDefaults.colors(
                unfocusedContainerColor = MaterialTheme.colorScheme.surfaceContainer,
                focusedContainerColor = MaterialTheme.colorScheme.surfaceContainer
            ),
        )

        Box(
            modifier = Modifier
                .matchParentSize()
                .alpha(0f)
                .clickable(onClick = { showDatePicker = true }),
        )
    }


}

@Preview(showBackground = true)
@Composable
fun PreviewDemoCalendarTextField() {
    DemoCalendarTextField("", { }, false)
}