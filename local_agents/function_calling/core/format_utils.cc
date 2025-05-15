// Copyright 2025 The Google AI Edge Authors.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

#include "local_agents/function_calling/core/format_utils.h"

#include <algorithm>
#include <optional>
#include <sstream>
#include <string>
#include <utility>
#include <vector>

#include "absl/container/flat_hash_set.h"  // from @abseil-cpp
#include "absl/status/statusor.h"          // from @abseil-cpp
#include "absl/strings/match.h"            // from @abseil-cpp
#include "absl/strings/string_view.h"      // from @abseil-cpp
#include "google/protobuf/struct.pb.h"
#include "local_agents/core/proto/content.pb.h"
#include "local_agents/core/proto/generative_service.pb.h"

namespace odml::generativeai {

using ::google::protobuf::ListValue;
using ::google::protobuf::Struct;
using ::google::protobuf::Value;
using ::odml::genai_modules::core::proto::FunctionCall;
using ::odml::genai_modules::core::proto::FunctionDeclaration;
using ::odml::genai_modules::core::proto::FunctionResponse;
using ::odml::genai_modules::core::proto::Schema;
using ::odml::genai_modules::core::proto::Tool;
using ::odml::genai_modules::core::proto::Type;

namespace {

std::vector<std::pair<std::string, Value>> SortStructFields(
    const Struct& struct_value) {
  std::vector<std::pair<std::string, Value>> sorted_fields(
      struct_value.fields().begin(), struct_value.fields().end());
  std::sort(
      sorted_fields.begin(), sorted_fields.end(),
      [](const std::pair<std::string, Value>& a,
         const std::pair<std::string, Value>& b) { return a.first < b.first; });
  return sorted_fields;
}
}  // namespace

std::optional<absl::string_view> ExtractInnerText(absl::string_view text,
                                                  absl::string_view prefix,
                                                  absl::string_view suffix) {
  if (absl::StartsWith(text, prefix) && absl::EndsWith(text, suffix)) {
    return text.substr(prefix.size(),
                       text.size() - prefix.size() - suffix.size());
  }
  return std::nullopt;
}

std::vector<std::pair<std::string, Schema>> SortParameters(
    const Schema& schema) {
  absl::flat_hash_set<std::string> required_parameters(
      schema.required().begin(), schema.required().end());
  std::vector<std::pair<std::string, Schema>> sorted_parameters(
      schema.properties().begin(), schema.properties().end());
  std::sort(sorted_parameters.begin(), sorted_parameters.end(),
            [&required_parameters](const std::pair<std::string, Schema>& a,
                                   const std::pair<std::string, Schema>& b) {
              bool a_required = required_parameters.contains(a.first);
              bool b_required = required_parameters.contains(b.first);
              if (a_required == b_required) {
                return a.first < b.first;
              } else {
                return a_required;
              }
            });
  return sorted_parameters;
}

std::string FormatTypeAsJson(const Type& type) {
  switch (type) {
    case Type::STRING:
      return "string";
    case Type::INTEGER:
      return "integer";
    case Type::NUMBER:
      return "number";
    case Type::BOOLEAN:
      return "boolean";
    case Type::OBJECT:
      return "object";
    case Type::ARRAY:
      return "array";
    default:
      return "null";
  }
}

// TODO(b/397358238): Make this support nested objects. It would be good to
// rewrite the *json functions with a more robust library rather
// than what we have now.
std::string FormatFunctionDeclarationAsJson(
    const FunctionDeclaration& function_declaration) {
  std::stringstream ss;
  ss << "{";
  ss << "\"name\": \"" << function_declaration.name() << "\", ";
  ss << "\"description\": \"" << function_declaration.description() << "\", ";
  ss << "\"parameters\": {";
  ss << "\"type\": \"object\", ";
  ss << "\"properties\": {";

  int count = 0;
  for (const auto& [key, value] :
       SortParameters(function_declaration.parameters())) {
    ss << "\"" << key << "\": {";
    ss << "\"type\": \"" << FormatTypeAsJson(value.type()) << "\"";
    if (!value.description().empty()) {
      ss << ", \"description\": \"" << value.description() << "\"";
    }
    ss << "}";
    count += 1;
    if (count < function_declaration.parameters().properties_size()) {
      ss << ", ";
    }
  }

  ss << "}";

  if (function_declaration.parameters().required_size() > 0) {
    ss << ", \"required\": [";
    int required_count = 0;
    for (const auto& required_param :
         function_declaration.parameters().required()) {
      ss << "\"" << required_param << "\"";
      if (++required_count <
          function_declaration.parameters().required_size()) {
        ss << ", ";
      }
    }
    ss << "]";
  }

  ss << "}";
  ss << "}";
  return ss.str();
}

std::string FormatToolAsJson(const Tool& tool_def) {
  int num_functions = tool_def.function_declarations().size();
  std::stringstream ss;
  int count = 0;
  for (const FunctionDeclaration& func_decl :
       tool_def.function_declarations()) {
    ss << FormatFunctionDeclarationAsJson(func_decl);
    if (++count < num_functions) {
      ss << ",";
    }
    ss << "\n";
  }
  return ss.str();
}

std::string FormatValueAsPython(const Value& value) {
  std::stringstream ss;
  if (value.has_null_value()) {
    ss << "None";
  } else if (value.has_string_value()) {
    ss << "\"" << value.string_value() << "\"";
  } else if (value.has_number_value()) {
    ss << value.number_value();
  } else if (value.has_bool_value()) {
    ss << (value.bool_value() ? "True" : "False");
  } else if (value.has_struct_value()) {
    ss << FormatStructAsPython(value.struct_value());
  } else if (value.has_list_value()) {
    ss << FormatListAsPython(value.list_value());
  }
  return ss.str();
}

std::string FormatStructAsPython(const Struct& struct_value) {
  std::stringstream ss;
  ss << "{";
  int count = 0;
  for (const auto& [key, value] : SortStructFields(struct_value)) {
    ss << "\"" << key << "\"" << ": ";
    ss << FormatValueAsPython(value);
    count += 1;
    if (count < struct_value.fields_size()) {
      ss << ", ";
    }
  }
  ss << "}";
  return ss.str();
}

std::string FormatListAsPython(const ListValue& list_value) {
  std::stringstream ss;
  ss << "[";
  int count = 0;
  for (const auto& element : list_value.values()) {
    ss << FormatValueAsPython(element);
    count += 1;
    if (count < list_value.values_size()) {
      ss << ", ";
    }
  }
  ss << "]";
  return ss.str();
}

// Formats a single function call.
//
// Does *not* include code fence or square brackets.
// TODO(b/397358238): Make this fail on invalid function calls. Also test the
// formatting of objects via the __type__ field.
absl::StatusOr<std::string> FormatFunctionCallAsPython(
    const FunctionCall& call) {
  std::stringstream ss;
  ss << call.name() << "(";
  if (call.has_args()) {
    const google::protobuf::Struct& args = call.args();
    int count = 0;
    for (const auto& [key, value] : SortStructFields(args)) {
      ss << key << "=";
      ss << FormatValueAsPython(value);
      if (++count < args.fields_size()) {
        ss << ", ";
      }
    }
  }
  ss << ")";
  return ss.str();
}

std::string FormatValueAsJson(const Value& value) {
  if (value.has_struct_value()) {
    return FormatStructAsJson(value.struct_value());
  } else if (value.has_list_value()) {
    return FormatListAsJson(value.list_value());
  } else if (value.has_null_value()) {
    return "null";
  } else if (value.has_number_value()) {
    std::stringstream ss;
    ss << value.number_value();
    return ss.str();
  } else if (value.has_string_value()) {
    return "\"" + value.string_value() + "\"";
  } else if (value.has_bool_value()) {
    return value.bool_value() ? "true" : "false";
  }
  return "";
}

std::string FormatListAsJson(const google::protobuf::ListValue& list_value) {
  std::stringstream ss;
  ss << "[";
  int count = 0;
  for (const auto& element : list_value.values()) {
    ss << FormatValueAsJson(element);
    if (++count < list_value.values_size()) {
      ss << ", ";
    }
  }
  ss << "]";
  return ss.str();
}

std::string FormatStructAsJson(const Struct& struct_v) {
  int count = 0;
  std::stringstream ss;
  ss << "{";
  for (const auto& [key, value] : SortStructFields(struct_v)) {
    ss << "\"" << key << "\"" << ": ";
    ss << FormatValueAsJson(value);
    if (++count < struct_v.fields_size()) {
      ss << ", ";
    }
  }
  ss << "}";
  return ss.str();
}

absl::StatusOr<std::string> FormatFunctionCallAsJson(const FunctionCall& call) {
  std::stringstream ss;
  ss << "{";
  ss << "\"name\": \"" << call.name() << "\"";
  if (call.has_args()) {
    ss << ", \"arguments\": ";
    ss << FormatStructAsJson(call.args());
  }
  ss << "}";
  return ss.str();
}

absl::StatusOr<std::string> FormatFunctionResponseAsJson(
    const FunctionResponse& response) {
  std::stringstream ss;
  std::string response_json = FormatStructAsJson(response.response());
  ss << response_json;
  return ss.str();
}

}  // namespace odml::generativeai
