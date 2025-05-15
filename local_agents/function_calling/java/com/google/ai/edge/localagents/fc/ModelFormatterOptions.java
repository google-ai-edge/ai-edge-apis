package com.google.ai.edge.localagents.fc;

import com.google.auto.value.AutoValue;

/** Options for formatting function call related data. */
@AutoValue
public abstract class ModelFormatterOptions {

  /** Whether to add a prompt template to the formatted output. */
  public abstract boolean addPromptTemplate();

  protected com.google.ai.edge.localagents.fc.proto.ModelFormatterOptions toProto() {
    return com.google.ai.edge.localagents.fc.proto.ModelFormatterOptions.newBuilder()
        .setAddPromptTemplate(addPromptTemplate())
        .build();
  }

  /** Builder for {@link ModelFormatterOptions}. */
  @AutoValue.Builder
  public abstract static class Builder {
    public abstract Builder setAddPromptTemplate(boolean addPromptTemplate);

    public final ModelFormatterOptions build() {
      return autoBuild();
    }

    abstract ModelFormatterOptions autoBuild();
  }

  public static Builder builder() {
    return new AutoValue_ModelFormatterOptions.Builder().setAddPromptTemplate(false);
  }
}
