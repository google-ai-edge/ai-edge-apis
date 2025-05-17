package com.google.sample.fcdemo.viewmodel

import kotlinx.coroutines.flow.StateFlow

data class FormField(
    val name: String,
    val label: String,
    val fieldset: String,
    val stateFlow: StateFlow<Any?>,
)

fun List<FormField>.fetchValue(name: String): Any? {
    return first { it.name == name }.stateFlow.value
}

fun List<FormField>.fetchFlow(name: String): StateFlow<Any?> {
    return first { it.name == name }.stateFlow
}
