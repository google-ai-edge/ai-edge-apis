package com.google.ai.edge.localagents.rag.models;

import com.google.auto.value.AutoOneOf;
import com.google.auto.value.AutoValue;
import com.google.protobuf.ByteString;

/**
 * Represents a part of a possibly larger content, which can be either text or inline data (Blob).
 */
@AutoOneOf(Part.Kind.class)
public abstract class Part {

  /** The possible kinds of data this Part can hold. */
  public enum Kind {
    TEXT,
    INLINE_DATA
  }

  public abstract Kind getKind();

  public abstract String text();

  public abstract Blob inlineData();

  public static Part ofText(String text) {
    return AutoOneOf_Part.text(text);
  }

  public static Part ofInlineData(Blob inlineData) {
    return AutoOneOf_Part.inlineData(inlineData);
  }

  /** Represents inlined binary data with a MIME type. */
  @AutoValue
  public abstract static class Blob {
    /** The possible MIME types for inline data. */
    public enum MimeType {
      IMAGE_PNG("image/png"),
      IMAGE_JPEG("image/jpeg");

      private final String value;

      MimeType(String value) {
        this.value = value;
      }

      @Override
      public String toString() {
        return value;
      }
    }

    public abstract MimeType mimeType();

    public abstract ByteString data();

    public static Blob create(MimeType mimeType, ByteString data) {
      return new AutoValue_Part_Blob(mimeType, data);
    }
  }
}
