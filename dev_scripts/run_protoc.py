# SPDX-FileCopyrightText: 2023 aas-core3.0-python-protobuf AUTHORS
#
# SPDX-License-Identifier: MIT

"""Run protoc to (re-)generate the Python code for handling AAS ProtoBufs."""

import argparse
import os
import pathlib
import re
import shlex
import shutil
import subprocess
import sys

# NOTE (aaronzi, 2026-11-05):
# protoc does not emit any copyright or license information, so we prepend
# the header to the generated files ourselves. Otherwise, the headers would be
# lost on every re-generation. The generated files are derived from
# the definitions in aas-core-protobuf, so we attribute both the upstream and
# this repository.
#
# REUSE-IgnoreStart
_LICENSE_HEADER = """\
# SPDX-FileCopyrightText: 2024 aas-core-protobuf AUTHORS
# SPDX-FileCopyrightText: 2023 aas-core3.0-python-protobuf AUTHORS
#
# SPDX-License-Identifier: MIT

"""
# REUSE-IgnoreEnd

_CODING_LINE_RE = re.compile(r"\A#.*coding[:=].*\n")

_LEADING_SPDX_COMMENTS_RE = re.compile(r"\A(?:#\s*(?:SPDX-[A-Za-z-]+:.*)?\n|\n)*")


def _prepend_license_header(text: str) -> str:
    """
    Replace any leading SPDX comment block in ``text`` with our license header.

    The coding line, if any, is kept as the very first line.
    """
    coding_line = ""
    mtch = _CODING_LINE_RE.match(text)
    if mtch is not None:
        coding_line = mtch.group(0)
        text = text[mtch.end() :]

    return (
        coding_line + _LICENSE_HEADER + _LEADING_SPDX_COMMENTS_RE.sub("", text, count=1)
    )


def main() -> int:
    """Execute the main routine."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()

    this_path = pathlib.Path(os.path.realpath(__file__))

    if shutil.which("protoc") is None:
        print(
            "The ProtoBuf compiler could not be found using `shutil.which` "
            "on `protoc`. Have you installed it on your system and does it reside on "
            "your PATH?",
            file=sys.stderr,
        )
        return 1

    cmd = [
        "protoc",
        "--proto_path",
        str(this_path.parent / "proto"),
        "--python_out",
        str(this_path.parent.parent / "aas_core3_protobuf"),
        "--pyi_out",
        str(this_path.parent.parent / "aas_core3_protobuf"),
        str(this_path.parent / "proto/types.proto"),
    ]

    completed = subprocess.run(cmd, cwd=str(this_path.parent), check=False)
    if completed.returncode != 0:
        cmd_joined = " ".join(shlex.quote(part) for part in cmd)
        print(
            f"Failed to run with exit code {completed.returncode}: {cmd_joined}",
            file=sys.stderr,
        )
        return 1

    for name in ["types_pb2.py", "types_pb2.pyi"]:
        path = this_path.parent.parent / "aas_core3_protobuf" / name
        text = path.read_text(encoding="utf-8")
        path.write_text(_prepend_license_header(text), encoding="utf-8")

    return 0


if __name__ == "__main__":
    sys.exit(main())
