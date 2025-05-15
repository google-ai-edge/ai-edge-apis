# Tool Simulation Library

## Overview

The `tool-simulation` library lets you evaluate and specialize LLMs on a
specific set of tools. The library is designed to be modular, allowing users to
plug in different model backends, prompt formats, and tool simulation logic.

## Set Up

The tool simulation library is available as a Python package. You can install
the library using pip:

```bash
pip install . #[TODO -- name of the package]
```

Or, if installing directly from the source directory:

```bash
pip install -e .
```

For development, including test dependencies:

```bash
pip install -e ".[test]"
```

## Tool Simulation

This library facilitates simulating LLM interactions within tool environments,
offering several benefits:

1.  **Data Generation:** Automatically create structured datasets
    (conversational logs) demonstrating tool interactions.
2.  **Model Evaluation:** Evaluate the performance of LLMs in realistic
    tool-use. By running a model against the simulated environment, you can
    assess its ability to correctly identify the need for a tool, formulate
    structured calls, and handle responses without needing live backends.
3.  **Experimentation:** Quickly iterate on different prompting strategies, tool
    definitions, or orchestration techniques.

## Core Concepts

1.  **Prompt Builders (`BasePromptBuilder`)**: Represent the conversation state
    for a specific format (e.g., Gemma, Llama). The underlying abstraction is a
    list of turns which themselves are list of content chunks.
2.  **Model Instance (`ModelInstance`)**: A protocol defining the interface for
    interacting with an LLM backend. Implementations handle the actual querying
    of the model.
3.  **Tool Representation (`tool_types`, `proto2tool`, `tool2str`)**: Tools are
    defined using standard `google.ai.generativelanguage` protos (`glm.Tool`),
    however we maintain an internal representation (see `tool_types`,
    `proto2tool`) for greater flexibility. A text representation of the tools
    can be generated with `tool2str`.
4.  **Function Calls (`str2call`)**: Provides parsing functionality to convert
    string representations of function calls (e.g.,
    `my_func(arg1="value",arg2=123))` into structured `FunctionCall` objects).
5.  **Synthetic Sessions (`SyntheticSession`)**: A protocol for simulating the
    backend execution of a tool/API call during data generation. Implementations
    return synthetic results based on the function call received.

## Tool Simulation Flow

The Tool Simulation process is illustrated in the diagram below. The workflow
below enables generating conversational data involving tool usage, evaluating
language models on tool interaction, or experimenting with tool integration
strategies..

The workflow starts with an **API Definition** (the schema of the tools the
model can use) and seed **Queries** (example user requests). These are fed into
a **Synthetic Generation** stage, which generate or augment existing data. For
best results we recommend having a well-thought-out set of seed queries. This
initial context seeds the core **Conversation Simulation** loop. Here, the
primary model (**Tool Use Model**) interacts in a multi-turn conversation:

1.  It might converse with a **Replier Model** model (simulating a user or
    another conversational agent, which can be scripted or behave dynamically).
2.  When the `Tool Use Model` model decides to use a tool based on the
    conversation, it formulates a call to the **API Environment**.
3.  The `API Environment` handles the tool's execution, providing realistic
    responses, including potential errors or specific data, based on the API
    definition and simulation logic. This can be either an LLM call or a
    realistic/mock backend for your tool.
4.  The `Tool Use Model` receives this simulated response and continues the
    conversation with the `Replier Model`.

Note that while we use `Model` this is technically a state stored in a
`PromptBuilder` object and therefore is separate from an actual model.

The entire interaction log from this simulation loop, containing user messages,
model replies, tool calls, and simulated tool results, is then passed through a
**Filtering** stage (for quality control or formatting) to produce the final
output: structured **Conversation Tapes**. This dataset can then be used for
model evaluation, fine-tuning, or further analysis.

```mermaid
graph TD
    %% Default Node Styles (applied via classDef or individual styling)
    %% Mermaid doesn't have global node defaults like DOT in the same way,
    %% so we'll define classes or style individually.

    %% Node Definitions
    APIDef["API Definition"]
    Queries["Queries"]
    SynthGen["Synthetic Generation"]

    subgraph SimulationLoop ["Simulation Loop"]
        ReplierModel["Replier Model"]
        ToolUseModel["Tool Use Model"]
        APIEnv["API Environment"]
    end

    Filtering["Filtering"]
    ConvTapes["Conversation Tapes"]

    %% Annotations - these will be regular nodes styled to look like text
    AnnotSynthGen["Can augment dataset<br>and generate<br>adversarial or<br>incomplete samples"]
    AnnotReplier["Can be instructed to be<br>collaborative, reserved, etc.<br>Can also be used to execute<br>a predefined script"]
    AnnotAPIEnv["Synthetic function replies generated<br>on-the-fly (or predefined for<br>evaluation), Can be used to simulate<br>errors/failure states"]

    %% Edges
    APIDef --> SynthGen
    Queries --> SynthGen
    SynthGen --> ToolUseModel

    %% Edges within the simulation loop
    ReplierModel --> ToolUseModel
    ToolUseModel --> ReplierModel
    ToolUseModel --> APIEnv
    APIEnv --> ToolUseModel

    %% Edges exiting the simulation loop
    ToolUseModel --> Filtering
    Filtering --> ConvTapes

    %% Edges for Annotations (using dotted lines)
    SynthGen -.-> AnnotSynthGen
    ReplierModel -.-> AnnotReplier
    APIEnv -.-> AnnotAPIEnv

    %% Styling
    %% Node specific styles
    style APIDef fill:#fef9e7,stroke:#f0ad4e,color:#333
    style Queries fill:#e8f8f5,stroke:#5dade2,color:#333
    style SynthGen fill:#f2f3f4,stroke:#839192,color:#333,stroke-dasharray: 5 5 %% Dashed border

    %% Styles for nodes within the subgraph (Mermaid doesn't directly inherit from subgraph like DOT for fill)
    style ReplierModel fill:#ffefd5,stroke:#ffbf00,color:#333
    style ToolUseModel fill:#ffefd5,stroke:#ffbf00,color:#333
    style APIEnv fill:#efebf5,stroke:#a569bd,color:#333

    %% Nodes after simulation loop
    style Filtering fill:#fdedec,stroke:#e74c3c,color:#333
    style ConvTapes fill:#e0f2f7,stroke:#4dd0e1,color:#333

    %% Annotation node styles (to make them look like plain text)
    style AnnotSynthGen fill:transparent,stroke:transparent,color:#555555,font-style:italic
    style AnnotReplier fill:transparent,stroke:transparent,color:#555555,font-style:italic
    style AnnotAPIEnv fill:transparent,stroke:transparent,color:#555555,font-style:italic

    %% Subgraph style (border color)
    %% Note: Mermaid subgraph styling is somewhat limited compared to DOT clusters.
    %% The title "Simulation Loop" is added for clarity, as an empty title can look odd.
    %% If you want the border to be black:
    classDef subgraphStyle stroke:black,stroke-width:2px
    class SimulationLoop subgraphStyle
```

## Structure

The library is organized into two main directories:

1.  **`tool_simulation/core`**: This contains our core library:

    *   Abstract base classes for prompts and turns (`base_prompt_builder.py`).
    *   Specific prompt builder implementations for different model formats
        (e.g., `gemma_prompt_builder.py`, `llama_prompt_builder.py`).
    *   The `ModelInstance` protocol for adding custom LLM backends
        (`model_instance.py`, `aistudio_backend.py`).
    *   Data structures and utilities for representing and handling tool schemas
        (`tool_types.py`, `proto2tool.py`, `tool2str.py`).
    *   Function call parsing logic (`str2call.py`).
    *   Testing utilities (`testing_utils.py`).

2.  **`tool_simulation/stages`**: This directory builds upon the `core`
    components to provide higher-level functionalities and pipeline components
    for common tasks:

    *   **Data Generation (`stages/data_generation`)**: Includes tools for
        generating initial seed data (`seed_data.py`).
    *   **Function Calling Simulation (`stages/function_calling`)**: Simulates
        multi-turn conversations involving tool use. This includes managing the
        interaction between the main LLM, a potential replier LLM, and simulated
        tool backends (`function_calling_episode.py`,
        `datagen_prompt_builder.py`, `replier_prompt_builder.py`, `session.py`).
    *   **Validation (`stages/validation`)**: Provides tools to validate
        generated function calls against schemas (`validate_function_call.py`)
        and to validate the overall coherence and correctness of generated
        conversations using a separate validation model (`validate_data.py`,
        `validation_prompt_builder.py`).
    *   **Exports (`stages/exports`)**: Contains utilities to export the
        generated conversation data into formats suitable for model training,
        such as TF Examples (`export_tf_example.py`).
    *   **Utilities (`stages/utils`)**: General helper functions used across
        stages, like text formatting (`margin.py`).

3.  **`tool_simulation/pipelines`**: This contains pipelines you can run:

    *   **Base Pipeline***: `base_pipeline` is a simple pipeline to showcase how
        different stages fit together.

## API Examples

### 1. Prompt Builders

Prompt builders construct the conversation history in the format expected by a
specific model.

**Example (`GemmaPromptBuilder`)**:

~~~python
from tool_simulation.core import gemma_prompt_builder
from tool_simulation.core.base_prompt_builder import ChunkKind

# Instantiate the builder
builder = gemma_prompt_builder.GemmaPromptBuilder()

# Add a user turn
builder.user_turn("What is the weather in London?")

# Add a model turn with a tool call
builder.model_turn("get_weather(location='London')", kind=ChunkKind.TOOL_CALL)

# Add a tool result turn (using user role for Gemma format)
builder.user_turn('{"temperature": "15C", "condition": "Cloudy"}', kind=ChunkKind.TOOL_RESULT)

# Get the full prompt string
prompt_string = builder.get_prompt()
print("--- Full Prompt ---")
print(prompt_string)

# Get the prompt string formatted for inference (appends start of model turn)
inference_prompt_string = builder.get_prompt(inference=True)
print("\n--- Inference Prompt ---")
print(inference_prompt_string)

# Expected Output:
# --- Full Prompt ---
# <start_of_turn>user
# What is the weather in London?<end_of_turn><start_of_turn>model
# ```tool_code
# get_weather(location='London')
# ```<end_of_turn><start_of_turn>user
# ```tool_outputs
# {"temperature": "15C", "condition": "Cloudy"}
# ```<end_of_turn>

# --- Inference Prompt ---
# <start_of_turn>user
# What is the weather in London?<end_of_turn><start_of_turn>model
# ```tool_code
# get_weather(location='London')
# ```<end_of_turn><start_of_turn>user
# ```tool_outputs
# {"temperature": "15C", "condition": "Cloudy"}
# ```<end_of_turn><start_of_turn>model
#
~~~

*(Similar examples apply to `LlamaPromptBuilder` with its specific formatting.)*

### 2. Model Interaction (`AIStudioModel`)

The `ModelInstance` protocol allows interacting with different LLMs.
`GeminiModel` is an implementation using the Google Generative AI SDK.

**Example**:

```python
from google.genai import types
from tool_simulation.core.aistudio_backend import AIStudioModel

api_key = "my_api_key"

tool = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="get_weather",
            description="Call this to obtain weather for a given location.",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "location": types.Schema(type=types.Type.STRING)
                },
                required=["location"]
            )
        )
    ]
)

# Instantiate the model
model = AIStudioModel(api_key=api_key, model_name='gemini-1.5-flash', tools=tool)

# Query the model
prompt = "What's the weather like in Tokyo?"
response = model.query_model(prompt)

print(f"Prompt: {prompt}")
print(f"Response: {response}")

# Example with function call expected:
prompt_fc = "Use the weather tool for Paris."
response_fc = model.query_model(prompt_fc)
print(f"\nPrompt: {prompt_fc}")
print(f"Response: {response_fc}")

# Example Output:
# Prompt: What's the weather like in Tokyo?
# Response: {"args": {"location": "Tokyo"}, "name": "get_weather"}

# Prompt: Use the weather tool for Paris.
# Response: {"args": {"location": "Paris"}, "name": "get_weather"}
```

### 3. Tool Schema Handling (`proto2tool`, `tool2str`)

Convert `glm.Tool` protobufs to internal representations or string formats.

**Example**:

```python
from google.genai import types
from tool_simulation.core import proto2tool, tool2str

weather_tool_proto = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="get_weather",
            description="Fetches weather data",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "location": types.Schema(type=types.Type.STRING, description="City name"),
                    "unit": types.Schema(type=types.Type.STRING, description="Temperature unit (C or F)")
                },
                required=["location"]
            )
        )
    ]
)

# 1. Convert proto to internal ToolDefinition
tool_definition = proto2tool.proto2tool(weather_tool_proto, tool_name="WeatherAPI")

print("--- Tool Definition ---")
print(tool_definition)
# Expected: ToolDefinition(name='WeatherAPI', functions={'get_weather': FunctionDefinition(...)})

# Access definition details
func_def = tool_definition.functions["get_weather"]
print(f"Function Name: {func_def.name}")
print(f"Location Arg Required: {func_def.args['location'].required}") # True
print(f"Unit Arg Required: {func_def.args['unit'].required}")       # False
print(f"Location Arg Type: {func_def.args['location'].dtype}")      # String()

# 2. Convert proto to JSON string representation
tool_json_string = tool2str.tool2str(weather_tool_proto)
print("\n--- Tool JSON String ---")
print(tool_json_string)
# --- Tool JSON String ---
# [
#   {
#     "description": "Fetches weather data",
#     "name": "get_weather",
#     "parameters": {
#       "properties": {
#         "location": {
#           "description": "City name",
#           "type": "STRING"
#         },
#         "unit": {
#           "description": "Temperature unit (C or F)",
#           "type": "STRING"
#         }
#       },
#       "required": [
#         "location"
#       ],
#       "type": "OBJECT"
#     }
#   }
# ]
```

### 4. Function Call Parsing (`str2call`)

Parse string representations of function calls into structured `FunctionCall`
objects.

**Example**:

```python
from tool_simulation.core import str2call

expression = "search_flights(origin='London', destination='Paris', passengers=2, options={'direct': True, 'class': 'economy'})"

try:
    parsed_call = str2call.parse_function_call_expression(expression)

    print(f"Function Name: {parsed_call.name}")
    print("\nArguments:")
    for name, arg in parsed_call.args.items():
        print(f"  - {name}:")
        print(f"    Value Container: {arg.value}")
        print(f"    Detected Type: {arg.dtype}")

    # Access specific argument details
    options_arg = parsed_call.args['options']
    print(f"\nOptions Type: {options_arg.dtype}")
    # Expected: Object(typename='dict', fields={'direct': Bool(), 'class': String()})

    # Reconstruct string (requires AST)
    print(f"\nReconstructed: {str(parsed_call)}")


except ValueError as e:
    print(f"Error parsing expression: {e}")

# Function Name: search_flights

# Arguments:
#   - origin:
#     Value Container: Container(typename='constant', fields='London')
#     Detected Type: String(typename='str')
#   - destination:
#     Value Container: Container(typename='constant', fields='Paris')
#     Detected Type: String(typename='str')
#   - passengers:
#     Value Container: Container(typename='constant', fields=2)
#     Detected Type: Int(typename='int')
#   - options:
#     Value Container: Container(typename='dict', fields={'direct': Container(typename='constant', fields=True), 'class': Container(typename='constant', fields='economy')})
#     Detected Type: Dict(typename='dict', inner_key_type=String(typename='str'), inner_value_type=Bool(typename='bool'))

# Options Type: Dict(typename='dict', inner_key_type=String(typename='str'), inner_value_type=Bool(typename='bool'))

# Reconstructed: search_flights(origin='London', destination='Paris', passengers=2, options={'direct': True, 'class': 'economy'})
```

### 5. Function Call Validation (`validate_function_call`)

Validate a parsed `FunctionCall` against its corresponding `glm.Tool` schema
definition.

**Example**:

```python
from google.genai import types
from tool_simulation.core import str2call
from tool_simulation.stages.validation import validate_function_call

# Tool Schema
tool_schema = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="search",
            description="Search items",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "query": types.Schema(type=types.Type.STRING),
                    "max_results": types.Schema(type=types.Type.INTEGER)
                },
                required=["query"]
            )
        )
    ]
)

# Function Calls (as strings)
valid_call_str = "search(query='example search', max_results=10)"
valid_call_optional_missing_str = "search(query='another search')"
invalid_call_missing_required_str = "search(max_results=5)"
invalid_call_wrong_type_str = "search(query='test', max_results='five')"
invalid_call_extra_arg_str = "search(query='stuff', filter='none')"

# Parse calls
valid_call = str2call.parse_function_call_expression(valid_call_str)
valid_call_optional_missing = str2call.parse_function_call_expression(valid_call_optional_missing_str)
invalid_call_missing_required = str2call.parse_function_call_expression(invalid_call_missing_required_str)
invalid_call_wrong_type = str2call.parse_function_call_expression(invalid_call_wrong_type_str)
invalid_call_extra_arg = str2call.parse_function_call_expression(invalid_call_extra_arg_str)

# Validate
print(f"'{valid_call_str}' is valid: {validate_function_call.validate_function_call(valid_call, tool_schema)}")
print(f"'{valid_call_optional_missing_str}' is valid: {validate_function_call.validate_function_call(valid_call_optional_missing, tool_schema)}")
print(f"'{invalid_call_missing_required_str}' is valid: {validate_function_call.validate_function_call(invalid_call_missing_required, tool_schema)}")
print(f"'{invalid_call_wrong_type_str}' is valid: {validate_function_call.validate_function_call(invalid_call_wrong_type, tool_schema)}")
print(f"'{invalid_call_extra_arg_str}' is valid: {validate_function_call.validate_function_call(invalid_call_extra_arg, tool_schema)}")

# Expected Output:
# 'search(query='example search', max_results=10)' is valid: True
# 'search(query='another search')' is valid: True
# 'search(max_results=5)' is valid: False
# 'search(query='test', max_results='five')' is valid: False
# 'search(query='stuff', filter='none')' is valid: False
```

## Tutorial: Generating Synthetic Tool Use Data

This tutorial walks you through manually using the `tool-simulation` library
components to generate conversational data for an API. We'll cover defining the
API, simulating its behavior, generating initial queries, running conversation
simulations, and validating the results.

## Goal

In the example below we will simulate conversations where a user interacts with
an agent that manages user accounts. We will look at generating different tasks
for he agent and executing them against an environment. For this tutorial we
will follow a simple function calling format where the tools are presented as
JSON and the model returns function calls formatted as python functions.

***NOTE:*** The `tool_simulation` library comes with base pipelines already
defined. This tutorial is an in-depth walkthrough through some of the main
components. After completing **Step 4** below, you can instead refer to
`tool_simulation/pipelines`

## Step 1: Define Your API Schema

First, define the structure of all the functions your API exposes using
`google.genai.Tool` and `google.genai.FunctionDeclaration`. This schema
should list the tools we want to run the simulation against. When prompting the
model, the schema will be lowered to a string representation.

```python
from google.genai import types

my_api = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="get_user_profile",
            description="Retrieves the profile information (name, email, status) for a given user ID.",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "user_id": types.Schema(
                        type=types.Type.STRING,
                        description="The unique identifier for the user (e.g., 'user123')."
                    )
                },
                required=["user_id"]
            )
        ),
        types.FunctionDeclaration(
            name="update_user_status",
            description="Sets a new status for a given user ID.",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "user_id": types.Schema(
                        type=types.Type.STRING,
                        description="The unique identifier for the user."
                    ),
                    "new_status": types.Schema(
                        type=types.Type.STRING,
                        description="The new status to set (e.g., 'active', 'inactive', 'away')."
                    )
                },
                required=["user_id", "new_status"]
            )
        ),
    ]
)
```

We can display this as a JSON string using `tool2str`.

```python
import tool_simulation.core.tool2str as tool2str
print(tool2str.tool2str(tool=my_api))
```

## Step 2: Define Your Parser Function

The tool simulator needs a way to convert the function calls emitted by
the model to a structured form. To do this conversion, we define a simple parser
function.
For this example we assume the model outputs either a function call:
\`\`\`tool_code\nf(...)\n\`\`\`, or plain text.

~~~python
from tool_simulation.core import str2call
from tool_simulation.stages.function_calling import datagen_prompt_builder
from tool_simulation.stages.validation import validate_function_call


def parse_output(text: str) -> datagen_prompt_builder.ParseResult:
  """Parses the output of a language model and returns a ParseResult.

  Args:
    text: The text to parse.

  Returns:
    A ParseResult object.
  """
  if not text:
    return datagen_prompt_builder.ParseResult(function_call=None, forward=None)
  if text.startswith("```tool_code\n") and text.endswith("\n```"):
    try:
      parsed_function_call = str2call.parse_function_call_expression(
          text.replace("```", "").replace("tool_code", "").strip()
      )
      is_valid = validate_function_call.validate_function_call(
          function_call=parsed_function_call, tool=my_api
      )
    except ValueError:
      is_valid = False
      parsed_function_call = None
    return datagen_prompt_builder.ParseResult(
        function_call=None if not is_valid else parsed_function_call,
        forward=None,
    )
  else:
    return datagen_prompt_builder.ParseResult(function_call=None, forward=text)
~~~

In the function above we parse the text and return the result as a
`ParseResult`, which is an utility class that contains a function call and
forward text. It is used to support different kinds of model behaviors (function
calls only, function call or text, or function call combined text). When both
fields are set to `None` the simulator interprets this as an error state.

In addition, we are also using `validate_function_call` to make sure the
function call is valid with respect to the given schema. When testing the parser
we get:

~~~python
print(parse_output("```tool_code\nget_user_profile(user_id=\"my_username\")\n```").function_call)
# get_user_profile(user_id='my_username')
print(parse_output("```tool_code\nget_user_profile(user_id=123)\n```").function_call)
# None -- in this case the types don't match
print(parse_output("Hello World").forward)
# Hello World
~~~

## Step 3: Define API Backend

In this step we define a mock backend for our API. The purpose is to provide
replies to the function calling model. While we are using a relatively simple
backend for this example, this can easily be extended to provide greater data
diversity.

```python
import copy
from tool_simulation.core.str2call import FunctionCall
from tool_simulation.stages.function_calling.session import SyntheticSession, FunctionReply


class SimplifiedAPISimulator(SyntheticSession):
  """Simulates responses for the User Profile and Status API."""

  _user_data = {
      "alice_1": {
          "name": "Alice",
          "email": "alice@example.com",
          "status": "active",
      },
      "bob_1": {
          "name": "Bob",
          "email": "bob@example.com",
          "status": "inactive",
      },
  }

  def reply(self, function_call: FunctionCall) -> FunctionReply:
    """Generates a synthetic response, assuming valid input."""

    if function_call.name == "get_user_profile":
      user_id = function_call.args["user_id"].value.fields
      profile_data = copy.deepcopy(self._user_data.get(user_id, {}))
      return FunctionReply(reply={"retrieved_user_profiles": [profile_data]})
    elif function_call.name == "update_user_status":
      user_id = function_call.args["user_id"].value.fields
      new_status = function_call.args["new_status"].value.fields
      if user_id not in self._user_data:
        return FunctionReply(reply={"status": "User ID not found"})
      self._user_data[user_id]["status"] = new_status
      return FunctionReply(reply={"user_id": user_id, "new_status": new_status})
    else:
      return FunctionReply(
          reply={"error": f"Function {function_call.name} not found."}
      )
```

We can test the environment:

~~~python
simulator = SimplifiedAPISimulator()
print(simulator.reply(parse_output("```tool_code\nget_user_profile(user_id=\"bob_1\")\n```").function_call))
# {"retrieved_user_profiles": [{"name": "Bob", "email": "bob@example.com", "status": "inactive"}]}
print(simulator.reply(parse_output("```tool_code\nget_user_profile(user_id=\"bogus_1\")\n```").function_call))
# {"retrieved_user_profiles": [{}]}
print(simulator.reply(parse_output("```tool_code\nupdate_user_status(user_id=\"bob_1\", new_status=\"active\")\n```").function_call))
# {"user_id": "bob_1", "new_status": "active"}
print(simulator.reply(parse_output("```tool_code\nget_user_profile(user_id=\"bob_1\")\n```").function_call))
# {"retrieved_user_profiles": [{"name": "Bob", "email": "bob@example.com", "status": "active"}]}
~~~

## Step 4: Configure Models and Prompt Builders for Simulation

To set up our simulation we need `PromptBuilder` objects for the function
calling model (`DataGenerationPromptBuilder`) and the replier model
(`ReplierPromptBuilder`). In some cases the replier (single-step function
calling) can be empty.

The `DataGenerationPromptBuilder` class is a wrapper around an inner
`PromptBuilder` and a session. It facilitates the interaction between the
environment and the tool calling model via
`DataGenerationPromptBuilder.compute_function_reply`. To create an instance you
need the `Session` and `parse_function` defined above.

~~~python
from tool_simulation.core import gemma_prompt_builder
from tool_simulation.stages.function_calling import datagen_prompt_builder as datagen_pb
from tool_simulation.stages.utils import margin


my_query = "Set the status of bob_1 to inactive."
inner_fc_pb = gemma_prompt_builder.GemmaPromptBuilder()
inner_fc_pb.user_turn(margin.trim_margin(f"""
    |You are an agent managing user profiles and statuses.
    |Available functions (schema provided below):
    |```json
    |{tool2str.tool2str(my_api)}
    |```
    |When calling a function, output ONLY the function call in the format: ```tool_code\nfunction_name(arg1='value1', arg2=...)\n```
    |User Query: {my_query}
    """))

datagen_pbuilder = datagen_pb.DataGenerationPromptBuilder(
    inner_prompt_builder=inner_fc_pb,
    session=SimplifiedAPISimulator(),
    parse_fn=parse_output,
)
~~~

We can inspect the formatted prompt as follows: `python
print(datagen_pbuilder.get_prompt())`

Similarly, we define a `ReplierPromptBuilder`. In this case we instruct it to
avoid asking follow-up questions.

```python
from tool_simulation.stages.function_calling import replier_prompt_builder
from tool_simulation.stages.utils import margin


replier_pbuilder = replier_prompt_builder.ReplierPromptBuilder()
replier_pbuilder.system_turn(margin.trim_margin("""
    |Pretend you are a user talking to an agent. The agent is responsible for
    >managing a user profiles tracker. Your messages are prefaced by the `User`
    >role, while the agent's responses are prefaced by the `Assistant` role.
    >If the agent is able to successfully complete the task, please
    >reply with STOP. If it made an error, reply with ERROR.
    |Do not ask the assistant any follow-up questions.
    |When you return your reply, do not preface it with any role, that happens
    >automatically.
    """))
replier_pbuilder.user_turn(my_query)
```

To run an episode, we also need inference backends for the two prompt builders.
We will use the AI Studio SDK with gemma models.

```python
from tool_simulation.core import aistudio_backend


api_key = "YOUR_API_KEY"
fc_model_instance = aistudio_backend.AIStudioModel(
    api_key=api_key,
    model_name="gemma-3-27b-it",
)

replier_model_instance = aistudio_backend.AIStudioModel(
    api_key=api_key,
    model_name="gemini-2.0-flash",
)
```

## Step 5: Run a Simulation Episode

We are now ready to run a simulation episode. This can be done with the
`run_function_calling_episode` utlity. Optionally, you can also use some of the
utilities in the `validation` stage to validate the simulated episode.

```python
from tool_simulation.stages.function_calling import function_calling_episode


result = function_calling_episode.run_function_calling_episode(
  fc_prompt_builder=datagen_pbuilder,
  replier_prompt_builder=replier_pbuilder,
  function_calling_model=fc_model_instance,
  replier_model=replier_model_instance,
)
print(result.get_prompt())
```

## Step 6: Scaling to Multiple Queries

The example above is meant to guide through the internals of how a data
generation pipeline can be built. The tool simulation library comes with a set
of default pipelines under `tool_simulation/pipelines` that can be used.

## Step 7: Running Trained Model With the On-Device FC SDK

The generated datasets can be exported in the TF Example and HuggingFace JSON
formats depending on your training setup. After training, export your checkpoint
in a format compatible with the inference interface you are using. The FC SDK
comes bundled with the
[LLM Inference API](https://ai.google.dev/edge/mediapipe/solutions/genai/llm_inference).
To use this backend, you can convert your checkpoint following the
[LLM Inference Guide](https://ai.google.dev/edge/mediapipe/solutions/genai/llm_inference#models).
For advanced use-cases where you are using a model not natively supported by the
FC SDK, you can specify your own `ModelFormatter`.
To adapt a model in the `tool_simulation` library to your custom format, you can
use the `core/base_prompt_builder` classes.
