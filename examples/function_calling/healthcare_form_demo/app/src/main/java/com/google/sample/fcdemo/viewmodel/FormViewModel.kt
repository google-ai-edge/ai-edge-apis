package com.google.sample.fcdemo.viewmodel

import android.util.Log
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.google.ai.edge.localagents.core.proto.Content
import com.google.ai.edge.localagents.core.proto.Part
import com.google.ai.edge.localagents.fc.ChatSession
import com.google.ai.edge.localagents.fc.GenerativeModel
import com.google.ai.edge.localagents.fc.HammerFormatter
import com.google.ai.edge.localagents.fc.LlmInferenceBackend
import com.google.ai.edge.localagents.fc.ModelFormatterOptions
import com.google.mediapipe.tasks.genai.llminference.LlmInference
import com.google.mediapipe.tasks.genai.llminference.LlmInference.Backend
import com.google.mediapipe.tasks.genai.llminference.LlmInference.LlmInferenceOptions
import com.google.sample.fcdemo.FcDemoApp
import com.google.sample.fcdemo.functioncalling.Tools
import com.google.sample.fcdemo.navigation.Destination
import com.google.sample.fcdemo.utilities.TAG
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.SharedFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asSharedFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import org.json.JSONException

const val TAG = "FormViewModel"

class FormViewModel : ViewModel() {

    private lateinit var chatSession: ChatSession
    val generativeModel by lazy {createGenerativeModel()}

    // Observable state to indicate that the initial hint prompt has been shown
    private val _hasShownPrompt = MutableStateFlow(false)
    val hasShownPrompt: StateFlow<Boolean> = _hasShownPrompt.asStateFlow()

    // Observable state to indicate that at least one field on a screen has been updated
    private val _hasRunOnce = MutableStateFlow(false)
    val hasRunOnce: StateFlow<Boolean> = _hasRunOnce.asStateFlow()

    // Observable state to indicate that all fields have been updated
    private val _isCompleteAndValid = MutableStateFlow(false)
    val isCompleteAndValid: StateFlow<Boolean> = _isCompleteAndValid.asStateFlow()

    // Observable state to request the UI to display a saving indicator
    private val _isSaving = MutableStateFlow(false)
    val isSaving: StateFlow<Boolean> = _isSaving.asStateFlow()

    // Observable state to request the UI to display a snackbar with an error message
    private val _errorEvent = MutableSharedFlow<String>()
    val errorEvent: SharedFlow<String> = _errorEvent.asSharedFlow()

    // Observable state to indicate that the model is running
    private val _isProcessing = MutableStateFlow(false)
    val isProcessing: StateFlow<Boolean> = _isProcessing.asStateFlow()

    private val _recognizedSpeech = MutableStateFlow<String>("")
    val recognizedSpeech: SharedFlow<String> = _recognizedSpeech.asSharedFlow()

    /**
     * Form field data
     */
    private val _firstName = MutableStateFlow("")
    private val _lastName = MutableStateFlow("")
    private val _dob = MutableStateFlow("")
    private val _occupation = MutableStateFlow("")
    private val _sex = MutableStateFlow<String?>(null)
    private val _maritalStatus = MutableStateFlow<String?>(null)
    private val _medicalConditionsMap = MutableStateFlow<Map<String, Boolean>>(
        Tools.medicalConditionsOptions.associateWith { false }
    )

    val formData = listOf(
        FormField("firstName", "First Name", "fieldset1", _firstName.asStateFlow()),
        FormField("lastName", "Last Name", "fieldset1", _lastName.asStateFlow()),
        FormField("dob", "Date of Birth", "fieldset1", _dob.asStateFlow()),
        FormField("occupation", "Occupation", "fieldset1", _occupation.asStateFlow()),
        FormField("sex", "Sex", "fieldset2", _sex.asStateFlow()),
        FormField("maritalStatus", "Marital Status", "fieldset2", _maritalStatus.asStateFlow()),
        FormField(
            "medicalConditions", "Medical Conditions", "fieldset3",
            _medicalConditionsMap.asStateFlow()
        ),
    )

    fun updateFirstName(value: String) {
        _firstName.value = value
    }

    fun updateLastName(value: String) {
        _lastName.value = value
    }

    fun updateDob(value: String) {
        _dob.value = value
    }

    fun updateOccupation(value: String) {
        _occupation.value = value
    }

    fun updateRecognizedSpeech(value: String) {
        _recognizedSpeech.value = value
    }

    fun updateSex(value: String?) {
        _sex.value = value
    }

    fun updateMaritalStatus(value: String?) {
        _maritalStatus.value = value
    }

    fun updateMedicalCondition(condition: String, isSelected: Boolean) {
        val updatedConditions = _medicalConditionsMap.value.toMutableMap()
        updatedConditions[condition] = isSelected
        _medicalConditionsMap.value = updatedConditions
    }

    fun setHasShownPrompt() {
        _hasShownPrompt.value = true
    }

    fun processVoiceInput(spokenText: String, destination: Destination) {
        viewModelScope.launch(Dispatchers.IO) {
            Log.d(TAG, "START PROCESSING")

            _isProcessing.value = true
            Log.i(TAG, "Model processing started")
            try {
                val response = chatSession.sendMessage(spokenText)
                Log.d(TAG, "Hammer Response: $response") // Log response

                response.getCandidates(0).content.partsList?.let {
                    parseResponse(it)
                } ?: run {
                    Log.e(TAG, "Hammer response was null")
                    _errorEvent.emit("GenerativeAI error: AI could not process the request.")
                }
            } catch (e: Exception) {
                Log.e(TAG, "Hammer Error: ${e.message}", e)
                val errorMessage = if (e is IndexOutOfBoundsException) {
                    "The model returned no response to \"$spokenText\"."
                } else {
                    e.localizedMessage
                }
                _errorEvent.emit("GenerativeAI error: $errorMessage")
            } finally {
                Log.i(TAG, "Model processing ended")
            }
        }
    }

    fun onVoiceRecognitionError(errorMessage: String) {
        viewModelScope.launch {
            _errorEvent.emit("Speech recognition error: $errorMessage")
        }
    }

    fun onNotificationMessage(notification: String) {
        viewModelScope.launch {
            _errorEvent.emit(notification)
        }
    }

    private fun parseResponse(parts: List<Part?>) {
        try {
            // extract the function from all the parts in the response
            parts.forEach { part ->
                part?.functionCall?.args?.fieldsMap?.forEach { (key, value) ->
                    value.stringValue?.let { stringValue ->
                        if (stringValue != "<unknown>") {
                            when (key) {
                                "first_name" -> _firstName.value = value.stringValue
                                "last_name" -> _lastName.value = value.stringValue
                                "occupation" -> _occupation.value = value.stringValue
                                "sex" -> _sex.value = value.stringValue
                                "marital_status" -> _maritalStatus.value = value.stringValue
                                "date_of_birth" -> _dob.value = value.stringValue
                                "conditions" -> {
                                    val currentMap = _medicalConditionsMap.value.toMutableMap()
                                    value.listValue.valuesList.forEach { condition ->
                                        currentMap[condition.stringValue] = true
                                    }
                                    _medicalConditionsMap.value = currentMap
                                }

                                else -> {
                                    throw Exception("Unknown function: $key value: $value")
                                }
                            }
                        }
                    }
                }
            }
            _hasRunOnce.value = true
        } catch (e: JSONException) {
            Log.e(TAG, "JSON Parsing Error: ${e.message}")
            viewModelScope.launch { _errorEvent.emit("GenerativeAI error: unexpected AI response format.") }
        } finally {
            Log.d(TAG, "STOP PROCESSING")
            _isProcessing.value = false
        }
    }

    fun parseConditionString(inputString: String): List<String> {
        val conditions = inputString.trim('{', '}')
            .split(',')
            .map { it.trim() }
            .filter {
                val parts = it.split('=')
                parts.size == 2 && parts[1].trim().lowercase() == "true"
            }
            .map {
                it.split('=')[0].trim()
            }

        return if (conditions.isEmpty()) {
            listOf("None selected")
        } else {
            conditions.mapIndexed { index, condition ->
                if (index < conditions.lastIndex) {
                    "$condition,"
                } else {
                    condition
                }
            }
        }
    }

    fun submitForm() {
        _isSaving.value = true
        viewModelScope.launch {
            // Simulate submission
            kotlinx.coroutines.delay(2500)
            Log.i(TAG, "Form Submitted:")
            Log.i(
                TAG,
                "Name: ${formData.fetchValue("firstName")} ${formData.fetchValue("lastName")}"
            )
            Log.i(TAG, "DOB: ${formData.fetchValue("dob")}")
            Log.i(TAG, "Occupation: ${formData.fetchValue("occupation")}")
            Log.i(TAG, "Sex: ${formData.fetchValue("sex")}")
            Log.i(TAG, "Marital Status: ${formData.fetchValue("maritalStatus")}")
            Log.i(
                TAG, "Medical Conditions: " +
                        "${
                            parseConditionString(
                                formData.fetchValue("medicalConditions").toString()
                            )
                        }"
            )

            _isCompleteAndValid.value = formData.fetchValue("firstName") != "" &&
                    formData.fetchValue("lastName") != "" &&
                    formData.fetchValue("dob") != "" &&
                    formData.fetchValue("sex") != null &&
                    formData.fetchValue("maritalStatus") != null

            if (!_isCompleteAndValid.value) {
                val errorField = when {
                    formData.fetchValue("firstName") == "" -> "First Name"
                    formData.fetchValue("lastName") == "" -> "Last Name"
                    formData.fetchValue("dob") == "" -> "Date of Birth"
                    formData.fetchValue("sex") == null -> "Sex"
                    formData.fetchValue("maritalStatus") == null -> "Marital Status"
                    else -> ""
                }
                _errorEvent.emit("Please enter a response for: $errorField")
            }
            _isSaving.value = false
            // The state model needs improving but this is a quick fix
            // set to false so the home screen knows that data entry is complete
            _hasRunOnce.value = false
        }
    }

    fun resetForm() {
        _lastName.value = ""
        _firstName.value = ""
        _dob.value = ""
        _occupation.value = ""
        _sex.value = null
        _maritalStatus.value = null
        _medicalConditionsMap.value = Tools.medicalConditionsOptions.associateWith { false }

        _hasRunOnce.value = false
        _hasShownPrompt.value = false
        _isCompleteAndValid.value = false
        _isSaving.value = false
        chatSession = generativeModel.startChat()
    }

    private fun createGenerativeModel(): GenerativeModel {
        val formatter =
            HammerFormatter(ModelFormatterOptions.builder().setAddPromptTemplate(true).build())

        val llmInferenceOptions = LlmInferenceOptions.builder()
            .setModelPath("/data/local/tmp/hammer2.1_1.5b_q8_ekv4096.task")
            .setMaxTokens(2048)
            .apply { setPreferredBackend(Backend.GPU) }
            .build()

        val llmInference =
            LlmInference.createFromOptions(FcDemoApp.appContext, llmInferenceOptions)
        val llmInferenceBackend =
            LlmInferenceBackend(llmInference, formatter)

        val systemInstruction = Content.newBuilder()
            .setRole("system")
            .addParts(
                Part.newBuilder()
                    .setText("This assistant will help you fill out a medical form.")
            )
            .build()

        val model = GenerativeModel(
            llmInferenceBackend,
            systemInstruction,
            listOf(Tools.medicalFormTools).toMutableList()
        )
        chatSession = model.startChat()
        return model
    }
}