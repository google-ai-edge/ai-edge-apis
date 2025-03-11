package com.google.ai.edge.samples.rag

import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.runtime.Composable
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController

@ExperimentalMaterial3Api
@Composable
fun NavView(chatViewModel: ChatViewModel) {
  val navController = rememberNavController()
  NavHost(navController = navController, startDestination = "chat") {
    composable("chat") { ChatView(chatViewModel) }
  }
}