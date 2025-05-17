@file:OptIn(ExperimentalMaterial3Api::class)

package com.google.sample.fcdemo.ui.components

import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.outlined.Home
import androidx.compose.material3.CenterAlignedTopAppBar
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color
import com.google.sample.fcdemo.navigation.Destination
import com.google.sample.fcdemo.ui.theme.Hero

@Composable
fun DemoTopAppBar(
    destination: Destination,
    title: String,
    onBackPressed: () -> Unit,
    onHomePressed: () -> Unit,
) {
    CenterAlignedTopAppBar(
        title = {Text(text = title)},
        navigationIcon = {
            if (destination != Destination.Summary) {
                IconButton(
                    onClick = { onBackPressed() }) {
                    Icon(
                        imageVector = Icons.AutoMirrored.Filled.ArrowBack,
                        contentDescription = "Navigate back"
                    )
                }
            }
        },
        actions = {
            if (destination != Destination.Home) {
                IconButton(onClick = { onHomePressed() }) {
                    Icon(
                        imageVector = Icons.Outlined.Home,
                        contentDescription = "Navigate home"
                    )
                }
            }

        },
        colors = TopAppBarDefaults.topAppBarColors(
            containerColor = MaterialTheme.colorScheme.surface, // Background color of the TopAppBar
            actionIconContentColor = MaterialTheme.colorScheme.onPrimaryContainer // Color of action icons (if any)
        )
    )
}