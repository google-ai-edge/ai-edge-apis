"""Build rule to depend on files downloaded from GCS."""

# buildifier: disable=unnamed-macro
def ai_edge_files(srcs):
    """Links file from GCS with the current directory.

    Args:
      srcs: the names of the mediapipe_file target, which is also the name of
      the external file in ai_edge_files.bzl. For example, if `name` is Foo,
      `ai_edge_files` will create a link to the downloaded file
      "@ai_edge_apis_Foo_tfile" to the current directory as
      "Foo.tflite".
    """

    for src in srcs:
        archive_name = "ai_edge_apis_%s" % src.replace("/", "_").replace(".", "_").replace("+", "_")
        native.genrule(
            name = "%s_ln" % archive_name,
            srcs = ["@%s//file" % archive_name],
            outs = [src],
            output_to_bindir = 1,
            cmd = "ln $< $@",
        )
