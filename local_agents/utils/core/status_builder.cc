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

#include "local_agents/utils/core/status_builder.h"

#include <memory>
#include <sstream>
#include <utility>

#include "absl/status/status.h"    // from @abseil-cpp
#include "absl/strings/str_cat.h"  // from @abseil-cpp
#include "local_agents/utils/core/source_location.h"

namespace odml::genai_modules {

StatusBuilder::StatusBuilder(const StatusBuilder& sb)
    : impl_(sb.impl_ ? std::make_unique<Impl>(*sb.impl_) : nullptr) {}

StatusBuilder& StatusBuilder::operator=(const StatusBuilder& sb) {
  if (!sb.impl_) {
    impl_ = nullptr;
    return *this;
  }
  if (impl_) {
    *impl_ = *sb.impl_;
    return *this;
  }
  impl_ = std::make_unique<Impl>(*sb.impl_);

  return *this;
}

StatusBuilder& StatusBuilder::SetAppend() & {
  if (!impl_) return *this;
  impl_->join_style = Impl::MessageJoinStyle::kAppend;
  return *this;
}

StatusBuilder&& StatusBuilder::SetAppend() && { return std::move(SetAppend()); }

StatusBuilder& StatusBuilder::SetPrepend() & {
  if (!impl_) return *this;
  impl_->join_style = Impl::MessageJoinStyle::kPrepend;
  return *this;
}

StatusBuilder&& StatusBuilder::SetPrepend() && {
  return std::move(SetPrepend());
}

StatusBuilder& StatusBuilder::SetNoLogging() & {
  if (!impl_) return *this;
  impl_->no_logging = true;
  return *this;
}

StatusBuilder&& StatusBuilder::SetNoLogging() && {
  return std::move(SetNoLogging());
}

StatusBuilder&& StatusBuilder::SetCode(absl::StatusCode code) && {
  return std::move(SetCode(code));
}

StatusBuilder& StatusBuilder::SetCode(absl::StatusCode code) & {
  if (!impl_) return *this;
  impl_->status = absl::Status(code, impl_->status.message());
  return *this;
}

StatusBuilder::operator absl::Status() const& {
  return StatusBuilder(*this).JoinMessageToStatus();
}

StatusBuilder::operator absl::Status() && { return JoinMessageToStatus(); }

absl::Status StatusBuilder::JoinMessageToStatus() {
  if (!impl_) {
    return absl::OkStatus();
  }
  return impl_->JoinMessageToStatus();
}

absl::Status StatusBuilder::Impl::JoinMessageToStatus() {
  if (stream.str().empty() || no_logging) {
    return status;
  }
  return absl::Status(status.code(), [this]() {
    switch (join_style) {
      case MessageJoinStyle::kAnnotate:
        return absl::StrCat(status.message(), "; ", stream.str());
      case MessageJoinStyle::kAppend:
        return absl::StrCat(status.message(), stream.str());
      case MessageJoinStyle::kPrepend:
        return absl::StrCat(stream.str(), status.message());
    }
  }());
}

StatusBuilder::Impl::Impl(const absl::Status& status,
                          odml::genai_modules::source_location location)
    : status(status), location(location), stream() {}

StatusBuilder::Impl::Impl(absl::Status&& status,
                          odml::genai_modules::source_location location)
    : status(std::move(status)), location(location), stream() {}

StatusBuilder::Impl::Impl(const Impl& other)
    : status(other.status),
      location(other.location),
      no_logging(other.no_logging),
      stream(other.stream.str()),
      join_style(other.join_style) {}

StatusBuilder::Impl& StatusBuilder::Impl::operator=(const Impl& other) {
  status = other.status;
  location = other.location;
  no_logging = other.no_logging;
  stream = std::ostringstream(other.stream.str());
  join_style = other.join_style;

  return *this;
}

}  // namespace odml::genai_modules
