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

#include "parser_utils.h"

#include <algorithm>
#include <cstddef>
#include <exception>
#include <string>
#include <utility>
#include <vector>

#include "ANTLRErrorListener.h"
#include "ANTLRInputStream.h"
#include "AntlrJsonLexer.h"
#include "AntlrJsonParser.h"
#include "AntlrJsonParserBaseListener.h"
#include "AntlrPythonLexer.h"
#include "AntlrPythonParser.h"
#include "AntlrPythonParserBaseListener.h"
#include "CommonTokenStream.h"
#include "Parser.h"
#include "Recognizer.h"
#include "Token.h"
#include "absl/log/absl_check.h"       // from @abseil-cpp
#include "absl/log/absl_log.h"         // from @abseil-cpp
#include "absl/log/check.h"            // from @abseil-cpp
#include "absl/status/status.h"        // from @abseil-cpp
#include "absl/status/statusor.h"      // from @abseil-cpp
#include "absl/strings/numbers.h"      // from @abseil-cpp
#include "absl/strings/str_cat.h"      // from @abseil-cpp
#include "absl/strings/str_join.h"     // from @abseil-cpp
#include "absl/strings/str_split.h"    // from @abseil-cpp
#include "absl/strings/string_view.h"  // from @abseil-cpp
#include "atn/ATNConfigSet.h"
#include "dfa/DFA.h"
#include "google/protobuf/struct.pb.h"
#include "local_agents/core/proto/content.pb.h"
#include "local_agents/core/proto/generative_service.pb.h"
#include "re2/re2.h"  // from @re2
#include "tree/ParseTree.h"
#include "tree/ParseTreeWalker.h"
#include "tree/TerminalNode.h"

namespace odml::generativeai {

namespace {
using ::odml::genai_modules::core::proto::Candidate;
using ::odml::genai_modules::core::proto::Content;
using ::odml::genai_modules::core::proto::FunctionCall;
using ::odml::genai_modules::core::proto::GenerateContentResponse;

class DefaultErrorListener final : public antlr4::ANTLRErrorListener {
 public:
  DefaultErrorListener() : status_(true) {};

  void syntaxError(antlr4::Recognizer* recognizer,
                   antlr4::Token* offendingSymbol, size_t line,
                   size_t charPositionInLine, const std::string& msg,
                   std::exception_ptr e) override {
    status_ = false;
  };

  void reportAmbiguity(antlr4::Parser* recognizer, const antlr4::dfa::DFA& dfa,
                       size_t startIndex, size_t stopIndex, bool exact,
                       const antlrcpp::BitSet& ambigAlts,
                       antlr4::atn::ATNConfigSet* configs) override {
    status_ = false;
  };

  void reportAttemptingFullContext(
      antlr4::Parser* recognizer, const antlr4::dfa::DFA& dfa,
      size_t startIndex, size_t stopIndex,
      const antlrcpp::BitSet& conflictingAlts,
      antlr4::atn::ATNConfigSet* configs) override {
    status_ = false;
  };

  void reportContextSensitivity(antlr4::Parser* recognizer,
                                const antlr4::dfa::DFA& dfa, size_t startIndex,
                                size_t stopIndex, size_t prediction,
                                antlr4::atn::ATNConfigSet* configs) override {
    status_ = false;
  }
  bool status() const { return status_; }

 private:
  bool status_;
};

absl::string_view StripQuotes(absl::string_view text) {
  if (text.size() < 2 || (text.front() != '"' && text.front() != '\'') ||
      text.back() != text.front()) {
    return text;
  }
  return text.substr(1, text.size() - 2);
}

absl::StatusOr<google::protobuf::ListValue> ParseList(
    AntlrPythonParser::ListContext* list);

absl::StatusOr<google::protobuf::Struct> ParseDict(
    AntlrPythonParser::DictContext* dict);

absl::StatusOr<google::protobuf::Struct> ParseObject(
    AntlrPythonParser::ObjectContext* object);

absl::StatusOr<google::protobuf::Value> ParseValue(
    AntlrPythonParser::ValueContext* value) {
  google::protobuf::Value value_proto;
  if (value == nullptr) {
    return value_proto;
  }
  std::string text = value->getText();
  if (value->INT()) {
    int int_value;
    ABSL_CHECK(absl::SimpleAtoi(text, &int_value));
    value_proto.set_number_value(int_value);
  } else if (value->FLOAT()) {
    double double_value;
    ABSL_CHECK(absl::SimpleAtod(text, &double_value));
    value_proto.set_number_value(double_value);
  } else if (value->STRING()) {
    value_proto.set_string_value(StripQuotes(text));
  } else if (value->BOOL()) {
    value_proto.set_bool_value(text == "True");
  } else if (value->NONE()) {
    value_proto.set_null_value(google::protobuf::NULL_VALUE);
  } else if (value->list()) {
    auto list_value = ParseList(value->list());
    if (!list_value.ok()) {
      return list_value.status();
    }
    value_proto.mutable_list_value()->MergeFrom(list_value.value());
  } else if (value->dict()) {
    auto dict_value = ParseDict(value->dict());
    if (!dict_value.ok()) {
      return dict_value.status();
    }
    value_proto.mutable_struct_value()->MergeFrom(dict_value.value());
  } else if (value->object()) {
    auto object_value = ParseObject(value->object());
    if (!object_value.ok()) {
      return object_value.status();
    }
    value_proto.mutable_struct_value()->MergeFrom(object_value.value());
  }
  return value_proto;
}

absl::StatusOr<google::protobuf::ListValue> ParseList(
    AntlrPythonParser::ListContext* list) {
  google::protobuf::ListValue list_value;
  if (list == nullptr) {
    return list_value;
  }
  for (AntlrPythonParser::ValueContext* value : list->value()) {
    auto parsed_value = ParseValue(value);
    if (!parsed_value.ok()) {
      return parsed_value.status();
    }
    list_value.add_values()->MergeFrom(parsed_value.value());
  }
  return list_value;
}

absl::StatusOr<google::protobuf::Struct> ParseDict(
    AntlrPythonParser::DictContext* dict) {
  google::protobuf::Struct struct_value;
  if (dict == nullptr) {
    return struct_value;
  }
  const auto& keys = dict->STRING();
  const auto& values = dict->value();
  const size_t num_pairs = std::min(keys.size(), values.size());

  for (size_t i = 0; i < num_pairs; ++i) {
    antlr4::tree::TerminalNode* key_node = keys[i];
    AntlrPythonParser::ValueContext* value_ctx = values[i];

    if (key_node == nullptr || value_ctx == nullptr) {
      continue;
    }
    std::string key_text = std::string(StripQuotes(key_node->getText()));
    if (struct_value.mutable_fields()->contains(key_text)) {
      return absl::InvalidArgumentError(
          absl::StrCat("Duplicate key: ", key_text));
    }
    auto parsed_value = ParseValue(value_ctx);
    if (!parsed_value.ok()) {
      return parsed_value.status();
    }
    (*struct_value.mutable_fields())[key_text] =
        std::move(parsed_value).value();
  }
  return struct_value;
}

absl::StatusOr<google::protobuf::Struct> ParseObject(
    AntlrPythonParser::ObjectContext* object) {
  google::protobuf::Struct struct_value;
  if (object == nullptr || object->NAME() == nullptr) {
    return struct_value;
  }
  std::string object_name = object->NAME()->getText();
  google::protobuf::Value object_name_value;
  object_name_value.set_string_value(object_name);
  (*struct_value.mutable_fields())["__type__"] = object_name_value;
  if (object->argValExpr()) {
    for (const auto& arg_val : object->argValExpr()->argVal()) {
      if (arg_val == nullptr || arg_val->NAME() == nullptr ||
          arg_val->NAME()->getText().empty()) {
        continue;
      }
      std::string name = arg_val->NAME()->getText();
      if (arg_val->value() == nullptr || arg_val->value()->getText().empty()) {
        continue;
      }
      if ((*struct_value.mutable_fields()).contains(name)) {
        return absl::InvalidArgumentError(
            absl::StrCat("Duplicate key: ", name));
      }
      auto parsed_value = ParseValue(arg_val->value());
      if (!parsed_value.ok()) {
        return parsed_value.status();
      }
      (*struct_value.mutable_fields())[name] = parsed_value.value();
    }
  }
  return struct_value;
}

class PythonListener : public AntlrPythonParserBaseListener {
 public:
  PythonListener() : status_(false) {};
  void enterFunctionCall(AntlrPythonParser::FunctionCallContext* ctx) override;
  const std::vector<FunctionCall>& function_calls() const {
    return function_calls_;
  }
  bool status() const { return status_; }

 private:
  std::vector<FunctionCall> function_calls_;
  bool status_;
};

void PythonListener::enterFunctionCall(
    AntlrPythonParser::FunctionCallContext* ctx) {
  if (ctx == nullptr) {
    return;
  }
  FunctionCall function_call;
  if (ctx->fullFunctionCall()) {
    AntlrPythonParser::FullFunctionCallContext* fcContext =
        ctx->fullFunctionCall();
    if (fcContext == nullptr || fcContext->NAME() == nullptr ||
        fcContext->NAME()->getText().empty()) {
      return;
    }
    function_call.set_name(fcContext->NAME()->getText());
    AntlrPythonParser::ArgValExprContext* argVals = fcContext->argValExpr();
    if (argVals == nullptr) {
      return;
    }
    for (AntlrPythonParser::ArgValContext* argValue : argVals->argVal()) {
      if (argValue == nullptr || argValue->NAME() == nullptr ||
          argValue->NAME()->getText().empty()) {
        return;
      }
      std::string name = argValue->NAME()->getText();
      AntlrPythonParser::ValueContext* value = argValue->value();
      if (value == nullptr || value->getText().empty()) {
        return;
      }
      auto parsed_value = ParseValue(value);
      if (!parsed_value.ok()) {
        return;
      }
      if ((*function_call.mutable_args()->mutable_fields()).contains(name)) {
        // Duplicate arg name.
        status_ = false;
        return;
      }
      (*function_call.mutable_args()->mutable_fields())[name] =
          parsed_value.value();
    }
  } else if (ctx->emptyFunctionCall()) {
    if (ctx->emptyFunctionCall()->NAME() == nullptr) {
      return;
    }
    function_call.set_name(ctx->emptyFunctionCall()->NAME()->getText());
  } else {
    return;
  }

  function_calls_.push_back(function_call);
  status_ = true;
}

absl::StatusOr<google::protobuf::ListValue> ParseJsonArray(
    AntlrJsonParser::ArrayContext* array_ctx);

absl::StatusOr<google::protobuf::Struct> ParseJsonObject(
    AntlrJsonParser::ObjectContext* object_ctx);

// Parses a JSON value context into a google::protobuf::Value.
absl::StatusOr<google::protobuf::Value> ParseJsonValue(
    AntlrJsonParser::ValueContext* value_ctx) {
  google::protobuf::Value value_proto;
  if (value_ctx == nullptr) {
    return value_proto;
  }

  if (value_ctx->STRING()) {
    value_proto.set_string_value(StripQuotes(value_ctx->getText()));
  } else if (value_ctx->NUMBER()) {
    double double_value;
    // JSON numbers can be ints or floats, SimpleAtod handles both.
    if (!absl::SimpleAtod(value_ctx->getText(), &double_value)) {
      return absl::InvalidArgumentError(
          absl::StrCat("Failed to parse number: ", value_ctx->getText()));
    }
    value_proto.set_number_value(double_value);
  } else if (value_ctx->object()) {
    auto object_value = ParseJsonObject(value_ctx->object());
    if (!object_value.ok()) {
      return object_value.status();
    }
    value_proto.mutable_struct_value()->MergeFrom(object_value.value());
  } else if (value_ctx->array()) {
    auto array_value = ParseJsonArray(value_ctx->array());
    if (!array_value.ok()) {
      return array_value.status();
    }
    value_proto.mutable_list_value()->MergeFrom(array_value.value());
  } else if (value_ctx->BOOLEAN()) {
    // JSON booleans are lowercase 'true' or 'false'.
    value_proto.set_bool_value(value_ctx->getText() == "true");
  } else if (value_ctx->NONE()) {
    value_proto.set_null_value(google::protobuf::NULL_VALUE);
  } else {
    // Should not happen if the grammar is correct and covers all value types.
    return absl::InternalError(
        absl::StrCat("Unhandled JSON value type: ", value_ctx->getText()));
  }
  return value_proto;
}

// Parses a JSON array context into a google::protobuf::ListValue.
absl::StatusOr<google::protobuf::ListValue> ParseJsonArray(
    AntlrJsonParser::ArrayContext* array_ctx) {
  google::protobuf::ListValue list_value;
  if (array_ctx == nullptr) {
    return list_value;  // Return empty list for null context
  }

  for (AntlrJsonParser::ValueContext* value : array_ctx->value()) {
    absl::StatusOr<google::protobuf::Value> parsed_value =
        ParseJsonValue(value);
    if (!parsed_value.ok()) {
      return parsed_value.status();
    }
    list_value.add_values()->MergeFrom(parsed_value.value());
  }
  return list_value;
}

// Parses a JSON object context into a google::protobuf::Struct.
absl::StatusOr<google::protobuf::Struct> ParseJsonObject(
    AntlrJsonParser::ObjectContext* object_ctx) {
  google::protobuf::Struct struct_value;
  if (object_ctx == nullptr) {
    return struct_value;  // Return empty struct for null context
  }

  for (AntlrJsonParser::PairContext* pair_ctx : object_ctx->pair()) {
    if (pair_ctx == nullptr || pair_ctx->STRING() == nullptr ||
        pair_ctx->value() == nullptr) {
      // Skip invalid pairs, though this might indicate a parsing issue.
      ABSL_LOG(WARNING) << "Skipping invalid pair in JSON object.";
      continue;
    }

    std::string key_text =
        std::string(StripQuotes(pair_ctx->STRING()->getText()));
    if (key_text.empty()) {
      return absl::InvalidArgumentError("JSON object key cannot be empty.");
    }

    if ((*struct_value.mutable_fields()).contains(key_text)) {
      return absl::InvalidArgumentError(
          absl::StrCat("Duplicate key in JSON object: ", key_text));
    }

    absl::StatusOr<google::protobuf::Value> parsed_value =
        ParseJsonValue(pair_ctx->value());
    if (!parsed_value.ok()) {
      return absl::Status(
          parsed_value.status().code(),
          absl::StrCat("Error parsing value for key '", key_text,
                       "': ", parsed_value.status().message()));
    }
    (*struct_value.mutable_fields())[key_text] = parsed_value.value();
  }
  return struct_value;
}

class JsonListener : public AntlrJsonParserBaseListener {
 public:
  JsonListener() : status_(false) {};
  void enterFunctionCall(AntlrJsonParser::FunctionCallContext* ctx) override;
  void enterFunctionCallList(
      AntlrJsonParser::FunctionCallListContext* ctx) override {
    if (ctx == nullptr) {
      return;
    }
    if (ctx->OPEN_BRACKET() != nullptr && ctx->CLOSE_BRACKET() != nullptr &&
        ctx->functionCall().empty()) {
      status_ = true;
    }
  }

  const std::vector<FunctionCall>& function_calls() const {
    return function_calls_;
  }
  bool status() const { return status_; }

 private:
  std::vector<FunctionCall> function_calls_;
  bool status_;
};

void JsonListener::enterFunctionCall(
    AntlrJsonParser::FunctionCallContext* ctx) {
  if (ctx == nullptr) {
    return;
  }
  FunctionCall function_call;
  if (ctx->fullFunctionCall()) {
    AntlrJsonParser::FullFunctionCallContext* fcContext =
        ctx->fullFunctionCall();
    if (fcContext == nullptr || fcContext->functionNamePair() == nullptr ||
        fcContext->functionNamePair()->getText().empty()) {
      return;
    }
    function_call.set_name(
        StripQuotes(fcContext->functionNamePair()->STRING()->getText()));
    AntlrJsonParser::FunctionArgsPairContext* argsPair =
        fcContext->functionArgsPair();
    if (argsPair == nullptr) {
      return;
    }
    absl::StatusOr<google::protobuf::Struct> parsed_args =
        ParseJsonObject(argsPair->object());
    if (!parsed_args.ok()) {
      status_ = false;
    }
    function_call.mutable_args()->MergeFrom(parsed_args.value());
    function_calls_.push_back(function_call);
    status_ = true;
  } else if (ctx->emptyFunctionCall()) {
    status_ = true;
  } else {
    return;
  }
}

std::string FilterFunctionCallString(const std::string& function_call_string,
                                     const RE2& regex) {
  std::vector<absl::string_view> lines =
      absl::StrSplit(function_call_string, '\n');
  std::string captured_part;
  std::vector<std::string> captured_lines;

  for (absl::string_view line : lines) {
    if (RE2::PartialMatch(line, regex, &captured_part)) {
      captured_lines.push_back(captured_part);
    } else {
      captured_lines.push_back(std::string(line));
    }
  }

  return absl::StrJoin(captured_lines, "\n");
}

}  // namespace

absl::StatusOr<std::vector<FunctionCall>> ParsePythonExpression(
    absl::string_view text) {
  antlr4::ANTLRInputStream input(std::string(text.begin(), text.end()));
  AntlrPythonLexer lexer(&input);
  lexer.removeErrorListeners();
  DefaultErrorListener error_listener;
  lexer.addErrorListener(&error_listener);
  antlr4::CommonTokenStream tokens(&lexer);
  tokens.fill();
  if (!error_listener.status()) {
    // Lexer reported one or more errors.
    return absl::InvalidArgumentError("Failed to parse function call");
  }
  AntlrPythonParser parser(&tokens);
  parser.removeErrorListeners();
  DefaultErrorListener parser_error_listener;
  parser.addErrorListener(&parser_error_listener);
  antlr4::tree::ParseTree* tree = parser.main();
  if (!parser_error_listener.status()) {
    // Parser reported one or more errors.
    return absl::InvalidArgumentError("Failed to parse function call");
  }
  PythonListener listener;
  antlr4::tree::ParseTreeWalker::DEFAULT.walk(&listener, tree);

  if (!listener.status()) {
    // Listener reported one or more errors.
    return absl::InvalidArgumentError("Failed to parse function call");
  }

  return listener.function_calls();
}

absl::StatusOr<std::vector<FunctionCall>> ParseJsonExpression(
    absl::string_view text) {
  antlr4::ANTLRInputStream input(std::string(text.begin(), text.end()));
  AntlrJsonLexer lexer(&input);
  lexer.removeErrorListeners();
  DefaultErrorListener lexer_error_listener;
  lexer.addErrorListener(&lexer_error_listener);

  antlr4::CommonTokenStream tokens(&lexer);
  tokens.fill();  // Consume all tokens from the lexer.

  if (!lexer_error_listener.status()) {
    return absl::InvalidArgumentError(
        absl::StrCat("Failed to lexer JSON input.", text));
  }
  AntlrJsonParser parser(&tokens);
  parser.removeErrorListeners();
  DefaultErrorListener parser_error_listener;
  parser.addErrorListener(&parser_error_listener);

  // Start parsing from the 'json' rule.
  AntlrJsonParser::JsonContext* json_ctx = parser.json();

  if (!parser_error_listener.status() || parser.getNumberOfSyntaxErrors() > 0) {
    return absl::InvalidArgumentError(
        absl::StrCat("Failed to parse JSON input.", text));
  }

  if (json_ctx == nullptr) {
    return absl::InvalidArgumentError("Parsing resulted in a null context.");
  }

  JsonListener listener;
  antlr4::tree::ParseTreeWalker::DEFAULT.walk(&listener, json_ctx);

  if (!listener.status()) {
    // Listener reported one or more errors.
    return absl::InvalidArgumentError(
        absl::StrCat("Failed to parse function call", text));
  }

  return listener.function_calls();
}

TextAndFunctionCalls ParseTextAndFunctionCallsString(
    absl::string_view response_str, absl::string_view code_fence_start,
    absl::string_view code_fence_end, bool escape_in_fence_strings) {
  TextAndFunctionCalls result;
  absl::string_view text_before;
  absl::string_view code_block;

  // Construct the regex pattern: (non-greedy text before) <start> (non-greedy
  // code) <end> QuoteMeta escapes any special regex characters in the fence
  // strings.
  std::string pattern;
  if (escape_in_fence_strings) {
    pattern = absl::StrCat("(?ms)(.*?)", RE2::QuoteMeta(code_fence_start),
                           "(.*?)", RE2::QuoteMeta(code_fence_end));
  } else {
    pattern =
        absl::StrCat("(?ms)(.*?)", code_fence_start, "(.*?)", code_fence_end);
  }
  RE2 regex(pattern);
  if (RE2::PartialMatch(response_str, regex, &text_before, &code_block)) {
    // Found both start and end fences.
    result.text = text_before;
    result.function_calls = code_block;
  } else {
    // Did not find the full pattern (start_fence ... end_fence).
    // Check if the start fence exists at all.
    size_t start_pos = response_str.find(code_fence_start);
    if (start_pos != absl::string_view::npos) {
      // Found start fence but no end fence (or regex failed for other reasons).
      // Mimic the original behavior: text is before start, function_calls is
      // after start.
      ABSL_LOG(WARNING)
          << "Code fence start found, but end fence pattern did not match.";
      result.text = response_str.substr(0, start_pos);
      result.function_calls =
          response_str.substr(start_pos + code_fence_start.length());
    } else {
      // No start fence found at all. Treat the entire string as text.
      result.text = response_str;
    }
  }
  return result;
}

absl::StatusOr<GenerateContentResponse> ParseResponse(
    absl::string_view response_str, absl::string_view code_fence_start,
    absl::string_view code_fence_end, absl::string_view response_role,
    const SyntaxType& syntax_type, bool escape_in_fence_strings,
    absl::string_view tool_code_regex) {
  GenerateContentResponse response;
  Candidate* candidate = response.add_candidates();
  Content* content = candidate->mutable_content();
  content->set_role(response_role);
  TextAndFunctionCalls text_and_function_calls =
      ParseTextAndFunctionCallsString(response_str, code_fence_start,
                                      code_fence_end, escape_in_fence_strings);
  if (!text_and_function_calls.text.empty()) {
    content->add_parts()->set_text(text_and_function_calls.text);
  }
  if (!text_and_function_calls.function_calls.empty()) {
    std::string function_calls_to_parse =
        std::string(text_and_function_calls.function_calls);
    if (!tool_code_regex.empty()) {
      RE2 regex(tool_code_regex);
      if (!regex.ok()) {
        return absl::InvalidArgumentError(
            absl::StrCat("Invalid tool_code_regex: ", tool_code_regex));
      }
      function_calls_to_parse =
          FilterFunctionCallString(function_calls_to_parse, regex);
      if (function_calls_to_parse.empty()) {
        return response;
      }
    }

    absl::StatusOr<std::vector<FunctionCall>> function_calls;
    if (syntax_type == SyntaxType::kPython) {
      function_calls = ParsePythonExpression(function_calls_to_parse);
    } else if (syntax_type == SyntaxType::kJson) {
      function_calls = ParseJsonExpression(function_calls_to_parse);
    } else {
      return absl::InvalidArgumentError("Unsupported syntax type.");
    }
    if (function_calls.ok()) {
      for (const auto& function_call : *function_calls) {
        *content->add_parts()->mutable_function_call() = function_call;
      }
    } else {
      return absl::InternalError("Failed to parse tool call from output.");
    }
  }
  return response;
}

}  // namespace odml::generativeai
