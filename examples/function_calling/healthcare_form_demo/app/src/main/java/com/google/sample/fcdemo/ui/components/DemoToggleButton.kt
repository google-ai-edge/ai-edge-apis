package com.google.sample.fcdemo.ui.components

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.SegmentedButton
import androidx.compose.material3.SegmentedButtonDefaults
import androidx.compose.material3.SingleChoiceSegmentedButtonRow
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp

@Composable
fun DemoSegmentedButton(
    value: String?,
    options: List<String>,
    onValueChange: (String) -> Unit,
    label: String,
) {
    val selectedIndex = options.indexOf(value)

    Column {
        Text(
            text = label,
            style = MaterialTheme.typography.titleLarge
        )

        Spacer(modifier = Modifier.height(16.dp))

        SingleChoiceSegmentedButtonRow(
            modifier = Modifier.fillMaxWidth(),
        ) {
            options.forEachIndexed { index, label ->
                SegmentedButton(
                    onClick = { onValueChange(label) },
                    shape = SegmentedButtonDefaults.itemShape(
                        index = index,
                        count = options.size
                    ),
                    modifier = Modifier.height(48.dp),
                    selected = index == selectedIndex,
                    label = { Text(text = label, fontSize = 18.sp) }
                )
            }
        }
    }
}