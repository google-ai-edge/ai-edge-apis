/**
 * Copyright 2025 The Google AI Edge Authors.
 *
 * <p>Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file
 * except in compliance with the License. You may obtain a copy of the License at
 *
 * <p>http://www.apache.org/licenses/LICENSE-2.0
 *
 * <p>Unless required by applicable law or agreed to in writing, software distributed under the
 * License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
 * express or implied. See the License for the specific language governing permissions and
 * limitations under the License.
 */
package com.google.ai.edge.localagents.fc;

import com.google.ai.edge.localagents.core.proto.Tool;
import com.google.ai.edge.localagents.fc.proto.ConstraintOptions;
import java.util.List;

/** A Constraint provider is responsible for creating and managing constraints. */
public interface ConstraintProvider {

  /**
   * Creates a constraint.
   *
   * @param tools The list of tools the constraint should be constrained to.
   * @param options The options to construct the constraint with.
   * @return The constraint.
   */
  public Constraint createConstraint(List<Tool> tools, ConstraintOptions options);

  /** Represents a constraint. */
  public static interface Constraint {
    public long getConstraintHandle();
  }
}
