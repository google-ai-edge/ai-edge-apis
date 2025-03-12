package com.google.ai.edge.samples.rag

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material.MaterialTheme
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Surface
import androidx.compose.ui.Modifier

class MainActivity : ComponentActivity() {
  lateinit var chatViewModel: ChatViewModel

  @ExperimentalMaterial3Api
  override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    chatViewModel = ChatViewModel(application)
    setContent {
      Surface(modifier = Modifier.fillMaxSize()) { MaterialTheme { NavView(chatViewModel) } }
    }
    chatViewModel.memorizeChunks("sample_context.txt")
  }

  private companion object {
    const val TAG = "MainActivity"
    const val PERMISSIONS_REQUEST = 1
  }
}
