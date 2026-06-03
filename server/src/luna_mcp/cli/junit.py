"""Hand-rolled JUnit XML writer using xml.etree (no external deps)."""
from __future__ import annotations

import time
import xml.etree.ElementTree as ET


class JUnitWriter:
    def __init__(self, suite_name: str):
        self._name = suite_name
        self._cases: list[dict] = []
        self._start = time.monotonic()

    def add_pass(self, name: str) -> None:
        self._cases.append({"name": name, "kind": "pass"})

    def add_failure(self, name: str, message: str) -> None:
        self._cases.append({"name": name, "kind": "failure", "message": message})

    def add_error(self, name: str, message: str) -> None:
        self._cases.append({"name": name, "kind": "error", "message": message})

    def build(self) -> ET.Element:
        failures = sum(1 for c in self._cases if c["kind"] == "failure")
        errors = sum(1 for c in self._cases if c["kind"] == "error")
        elapsed = f"{time.monotonic() - self._start:.3f}"
        suite = ET.Element("testsuite", {
            "name": self._name,
            "tests": str(len(self._cases)),
            "failures": str(failures),
            "errors": str(errors),
            "time": elapsed,
        })
        for c in self._cases:
            tc = ET.SubElement(suite, "testcase", {"name": c["name"], "time": "0"})
            if c["kind"] == "failure":
                fail = ET.SubElement(tc, "failure", {"message": c["message"]})
                fail.text = c["message"]
            elif c["kind"] == "error":
                err = ET.SubElement(tc, "error", {"message": c["message"]})
                err.text = c["message"]
        return suite

    def write(self, path: str) -> None:
        tree = ET.ElementTree(self.build())
        ET.indent(tree, space="  ")
        tree.write(path, encoding="unicode", xml_declaration=True)
