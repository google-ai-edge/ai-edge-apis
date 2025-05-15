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

#ifndef THIRD_PARTY_ODML_GENAI_MODULES_UTILS_CORE_SOURCE_LOCATION_H_
#define THIRD_PARTY_ODML_GENAI_MODULES_UTILS_CORE_SOURCE_LOCATION_H_

#include <cstdint>

namespace odml::genai_modules {

// Class representing a specific location in the source code of a program.
// source_location is copyable.
class source_location {
 public:
  // Avoid this constructor; it populates the object with dummy values.
  constexpr source_location() : line_(0), file_name_(nullptr) {}

  // Wrapper to invoke the private constructor below. This should only be
  // used by the GENAI_MODULES_LOC macro, hence the name.
  static constexpr source_location DoNotInvokeDirectly(std::uint_least32_t line,
                                                       const char* file_name) {
    return source_location(line, file_name);
  }

  // The line number of the captured source location.
  constexpr std::uint_least32_t line() const { return line_; }

  // The file name of the captured source location.
  constexpr const char* file_name() const { return file_name_; }

  // column() and function_name() are omitted because we don't have a
  // way to support them.

 private:
  // Do not invoke this constructor directly. Instead, use the
  // GENAI_MODULES_LOC macro below.
  //
  // file_name must outlive all copies of the source_location
  // object, so in practice it should be a string literal.
  constexpr source_location(std::uint_least32_t line, const char* file_name)
      : line_(line), file_name_(file_name) {}

  std::uint_least32_t line_;
  const char* file_name_;
};

}  // namespace odml::genai_modules

// If a function takes a source_location parameter, pass this as the argument.
#define GENAI_MODULES_LOC \
  odml::genai_modules::source_location::DoNotInvokeDirectly(__LINE__, __FILE__)

#endif  // THIRD_PARTY_ODML_GENAI_MODULES_UTILS_CORE_SOURCE_LOCATION_H_
