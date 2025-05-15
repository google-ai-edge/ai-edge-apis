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

#ifndef THIRD_PARTY_ODML_GENAI_MODULES_UTILS_CORE_RET_CHECK_H_
#define THIRD_PARTY_ODML_GENAI_MODULES_UTILS_CORE_RET_CHECK_H_

#include "absl/base/optimization.h"  // from @abseil-cpp
#include "absl/status/status.h"      // from @abseil-cpp
#include "local_agents/utils/core/source_location.h"
#include "local_agents/utils/core/status_builder.h"

namespace odml::genai_modules {

// Returns a StatusBuilder that corresponds to a `RET_CHECK` failure.
StatusBuilder RetCheckFailSlowPath(
    odml::genai_modules::source_location location);

// Returns a StatusBuilder that corresponds to a `RET_CHECK` failure.
StatusBuilder RetCheckFailSlowPath(
    odml::genai_modules::source_location location, const char* condition);

// Returns a StatusBuilder that corresponds to a `RET_CHECK` failure.
StatusBuilder RetCheckFailSlowPath(
    odml::genai_modules::source_location location, const char* condition,
    const absl::Status& status);

inline StatusBuilder RetCheckImpl(
    const absl::Status& status, const char* condition,
    odml::genai_modules::source_location location) {
  if (ABSL_PREDICT_TRUE(status.ok()))
    return StatusBuilder(absl::OkStatus(), location);
  return RetCheckFailSlowPath(location, condition, status);
}

}  // namespace odml::genai_modules

#define RET_CHECK(cond)               \
  while (ABSL_PREDICT_FALSE(!(cond))) \
  return odml::genai_modules::RetCheckFailSlowPath(GENAI_MODULES_LOC, #cond)

#define RET_CHECK_OK(status) \
  RETURN_IF_ERROR(           \
      odml::genai_modules::RetCheckImpl((status), #status, GENAI_MODULES_LOC))

#define RET_CHECK_FAIL() \
  return odml::genai_modules::RetCheckFailSlowPath(GENAI_MODULES_LOC)

#define GENAI_MODULES_INTERNAL_RET_CHECK_OP(name, op, lhs, rhs) \
  RET_CHECK((lhs)op(rhs))

#define RET_CHECK_EQ(lhs, rhs) \
  GENAI_MODULES_INTERNAL_RET_CHECK_OP(EQ, ==, lhs, rhs)
#define RET_CHECK_NE(lhs, rhs) \
  GENAI_MODULES_INTERNAL_RET_CHECK_OP(NE, !=, lhs, rhs)
#define RET_CHECK_LE(lhs, rhs) \
  GENAI_MODULES_INTERNAL_RET_CHECK_OP(LE, <=, lhs, rhs)
#define RET_CHECK_LT(lhs, rhs) \
  GENAI_MODULES_INTERNAL_RET_CHECK_OP(LT, <, lhs, rhs)
#define RET_CHECK_GE(lhs, rhs) \
  GENAI_MODULES_INTERNAL_RET_CHECK_OP(GE, >=, lhs, rhs)
#define RET_CHECK_GT(lhs, rhs) \
  GENAI_MODULES_INTERNAL_RET_CHECK_OP(GT, >, lhs, rhs)

#endif  // THIRD_PARTY_ODML_GENAI_MODULES_UTILS_CORE_RET_CHECK_H_
