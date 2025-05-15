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
import java.io.Closeable;
import java.util.List;

/** Utility class for creating and managing FST constraints using JNI. */
public final class FstConstraintProvider implements Closeable, ConstraintProvider {
  private long fstConstraintProviderHandle;

  static {
    System.loadLibrary("jni_fst_constraint_android");
  }

  /** Represents an FST constraint. */
  public static class FstConstraint implements Closeable, Constraint {
    private final long nativePtr;
    private final long sharedPtrNative;

    // Private constructor
    private FstConstraint(long ptr) {
      this.nativePtr = ptr;
      this.sharedPtrNative = 0;
    }

    @Override
    public long getConstraintHandle() {
      return sharedPtrNative;
    }

    @Override
    public void close() {
      nativeReleaseFstConstraint();
    }

    private native void nativeReleaseFstConstraint();
  }

  /**
   * Initializes the FST constraint provider.
   *
   * @param sentencePieceProcessorHandle The handle to the SentencePieceProcessor.
   */
  public FstConstraintProvider(long sentencePieceProcessorHandle) {
    if (fstConstraintProviderHandle != 0) {
      throw new IllegalStateException("FST constraint provider already initialized.");
    }
    fstConstraintProviderHandle = nativeCreateFstConstraintProvider(sentencePieceProcessorHandle);
  }

  @Override
  public Constraint createConstraint(List<Tool> tools, ConstraintOptions options) {
    if (fstConstraintProviderHandle == 0) {
      throw new IllegalStateException("FST constraint provider not initialized.");
    }
    byte[][] toolsArray = new byte[tools.size()][];
    for (int i = 0; i < tools.size(); i++) {
      toolsArray[i] = tools.get(i).toByteArray();
    }
    return nativeCreateFstConstraint(
        fstConstraintProviderHandle, toolsArray, options.toByteArray());
  }

  /** Deletes the FST constraint provider. */
  private void deleteFstConstraintProvider() {
    if (fstConstraintProviderHandle != 0) {
      nativeDeleteFstConstraintProvider(fstConstraintProviderHandle);
      fstConstraintProviderHandle = 0;
    }
  }

  @Override
  public void close() {
    this.deleteFstConstraintProvider();
  }

  // Native methods declared in jni_fst_constraint.cc
  private native long nativeCreateFstConstraintProvider(long sentencePieceProcessorHandle);

  private native void nativeDeleteFstConstraintProvider(long providerPtr);

  private native FstConstraint nativeCreateFstConstraint(
      long providerPtr, byte[][] tools, byte[] constraintOptionsBytes);
}
