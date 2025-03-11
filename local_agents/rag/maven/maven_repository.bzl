"""Starlark rule to create a maven repository from a single artifact."""

load("@build_bazel_rules_android//android:rules.bzl", "android_binary")

_pom_tmpl = "\n".join([
    '<?xml version="1.0" encoding="UTF-8"?>',
    '<project xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd"',
    '    xmlns="http://maven.apache.org/POM/4.0.0"',
    '    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">',
    "  <modelVersion>4.0.0</modelVersion>",
    "  <groupId>{group_id}</groupId>",
    "  <artifactId>{artifact_id}</artifactId>",
    "  <version>{version}</version>",
    "  <packaging>{packaging}</packaging>",
    "{identity}",
    "  <licenses>",
    "    <license>",
    "      <name>The Apache Software License, Version 2.0</name>",
    "      <url>http://www.apache.org/licenses/LICENSE-2.0.txt</url>",
    "      <distribution>repo</distribution>",
    "    </license>",
    "  </licenses>",
    "  <developers>",
    "    <developer>",
    "      <name>The MediaPipe Authors</name>",
    "    </developer>",
    "  </developers>",
    "  <dependencies>",
    "{dependencies}",
    "  </dependencies>",
    "</project>",
    "",
])

_identity_tmpl = "\n".join([
    "  <name>{lib_name}</name>",
    "  <description>{lib_description}</description>",
    "  <url>{lib_url}</url>",
    "  <inceptionYear>{inception_year}</inceptionYear>",
])

_dependency_tmpl = "\n".join([
    "    <dependency>",
    "      <groupId>{group_id}</groupId>",
    "      <artifactId>{artifact_id}</artifactId>",
    "      <version>{version}</version>",
    "      <scope>compile</scope>",
    "      <optional>{optional}</optional>",
    "    </dependency>",
])

_metadata_tmpl = "\n".join([
    '<?xml version="1.0" encoding="UTF-8"?>',
    "<metadata>",
    "  <groupId>{group_id}</groupId>",
    "  <artifactId>{artifact_id}</artifactId>",
    "  <version>{version}</version>",
    "  <versioning>",
    "    <release>{version}</release>",
    "    <versions>",
    "      <version>{version}</version>",
    "    </versions>",
    "  <lastUpdated>{last_updated}</lastUpdated>",
    "  </versioning>",
    "</metadata>",
    "",
])

def _packaging_type(f):
    """Returns the packaging type used by the file f."""
    if f.basename.endswith(".aar"):
        return "aar"
    elif f.basename.endswith(".jar"):
        return "jar"
    fail("Artifact has unknown packaging type: %s" % f.short_path)

def _create_pom_string(ctx):
    """Returns the contents of the pom file as a string."""
    dependencies = []
    for dep in ctx.attr.artifact_deps:
        if dep.count(":") != 2:
            fail("artifact_deps values must be of form: groupId:artifactId:version")

        group_id, artifact_id, version = dep.split(":")
        dependencies.append(_dependency_tmpl.format(
            group_id = group_id,
            artifact_id = artifact_id,
            version = version,
            optional = "false",
        ))

    for dep in ctx.attr.artifact_optional_deps:
        if dep.count(":") != 2:
            fail("artifact_optional_deps values must be of form: groupId:artifactId:version")

        group_id, artifact_id, version = dep.split(":")
        dependencies.append(_dependency_tmpl.format(
            group_id = group_id,
            artifact_id = artifact_id,
            version = version,
            optional = "true",
        ))

    return _pom_tmpl.format(
        group_id = ctx.attr.group_id,
        artifact_id = ctx.attr.artifact_id,
        version = ctx.attr.version,
        packaging = _packaging_type(ctx.file.src),
        identity = _identity_tmpl.format(
            lib_name = ctx.attr.lib_name,
            lib_description = ctx.attr.lib_description,
            lib_url = ctx.attr.lib_url,
            inception_year = ctx.attr.inception_year,
        ),
        dependencies = "\n".join(dependencies),
    )

def _create_metadata_string(ctx):
    """Returns the string contents of maven-metadata.xml for the group."""
    return _metadata_tmpl.format(
        group_id = ctx.attr.group_id,
        artifact_id = ctx.attr.artifact_id,
        version = ctx.attr.version,
        last_updated = ctx.attr.last_updated,
    )

def _maven_artifact_impl(ctx):
    """Generates maven repository for a single artifact."""
    pom = ctx.actions.declare_file(
        "%s/%s-%s.pom" % (ctx.label.name, ctx.attr.artifact_id, ctx.attr.version),
    )
    ctx.actions.write(output = pom, content = _create_pom_string(ctx))

    metadata = ctx.actions.declare_file("%s/maven-metadata.xml" % ctx.label.name)
    ctx.actions.write(output = metadata, content = _create_metadata_string(ctx))

    # Rename the artifact to match the naming required inside the repository.
    artifact = ctx.actions.declare_file("%s/%s-%s.%s" % (
        ctx.label.name,
        ctx.attr.artifact_id,
        ctx.attr.version,
        _packaging_type(ctx.file.src),
    ))
    ctx.actions.run_shell(
        inputs = [ctx.file.src],
        outputs = [artifact],
        command = "cp %s %s" % (ctx.file.src.path, artifact.path),
    )

    ctx.actions.run(
        inputs = [pom, metadata, artifact],
        outputs = [ctx.outputs.m2repository],
        arguments = [
            "--group_path=%s" % ctx.attr.group_id.replace(".", "/"),
            "--artifact_id=%s" % ctx.attr.artifact_id,
            "--version=%s" % ctx.attr.version,
            "--artifact=%s" % artifact.path,
            "--pom=%s" % pom.path,
            "--metadata=%s" % metadata.path,
            "--output=%s" % ctx.outputs.m2repository.path,
        ],
        executable = ctx.executable._maven_artifact,
        progress_message = (
            "Packaging repository: %s" % ctx.outputs.m2repository.short_path
        ),
    )

def android_jni_aar(name, source_library, native_libraries):
    """Builds an AAR file with jni.

    Args:
      name: The bazel target name.
      source_library: The source library to include in the AAR.
      native_libraries: The native binaries to include in the AAR.
    """

    # Generates dummy AndroidManifest.xml for dummy apk usage
    # (dummy apk is generated by <name>_dummy_app target below)
    native.genrule(
        name = name + "_binary_manifest_generator",
        outs = [name + "_generated_AndroidManifest.xml"],
        cmd = """
cat > $(OUTS) <<EOF
<manifest
  xmlns:android="http://schemas.android.com/apk/res/android"
  package="dummy.package.for.so">
  <uses-sdk android:minSdkVersion="24"/>
</manifest>
EOF
""",
    )

    # Generates dummy apk including .so files.
    # We extract out .so files and throw away the apk.
    android_binary(
        name = name + "_dummy_app",
        manifest = name + "_generated_AndroidManifest.xml",
        custom_package = "dummy.package.for.so",
        multidex = "native",
        deps = [source_library] + native_libraries,
    )

    native.genrule(
        name = name,
        srcs = [source_library + ".aar", name + "_dummy_app_unsigned.apk"],
        outs = [name + ".aar"],
        tags = ["manual"],
        cmd = """
cp $(location {}.aar) $(location :{}.aar)
chmod +w $(location :{}.aar)
origdir=$$PWD
cd $$(mktemp -d)
unzip $$origdir/$(location :{}_dummy_app_unsigned.apk) *
cp -r lib jni
zip -r $$origdir/$(location :{}.aar) jni/*/*.so
""".format(source_library, name, name, name, name),
    )

def java_proto_lite_srcs(name, jar, package_root, proto_files):
    """Extracts java proto lite srcs from a jar file.

    Args:
      name: The bazel target name.
      jar: The source jar file (usually a java_proto_lite target).
      package_root: The root package of the java proto lite srcs.
      proto_files: The proto files to extract.
    """
    package_path = package_root.replace(".", "/")
    native.genrule(
        name = name,
        srcs = [jar],
        outs = proto_files,
        cmd = """
            mkdir -p extracted_java
            for f in $(locations {0}); do
                if [[ $$f == *.jar ]]; then
                    unzip -qo $$f -d extracted_java
                fi
            done
            cp extracted_java/{1}/*.java $$(dirname $(location {2}))
        """.format(jar, package_path, proto_files[0]),
    )

maven_artifact = rule(
    implementation = _maven_artifact_impl,
    attrs = {
        "src": attr.label(
            mandatory = True,
            allow_single_file = [".aar", ".jar"],
        ),
        "group_id": attr.string(mandatory = True),
        "artifact_id": attr.string(mandatory = True),
        "version": attr.string(mandatory = True),
        "last_updated": attr.string(mandatory = True),
        "artifact_deps": attr.string_list(),
        "artifact_optional_deps": attr.string_list(),
        "lib_name": attr.string(default = ""),
        "lib_description": attr.string(default = ""),
        "lib_url": attr.string(default = ""),
        "inception_year": attr.string(default = ""),
        "_maven_artifact": attr.label(
            default = Label("@ai_edge_apis//local_agents/rag/maven:maven_artifact"),
            executable = True,
            allow_files = True,
            cfg = "exec",
        ),
    },
    outputs = {
        "m2repository": "%{name}.zip",
    },
)
