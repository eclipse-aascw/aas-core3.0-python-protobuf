"""Check that the version in ``pyproject.toml`` and ``__init__.py`` coincide."""

import importlib.metadata
import sys

import aas_core3_protobuf


def main() -> None:
    """Execute the main routine."""
    init_version = aas_core3_protobuf.__version__

    # NOTE (aaronzi, 2026-11-05):
    # Recent setuptools writes the metadata under the normalized name
    # aas_core3_0_protobuf, and importlib.metadata in Python 3.8 and 3.9 does not
    # normalize the dotted name aas-core3.0-protobuf, so we look up the normalized one.
    pyproject_toml_version = importlib.metadata.version("aas_core3_0_protobuf")

    if init_version != pyproject_toml_version:
        print(
            f"The version in {aas_core3_protobuf.__file__} is: {init_version!r}, "
            f"but the version in pyproject.toml is: {pyproject_toml_version!r}",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
