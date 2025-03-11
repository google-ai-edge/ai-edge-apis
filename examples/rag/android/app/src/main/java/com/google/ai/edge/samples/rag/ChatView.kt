package com.google.ai.edge.samples.rag

import androidx.compose.foundation.background
import androidx.compose.foundation.gestures.detectTapGestures
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.IntrinsicSize
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.aspectRatio
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.widthIn
import androidx.compose.foundation.layout.wrapContentHeight
import androidx.compose.foundation.layout.wrapContentWidth
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.selection.SelectionContainer
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.Send
import androidx.compose.material3.Divider
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.ExposedDropdownMenuBox
import androidx.compose.material3.ExposedDropdownMenuDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TextField
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.platform.LocalFocusManager
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import kotlinx.coroutines.launch

@Composable
/** Displays a standard divider. */
fun StandardDivider() {
  Divider(thickness = 1.dp, modifier = Modifier.padding(vertical = 3.dp))
}

@ExperimentalMaterial3Api
@Composable
/** Displays a dropdown menu with a list of LLMs. */
fun LlmModelSelectionDropdownMenu() {
  var expandModelDropdownMenu by remember { mutableStateOf(false) }

  Box(modifier = Modifier.fillMaxWidth(), contentAlignment = Alignment.TopStart) {
    ExposedDropdownMenuBox(
      expanded = expandModelDropdownMenu,
      onExpandedChange = { expandModelDropdownMenu = it },
    ) {
      TextField(
        value = "MediaPipe LLM",
        onValueChange = {},
        readOnly = true,
        trailingIcon = {
          ExposedDropdownMenuDefaults.TrailingIcon(expanded = expandModelDropdownMenu)
        },
        colors = ExposedDropdownMenuDefaults.textFieldColors(),
        modifier = Modifier.fillMaxWidth().menuAnchor(),
      )

      ExposedDropdownMenu(
        expanded = expandModelDropdownMenu,
        onDismissRequest = { expandModelDropdownMenu = false },
      ) {
      }
    }
  }
}

@ExperimentalMaterial3Api
@Composable
/**
 * Displays a chat view with a top bar, a dropdown menu, a message list and a message sending box.
 */
fun ChatView(viewModel: ChatViewModel) {
  val localFocusManager = LocalFocusManager.current
  val composableScope = rememberCoroutineScope()

  Scaffold(
    topBar = {
      TopAppBar(
        title = {
          Text(text = "On-device RAG pipeline", color = MaterialTheme.colorScheme.onPrimary)
        },
        colors =
          TopAppBarDefaults.topAppBarColors(containerColor = MaterialTheme.colorScheme.primary),
      )
    },
    modifier =
      Modifier.pointerInput(Unit) { detectTapGestures(onTap = { localFocusManager.clearFocus() }) },
  ) { paddingValues ->
    Column(modifier = Modifier.fillMaxSize().padding(paddingValues).padding(horizontal = 8.dp)) {
      val lazyColumnListState = rememberLazyListState()

      LlmModelSelectionDropdownMenu()

      Text(
        text = viewModel.statistics.value,
        textAlign = TextAlign.Center,
        modifier = Modifier.fillMaxWidth().wrapContentHeight().padding(top = 5.dp),
      )

      LazyColumn(
        modifier = Modifier.weight(9f),
        verticalArrangement = Arrangement.spacedBy(5.dp, alignment = Alignment.Bottom),
        state = lazyColumnListState,
      ) {
        composableScope.launch { lazyColumnListState.animateScrollToItem(viewModel.messages.size) }
        items(items = viewModel.messages) { message -> MessageView(messageData = message) }
        item {
          // place holder
        }
      }
      StandardDivider()
      SendMessageView(viewModel = viewModel)
    }
  }
}

@Composable
/** Displays a single message. */
fun MessageView(messageData: MessageData) {
  SelectionContainer {
    val fromModel: Boolean = messageData.owner == MessageOwner.Model
    val color =
      if (fromModel) {
        MaterialTheme.colorScheme.onSecondaryContainer
      } else {
        MaterialTheme.colorScheme.onPrimaryContainer
      }
    val backgroundColor =
      if (fromModel) {
        MaterialTheme.colorScheme.secondaryContainer
      } else {
        MaterialTheme.colorScheme.primaryContainer
      }
    val textAlign = if (fromModel) TextAlign.Left else TextAlign.Right
    val horizontalArrangement = if (fromModel) Arrangement.Start else Arrangement.End

    Row(horizontalArrangement = horizontalArrangement, modifier = Modifier.fillMaxWidth()) {
      Text(
        text = messageData.message,
        textAlign = textAlign,
        color = color,
        style = TextStyle(fontSize = 18.sp),
        modifier =
          Modifier.wrapContentWidth()
            .background(color = backgroundColor, shape = RoundedCornerShape(5.dp))
            .padding(3.dp)
            .widthIn(max = 300.dp),
      )
    }
  }
}

@ExperimentalMaterial3Api
@Composable
/** Displays a message sending box. */
fun SendMessageView(viewModel: ChatViewModel) {
  val localFocusManager = LocalFocusManager.current
  Row(
    horizontalArrangement = Arrangement.spacedBy(5.dp),
    verticalAlignment = Alignment.CenterVertically,
    modifier = Modifier.height(IntrinsicSize.Max).fillMaxWidth().padding(bottom = 5.dp),
  ) {
    var text by rememberSaveable { mutableStateOf("") }
    OutlinedTextField(
      value = text,
      textStyle = TextStyle(fontSize = 18.sp),
      onValueChange = { text = it },
      label = { Text(text = "Query:", style = TextStyle(fontSize = 18.sp)) },
      modifier = Modifier.weight(9f),
    )
    IconButton(
      onClick = {
        localFocusManager.clearFocus()
        viewModel.requestResponse(text)
        text = ""
      },
      modifier = Modifier.aspectRatio(1f).weight(1f),
      enabled = (text != ""),
    ) {
      Icon(imageVector = Icons.AutoMirrored.Filled.Send, contentDescription = "Commit message")
    }
  }
}