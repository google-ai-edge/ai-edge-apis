package com.google.sample.fcdemo.ui.components

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.FlowRow
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.selection.selectableGroup
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Check
import androidx.compose.material3.FilterChip
import androidx.compose.material3.FilterChipDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp

@Composable
fun DemoChipGroup(
    label: String,
    options: Map<String, Boolean>,
    onValueChange: (String, Boolean) -> Unit,
) {
    Column {
        Text(
            text = label,
            style = MaterialTheme.typography.titleLarge
        )

        Spacer(modifier = Modifier.height(12.dp))

        FlowRow(
            modifier = Modifier
                .fillMaxWidth()
                .selectableGroup(),
        ) {
            options.forEach { (text, isSelected) ->
                FilterChip(
                    selected = isSelected,
                    onClick = {
                        onValueChange(text, !isSelected)
                    },
                    label = { Text(text = text, fontSize = 18.sp) },
                    modifier = Modifier
                        .height(height = 52.dp)
                        .padding(end = 8.dp, bottom = 8.dp),
                    leadingIcon = {
                        if (isSelected) {
                            Icon(
                                imageVector = Icons.Filled.Check,
                                contentDescription = "Selected"
                            )
                        }
                    },
                    colors = FilterChipDefaults.filterChipColors(
                        containerColor = MaterialTheme.colorScheme.surface,
                    )
                )
            }
        }
    }
}