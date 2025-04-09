"""Provides BUILD macros for ODML proto-buffers.
"""

_proto_library = native.proto_library
java_proto_library = native.java_proto_library
java_lite_proto_library = native.java_lite_proto_library
cc_proto_library = native.cc_proto_library

def provided_args(**kwargs):
    """Returns the keyword arguments omitting None arguments."""
    return {k: v for k, v in kwargs.items() if v != None}

def replace_suffix(string, old, new):
    """Returns a string with an old suffix replaced by a new suffix."""
    return string.endswith(old) and string[:-len(old)] + new or string

def replace_deps(deps, old, new):
    """Returns deps with an old suffix replaced by a new suffix.

    Args:
      deps: the specified dep targets.
      old: the suffix to remove.
      new: the suffix to insert.
    Returns:
      the modified dep targets.
    """
    if deps == None:
        return deps

    deps = [dep for dep in deps if not dep.endswith("_annotations")]
    deps = [replace_suffix(dep, old, new) for dep in deps]
    return deps

def ai_edge_proto_library_impl(
        name,
        srcs,
        deps = [],
        exports = None,
        visibility = None,
        testonly = None,
        compatible_with = None,
        alwayslink = None,
        def_proto = True,
        def_cc_proto = True,
        def_java_lite_proto = True,
        def_java_proto = True):
    """Defines the proto_library targets needed for all AI Edge platforms.

    Args:
      name: the new proto_library target name.
      srcs: the ".proto" source files to compile.
      deps: the proto_library targets for all referenced protobufs.
      exports: deps that are published with "import public".
      visibility: visibility of this target.
      testonly: true means the proto can be used for testing only.
      compatible_with: a list of environments the rule is compatible with.
      alwayslink: any binary depending on the generated C++ library will link all object files,
          useful if the protocol buffer is looked up dynamically.
      def_proto: define the proto_library target
      def_cc_proto: define the cc_proto_library target
      def_java_lite_proto: define the java_lite_proto_library target
      def_java_proto: define the java_proto_library target
    """

    # The proto_library targets for the compiled ".proto" source files.
    proto_deps = [":" + name]

    if def_proto:
        _proto_library(**provided_args(
            name = name,
            srcs = srcs,
            deps = deps,
            exports = exports,
            visibility = visibility,
            testonly = testonly,
            compatible_with = compatible_with,
        ))

    if def_cc_proto:
        cc_proto_library(**provided_args(
            name = replace_suffix(name, "_proto", "_cc_proto"),
            deps = proto_deps,
            visibility = visibility,
            testonly = testonly,
            compatible_with = compatible_with,
        ))

    if def_java_lite_proto:
        java_lite_proto_library(**provided_args(
            name = replace_suffix(name, "_proto", "_java_proto_lite"),
            deps = proto_deps,
            visibility = visibility,
            testonly = testonly,
            compatible_with = compatible_with,
        ))

    if def_java_proto:
        java_proto_library(**provided_args(
            name = replace_suffix(name, "_proto", "_java_proto"),
            deps = proto_deps,
            visibility = visibility,
            testonly = testonly,
            compatible_with = compatible_with,
        ))

def ai_edge_proto_library(
        name,
        srcs,
        deps = [],
        exports = None,
        visibility = None,
        testonly = None,
        compatible_with = None,
        alwayslink = None,
        def_proto = True,
        def_cc_proto = True,
        def_java_lite_proto = True,
        def_java_proto = True):
    """Defines the proto_library targets needed for all ODML platforms.

    Args:
      name: the new proto_library target name.
      srcs: the ".proto" source files to compile.
      deps: the proto_library targets for all referenced protobufs.
      exports: deps that are published with "import public".
      visibility: visibility of this target.
      testonly: true means the proto can be used for testing only.
      compatible_with: a list of environments the rule is compatible with.
      alwayslink: any binary depending on the generated C++ library will link all object files,
          useful if the protocol buffer is looked up dynamically.
      def_proto: define the proto_library target
      def_cc_proto: define the cc_proto_library target
      def_java_lite_proto: define the java_lite_proto_library target
      def_java_proto: define the java_proto_library target
    """

    ai_edge_proto_library_impl(
        name = name,
        srcs = srcs,
        deps = deps,
        exports = exports,
        visibility = visibility,
        testonly = testonly,
        compatible_with = compatible_with,
        alwayslink = alwayslink,
        def_proto = def_proto,
        def_cc_proto = def_cc_proto,
        def_java_lite_proto = def_java_lite_proto,
        def_java_proto = def_java_proto,
    )
