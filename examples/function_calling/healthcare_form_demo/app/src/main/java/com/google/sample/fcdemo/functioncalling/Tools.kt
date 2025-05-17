package com.google.sample.fcdemo.functioncalling

import com.google.ai.edge.localagents.core.proto.FunctionDeclaration
import com.google.ai.edge.localagents.core.proto.Schema
import com.google.ai.edge.localagents.core.proto.Tool
import com.google.ai.edge.localagents.core.proto.Type.STRING
import com.google.ai.edge.localagents.core.proto.Type.OBJECT
import com.google.ai.edge.localagents.core.proto.Type.ARRAY

/** Tools for the generative AI demo app. */
object Tools {
    val sexOptions =
        listOf(
            "Female",
            "Male"
        )
    val maritalStatusOptions =
        listOf(
            "Single",
            "Married",
            "Divorced",
            "Widowed",
            "Separated",
            "Domestic Partnership"
        )
    val medicalConditionsOptions =
        listOf(
            "Hypertension",
            "Diabetes",
            "Asthma",
            "Arthritis",
            "Migraine",
            "Depression",
            "Kidney Disease",
            "Anxiety",
            "Allergies",
            "Heart Disease",
        )

    val medicalFormTools: Tool =
        Tool.newBuilder()
            .addFunctionDeclarations(
                FunctionDeclaration.newBuilder()
                    .setName("provide_name")
                    .setDescription("Records the user's first and last name.")
                    .setParameters(
                        Schema.newBuilder()
                            .setType(OBJECT)
                            .putProperties(
                                "first_name",
                                Schema.newBuilder()
                                    .setType(STRING)
                                    .setDescription("The user's first name.")
                                    .build(),
                            )
                            .putProperties(
                                "last_name",
                                Schema.newBuilder()
                                    .setType(STRING)
                                    .setDescription("The user's last name.")
                                    .build(),
                            )
                            .build()
                    )
            )
            .addFunctionDeclarations(
                FunctionDeclaration.newBuilder()
                    .setName("provide_dob")
                    .setDescription("Records the user's date of birth.")
                    .setParameters(
                        Schema.newBuilder()
                            .setType(OBJECT)
                            .putProperties(
                                "date_of_birth",
                                Schema.newBuilder()
                                    .setType(STRING)
                                    .setDescription("The user's date of birth in MM/DD/YYYY format.")
                                    .build(),
                            )
                            .build()
                    )
            )
            .addFunctionDeclarations(
                FunctionDeclaration.newBuilder()
                    .setName("provide_demographics")
                    .setDescription("Records the user's sex and marital status.")
                    .setParameters(
                        Schema.newBuilder()
                            .setType(OBJECT)
                            .putProperties(
                                "sex",
                                Schema.newBuilder()
                                    .setType(STRING)
                                    .setFormat("enum")
                                    .setDescription("The user's sex. The possible choices are: [${sexOptions.joinToString()}]")
                                    .addEnum("male")
                                    .addEnum("female")
                                    .build(),
                            )
                            .putProperties(
                                "marital_status",
                                Schema.newBuilder()
                                    .setType(STRING)
                                    .setFormat("enum")
                                    .setDescription(
                                        "The user's marital status. The possible choices are : [${maritalStatusOptions.joinToString()}]"
                                    )
                                    .addEnum("single")
                                    .addEnum("married")
                                    .addEnum("divorced")
                                    .addEnum("widowed")
                                    .addEnum("separated")
                                    .addEnum("domestic partnership")
                                    .build(),
                            )
                            .build()
                    )
            )
            .addFunctionDeclarations(
                FunctionDeclaration.newBuilder()
                    .setName("provide_occupation")
                    .setDescription("Records the user's occupation or job.")
                    .setParameters(
                        Schema.newBuilder()
                            .setType(OBJECT)
                            .putProperties(
                                "occupation",
                                Schema.newBuilder()
                                    .setType(STRING)
                                    .setDescription("The user's occupation or job.")
                                    .build(),
                            )
                            .addRequired("occupation")
                            .build()
                    )
            )
            .addFunctionDeclarations(
                FunctionDeclaration.newBuilder()
                    .setName("update_medical_history")
                    .setDescription(
                        "Updates the user's medical history based on the conditions provided. This adds to any previously mentioned conditions."
                    )
                    .setParameters(
                        Schema.newBuilder()
                            .setType(OBJECT)
                            .putProperties(
                                "conditions",
                                Schema.newBuilder()
                                    .setType(ARRAY)
                                    .setDescription(
                                        "A list of medical conditions the user has or has had. The choices are: [${medicalConditionsOptions.joinToString()}]"
                                    )
                                    .setItems(Schema.newBuilder().setType(STRING).build())
                                    .build(),
                            )
                            .addRequired("conditions")
                            .build()
                    )
            )
            .build()
}