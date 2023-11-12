#!/usr/bin/env python
# Copyright (c) 2021 elParaguayo
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# A short script which identifies any leftover print statements
import argparse
import ast
import os
import sys
from pathlib import Path
from typing import List


def folder(value):
    value = os.path.abspath(value)
    if not os.path.isdir(value):
        raise argparse.ArgumentTypeError("Invalid root folder.")
    return value


class PrintStatementChecker:
    """
    Object that takes path to libqtile module and loops over modules to
    identify undocumented commands.
    """
    def __init__(self, files: List[str], paths: None | List[str], verbose: bool = False):
        self.files = files
        self.paths = paths
        self.verbose = verbose
        self.errors = 0
        if self.verbose:
            print("Checking for print statements...")  # type: ignore

    def check(self) -> None:
        """
        Method to scan python files for surplus print statements.
        """
        if self.paths is not None:
            for path in self.paths:
                self.files.extend([f.as_posix() for f in Path(path).rglob("*.py")])

        for f in self.files:
            if self.verbose:
                print(f"Checking {f}...")  # type: ignore
            self._check_file(f)

    def _check_file(self, fname: str) -> None:
        """
        Check an individual file for print statements
        """
        with open(fname, "r") as f:
            raw = ast.parse(f.read(), type_comments=True)

        calls = [x for x in ast.walk(raw) if isinstance(x, ast.Call)]
        prints = [x for x in calls if getattr(x.func, "id", "") == "print"]

        ignores = [r.lineno for r in raw.type_ignores]

        for p in prints:
            if p.lineno in ignores:
                continue
            self.errors += 1
            print(f"{self.errors:>3} {fname}:{p.lineno}")  # type: ignore


def main():
    parser = argparse.ArgumentParser(description="Check code doesn't include debugging print statements.")
    parser.add_argument(
        "-f",
        "--folder",
        dest="folders",
        type=folder,
        action="append",
        help="Folder to search.",
    )
    parser.add_argument(
        "-w",
        "--warn-only",
        dest="warn",
        action="store_true",
        help="Don't return error code on failure."
    )
    parser.add_argument(
        "-v",
        "--verbose",
        dest="verbose",
        action="store_true",
        help="Print additional output"
    )
    parser.add_argument(
        "files",
        help="Files",
        nargs=argparse.REMAINDER
    )

    args = parser.parse_args()

    checker = PrintStatementChecker(args.files, args.folders, args.verbose)
    checker.check()

    if checker.errors and not args.warn:
        sys.exit(
            "ERROR: Code contains print statements. "
            "Note: You can use '# type: ignore' to suppress error checking."
        )
    elif not checker.errors:
        if args.verbose:
            print("No print statements found.")  # type: ignore
        sys.exit(0)


if __name__ == "__main__":
    main()
