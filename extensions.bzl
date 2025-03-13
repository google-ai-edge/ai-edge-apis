"""Static files for the ai_edge_apis module."""

load("//:rag_pipeline.bzl", "rag_pipeline_files")

def _non_module_dependencies_impl(_ctx):
    rag_pipeline_files()

non_module_dependencies = module_extension(
    implementation = _non_module_dependencies_impl,
)
