package com.google.sample.fcdemo.activities

import android.Manifest
import android.content.pm.PackageManager
import android.os.Bundle
import android.util.Log
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.activity.result.contract.ActivityResultContracts
import androidx.core.content.ContextCompat
import androidx.lifecycle.lifecycleScope
import com.google.sample.fcdemo.R
import com.google.sample.fcdemo.navigation.MedicalFormNavHost
import com.google.sample.fcdemo.ui.theme.FunctionCallingDemoTheme
import com.google.sample.fcdemo.viewmodel.FormViewModel
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch

class MainActivity : ComponentActivity() {

    private val requestPermissionLauncher =
        registerForActivityResult(ActivityResultContracts.RequestPermission()) { isGranted ->
            if (isGranted) {
                startApp()
            } else {
                Log.e(localClassName, getString(R.string.missing_audio_permission_user_denied))
                finish() // Close the app if permission is denied
            }
        }

    override fun onCreate(savedInstanceState: Bundle?) {
        enableEdgeToEdge()
        super.onCreate(savedInstanceState)

        // Check for RECORD_AUDIO permission and handle accordingly.
        when (ContextCompat.checkSelfPermission(this, Manifest.permission.RECORD_AUDIO)) {
            PackageManager.PERMISSION_GRANTED -> {
                // Permission is already granted, start the app
                startApp()
            }

            else -> {
                // Permission is not granted, request it
                requestPermissionLauncher.launch(Manifest.permission.RECORD_AUDIO)
            }
        }
    }

    private fun startApp() {
        val formViewModel = FormViewModel()
        lifecycleScope.launch(Dispatchers.IO)  {
            // calling this method here will force the lazy instantiation of the chat service.
            // Starting the chat service is an expensive process, so starting it here should minimize
            // UI delay
            formViewModel.generativeModel
        }
        setContent {
            FunctionCallingDemoTheme {
                MedicalFormNavHost(formViewModel)
            }
        }
    }
}