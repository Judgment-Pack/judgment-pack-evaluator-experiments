"""Tests for class_agreement.py that need neither evaluator.

The driver finds its corpus relative to its own file, so each test copies the
driver into a temporary directory with the same layout (harness/ beside
reference/conformance-evaluation/) and writes whatever manifest the verdict
needs. The two implementations are stand-ins: a shell script that prints fixed
output and exits with a fixed status for the Go side, and a stub jps_evaluator
package for the Python side. The real corpus never supplies an empty manifest,
a row both sides refuse, or a row on which they differ, so these verdicts can
only be held by tests.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))

PERMIT = json.dumps({"disposition": {"kind": "permit"}})
DENY = json.dumps({"disposition": {"kind": "deny"}})


class DriverVerdictTests(unittest.TestCase):
    def setUp(self):
        # A copy of the driver beside a writable corpus, in the same layout
        # the driver expects: manifest.json one directory above harness/.
        self.layout = tempfile.mkdtemp(prefix="agreement-layout-")
        harness_dir = os.path.join(self.layout, "harness")
        self.corpus = os.path.join(self.layout, "reference", "conformance-evaluation")
        os.makedirs(harness_dir)
        os.makedirs(self.corpus)
        shutil.copy(os.path.join(HERE, "class_agreement.py"), harness_dir)
        self.driver = os.path.join(harness_dir, "class_agreement.py")
        # The Python stand-in: a stub jps_evaluator package the driver runs
        # with `python -m jps_evaluator` from this directory.
        self.pyrepo = tempfile.mkdtemp(prefix="agreement-pyrepo-")
        # The Go stand-in: an executable shell script with fixed output.
        handle, self.gobin = tempfile.mkstemp(prefix="agreement-gobin-", suffix=".sh")
        os.close(handle)

    def tearDown(self):
        shutil.rmtree(self.layout, ignore_errors=True)
        shutil.rmtree(self.pyrepo, ignore_errors=True)
        try:
            os.unlink(self.gobin)
        except OSError:
            pass

    def write_manifest(self, cases):
        with open(os.path.join(self.corpus, "manifest.json"), "w") as handle:
            json.dump({"cases": cases}, handle)

    @staticmethod
    def one_row(row_id="row-1"):
        # The stand-ins ignore their arguments, so the pack need not exist;
        # the row carries only what the driver reads before invoking them.
        return {"id": row_id, "pack": "packs/stub.json", "facts": {}}

    def write_go_stub(self, output, status):
        quoted = output.replace("'", "'\\''")
        with open(self.gobin, "w") as handle:
            handle.write("#!/bin/sh\n")
            handle.write("printf '%%s' '%s'\n" % quoted)
            handle.write("exit %d\n" % status)
        os.chmod(self.gobin, 0o755)

    def write_py_stub(self, output, status):
        package = os.path.join(self.pyrepo, "jps_evaluator")
        os.makedirs(package, exist_ok=True)
        with open(os.path.join(package, "__init__.py"), "w") as handle:
            handle.write("")
        with open(os.path.join(package, "__main__.py"), "w") as handle:
            handle.write("import sys\nsys.stdout.write(%r)\nsys.exit(%d)\n" % (output, status))

    def run_driver(self):
        return subprocess.run(
            [sys.executable, self.driver, self.gobin, self.pyrepo],
            capture_output=True,
            text=True,
            timeout=120,
        )

    def test_an_empty_manifest_is_refused_and_names_zero_rows(self):
        self.write_manifest([])
        self.write_go_stub("", 0)
        self.write_py_stub("", 0)
        proc = self.run_driver()
        self.assertEqual(1, proc.returncode)
        self.assertEqual("", proc.stdout)
        self.assertIn("zero rows", proc.stderr)

    def test_two_identical_errors_do_not_agree(self):
        # Both sides fail with byte-identical output. The tuples compare
        # equal, but neither side produced a disposition, so the row differs.
        self.write_manifest([self.one_row()])
        self.write_go_stub("boom", 3)
        self.write_py_stub("boom", 3)
        proc = self.run_driver()
        self.assertEqual(1, proc.returncode)
        self.assertIn("DIFF", proc.stdout)
        self.assertIn("row-1", proc.stdout)
        self.assertIn("0/1 rows byte-agree between implementations", proc.stdout)

    def test_differing_dispositions_fail_the_row(self):
        self.write_manifest([self.one_row()])
        self.write_go_stub(PERMIT, 0)
        self.write_py_stub(DENY, 0)
        proc = self.run_driver()
        self.assertEqual(1, proc.returncode)
        self.assertIn("DIFF", proc.stdout)
        self.assertIn("row-1", proc.stdout)
        self.assertIn("0/1 rows byte-agree between implementations", proc.stdout)

    def test_matching_dispositions_agree(self):
        # Control: the same disposition from both stand-ins passes, showing
        # the stand-ins exercise the driver rather than failing for their own sake.
        self.write_manifest([self.one_row()])
        self.write_go_stub(PERMIT, 0)
        self.write_py_stub(PERMIT, 0)
        proc = self.run_driver()
        self.assertEqual(0, proc.returncode)
        self.assertIn("AGREE", proc.stdout)
        self.assertIn("1/1 rows byte-agree between implementations", proc.stdout)


if __name__ == "__main__":
    unittest.main()
