#!/usr/bin/env python3
"""Controls on what this study's numbers can mean (PREREGISTRATION.md §6).

C1 — the ported bytes are Study 010's. Every byte-identical port must hash to
010's registered digest, every adapted port's digest must be the one
`harness/PORTS.md` records, and 010's `PROTOCOL-LOCK.json` — which does not
digest itself — must hash to the value pinned here, so the digest table's
authority is not a mutable file.

C2 — the family still describes the pack it was written against. Every
mutation's patch preimage must be present, byte-exact, at its JSON pointer in
Study 010's pack C, and the six indexes must be contiguous 0-5. This study
applies no patch and builds no pack D; the check exists because a predicate
whose mutation no longer applies to that pack would be measuring nothing.

Both read Study 010's directory; neither writes to it, and no evaluator runs.
"""
from __future__ import annotations
import hashlib
import json
import os
import unittest

import integrity
import score_rates

HERE = os.path.dirname(os.path.abspath(__file__))
STUDY = os.path.dirname(os.path.dirname(HERE))
TEN = os.path.normpath(os.path.join(STUDY, "..", "010-blinded-oracle"))

LOCK_DIGEST = "sha256:4966aa821325417f2cbce24a1a6ce7a10a45eefcbe2ec8fc16a4b2f1113543b1"
BYTE_IDENTICAL = {
    "harness/policy_mirror.py": "harness/policy_mirror.py",
    "transcription/PROMPT.txt": "transcription/PROMPT.txt",
    "FAMILY.json": "FAMILY.json",
}
ADAPTED = ("harness/records_compile.py", "harness/transcript_check.py",
           "transcription/authoring_call.sh")


def digest(path: str) -> str:
    with open(path, "rb") as handle:
        return "sha256:" + hashlib.sha256(handle.read()).hexdigest()


class PortedBytes(unittest.TestCase):
    """C1."""

    def setUp(self):
        self.lock = json.load(open(os.path.join(TEN, "PROTOCOL-LOCK.json")))

    def test_study_010s_lock_is_the_file_this_study_pinned(self):
        self.assertEqual(digest(os.path.join(TEN, "PROTOCOL-LOCK.json")), LOCK_DIGEST)

    def test_the_byte_identical_ports_are_010s_locked_bytes(self):
        for source, destination in BYTE_IDENTICAL.items():
            registered = "sha256:" + self.lock["lockedInputs"][source].split(":")[-1]
            self.assertEqual(digest(os.path.join(TEN, source)), registered,
                             "%s is not at its locked digest in Study 010" % source)
            self.assertEqual(digest(os.path.join(STUDY, destination)), registered,
                             "%s is not byte-identical to Study 010's" % destination)

    def test_the_adapted_ports_carry_the_digest_ports_md_records(self):
        with open(os.path.join(STUDY, "harness", "PORTS.md")) as handle:
            ports = handle.read()
        for relative in ADAPTED:
            source = relative if relative.startswith("harness/") else relative
            base = self.lock["lockedInputs"][source]
            self.assertIn(base.split(":")[-1], ports,
                          "PORTS.md does not record %s's Study 010 base digest" % relative)
            here = digest(os.path.join(STUDY, relative)).split(":")[-1]
            self.assertIn(here, ports,
                          "PORTS.md does not record %s's current digest — the port "
                          "changed after its provenance was written" % relative)

    def test_the_registry_pins_what_the_scorer_refuses_without(self):
        pins = score_rates.load_json(os.path.join(STUDY, "harness", "PINS.json"))
        self.assertEqual(digest(os.path.join(STUDY, "transcription", "PROMPT.txt")),
                         pins["prompt"]["sha256"])
        self.assertEqual(digest(os.path.join(STUDY, "transcription", "PROBE-PROMPT.txt")),
                         pins["probePrompt"]["sha256"])
        self.assertEqual(digest(os.path.join(STUDY, "FAMILY.json")),
                         pins["family"]["sha256"])
        self.assertEqual(pins["codex"]["model"], "gpt-5.6-sol")

    def test_the_probe_prompt_is_the_registered_bytes(self):
        with open(os.path.join(STUDY, "transcription", "PROBE-PROMPT.txt"), "rb") as handle:
            self.assertEqual(handle.read(), b"Reply with exactly one word: ready")


class PortedBytesAtRunTime(unittest.TestCase):
    """C1 where §6 says it runs: as a precondition, not only in pytest.

    The check is exercised against a throwaway copy of the study, so the
    committed tree is never touched: one byte changed in the "byte-identical"
    mirror must stop the batch and the scorer, because that byte moves every
    rate and every §5 tier and nothing downstream would notice.
    """

    def setUp(self):
        self.lock = json.load(open(os.path.join(TEN, "PROTOCOL-LOCK.json")))

    def locked(self, source: str) -> str:
        """The bare digest Study 010's lock records for one of its own files —
        the authority every source cell below is checked against."""
        return self.lock["lockedInputs"][source].split(":")[-1]

    def copy_study(self) -> str:
        import shutil
        import tempfile
        root = tempfile.mkdtemp(prefix="s011-integrity-")
        self.addCleanup(shutil.rmtree, root, True)
        study = os.path.join(root, "011-copy")
        os.makedirs(os.path.join(study, "harness"))
        os.makedirs(os.path.join(study, "transcription"))
        for relative in sorted(integrity.REQUIRED_PORTS) + [
                "harness/PORTS.md", "harness/PINS.json", "transcription/PROBE-PROMPT.txt"]:
            shutil.copyfile(os.path.join(STUDY, relative), os.path.join(study, relative))
        return study

    def test_the_committed_tree_passes_the_check_it_registers(self):
        summary = integrity.verify()
        self.assertIn("harness/policy_mirror.py", summary["portedFiles"])
        self.assertEqual(summary["study010LockSha256"], LOCK_DIGEST)

    def test_one_changed_byte_in_a_ported_file_refuses(self):
        study = self.copy_study()
        target = os.path.join(study, "harness", "policy_mirror.py")
        with open(target, "a") as handle:
            handle.write("# one byte of drift\n")
        with self.assertRaises(integrity.IntegrityError) as caught:
            integrity.verify(study=study, ten=TEN)
        self.assertIn("policy_mirror.py", str(caught.exception))

    def test_a_row_deleted_from_the_table_refuses(self):
        study = self.copy_study()
        path = os.path.join(study, "harness", "PORTS.md")
        with open(path) as handle:
            kept = [line for line in handle
                    if "| `harness/records_compile.py` |" not in line]
        with open(path, "w") as handle:
            handle.writelines(kept)
        with self.assertRaises(integrity.IntegrityError) as caught:
            integrity.verify(study=study, ten=TEN)
        self.assertIn("records_compile.py", str(caught.exception))

    def test_a_registry_whose_pins_do_not_match_the_files_refuses(self):
        study = self.copy_study()
        path = os.path.join(study, "harness", "PINS.json")
        pins = json.load(open(path))
        pins["family"]["sha256"] = "sha256:" + "0" * 64
        with open(path, "w") as handle:
            json.dump(pins, handle, indent=2)
        with self.assertRaises(integrity.IntegrityError):
            integrity.verify(study=study, ten=TEN)

    def edit_ports_row(self, study: str, relative: str, old: str, new: str,
                       which: str = "all") -> str:
        """Rewrite one cell of one PORTS.md row. `which` picks the source cell
        ('first'), the destination cell ('last'), or both ('all') — the three
        shapes an editor of this file could take."""
        path = os.path.join(study, "harness", "PORTS.md")
        with open(path) as handle:
            lines = handle.read().splitlines(True)
        edited = None
        for index, line in enumerate(lines):
            if not line.startswith("| `%s` |" % relative):
                continue
            if which == "all":
                line = line.replace(old, new)
            elif which == "first":
                line = line.replace(old, new, 1)
            else:
                head, _, tail = line.rpartition(old)
                line = head + new + tail
            lines[index] = edited = line
        self.assertIsNotNone(edited, "no PORTS.md row for %s" % relative)
        with open(path, "w") as handle:
            handle.writelines(lines)
        return edited

    def test_a_port_edited_together_with_its_own_ports_row_still_refuses(self):
        """The freeze-blocking hole: `harness/PORTS.md` is an editable file in
        THIS study, so a table checked only against itself authenticates
        whatever the editor wrote. An attacker changes a byte of the mirror —
        which moves every rate and every §5 tier — and changes that row's two
        digest cells to match. Study 010's lock is untouched, and it is the
        only thing that can notice."""
        study = self.copy_study()
        target = os.path.join(study, "harness", "policy_mirror.py")
        with open(target, "a") as handle:
            handle.write("# one byte of drift\n")
        drifted = digest(target).split(":")[-1]
        locked = self.locked("harness/policy_mirror.py")
        self.edit_ports_row(study, "harness/policy_mirror.py", locked, drifted)
        with self.assertRaises(integrity.IntegrityError) as caught:
            integrity.verify(study=study, ten=TEN)
        self.assertIn("PROTOCOL-LOCK.json", str(caught.exception))

    def test_a_byte_identical_port_answers_to_the_lock_not_to_the_table(self):
        """The same attack with only the DESTINATION cell moved, so the source
        column still agrees with 010's lock. A port §2.1 calls byte-identical
        must equal 010's LOCKED bytes; a prose column saying 'no — byte
        identical' is not a check."""
        study = self.copy_study()
        target = os.path.join(study, "FAMILY.json")
        with open(target, "a") as handle:
            handle.write("\n")
        drifted = digest(target).split(":")[-1]
        locked = self.locked("FAMILY.json")
        # Only the DESTINATION cell moves, so the source column still agrees
        # with the lock and every source-side check passes.
        row = self.edit_ports_row(study, "FAMILY.json", locked, drifted, which="last")
        self.assertEqual(row.count(locked), 1, "the source cell must survive: %r" % row)
        self.assertIn(drifted, row)
        with self.assertRaises(integrity.IntegrityError) as caught:
            integrity.verify(study=study, ten=TEN)
        self.assertIn("BYTE-IDENTICALLY", str(caught.exception))

    def test_a_ports_row_naming_a_source_the_lock_does_not_lock_refuses(self):
        study = self.copy_study()
        # The source cell alone: the destination set still names the six files,
        # so the row survives to the lock lookup that has nothing to look up.
        self.edit_ports_row(study, "harness/policy_mirror.py",
                            "`harness/policy_mirror.py` |", "`harness/mirror.py` |",
                            which="first")
        with self.assertRaises(integrity.IntegrityError) as caught:
            integrity.verify(study=study, ten=TEN)
        self.assertIn("no such input", str(caught.exception))

    def test_a_lock_that_is_not_the_pinned_one_refuses_before_it_is_read(self):
        import shutil
        import tempfile

        study = self.copy_study()
        ten = tempfile.mkdtemp(prefix="s011-fake-ten-")
        self.addCleanup(shutil.rmtree, ten, True)
        lock = json.load(open(os.path.join(TEN, "PROTOCOL-LOCK.json")))
        # A lock that would bless a drifted mirror, if it were ever read.
        lock["lockedInputs"]["harness/policy_mirror.py"] = "sha256:" + "0" * 64
        with open(os.path.join(ten, "PROTOCOL-LOCK.json"), "w") as handle:
            json.dump(lock, handle, indent=2)
        with self.assertRaises(integrity.IntegrityError) as caught:
            integrity.verify(study=study, ten=ten)
        self.assertIn("not the pinned", str(caught.exception))


class RegisteredInterpreter(unittest.TestCase):
    """§2.6: the registry's `python` member is read by code, not only recorded.

    The reviewed draft registered CPython 3.12.11 and no harness code read it,
    while every README command ran a bare `python3` that resolves to 3.8.20 on
    this machine — so the registered runbook ran the batch under an
    unregistered interpreter.
    """

    def test_the_running_interpreter_is_the_registered_one(self):
        pins = json.load(open(os.path.join(STUDY, "harness", "PINS.json")))
        self.assertEqual(integrity.verify_interpreter(pins).split()[0],
                         pins["python"]["implementation"])

    def test_another_implementation_or_series_refuses(self):
        pins = json.load(open(os.path.join(STUDY, "harness", "PINS.json")))
        for member, value in (("implementation", "PyPy"), ("series", "3.8")):
            wrong = json.loads(json.dumps(pins))
            wrong["python"][member] = value
            with self.assertRaises(integrity.IntegrityError) as caught:
                integrity.verify_interpreter(wrong)
            self.assertIn("registers", str(caught.exception))

    def test_a_registry_pinning_no_interpreter_refuses(self):
        with self.assertRaises(integrity.IntegrityError):
            integrity.verify_interpreter({})

    def test_the_patch_level_is_recorded_and_not_required(self):
        # Registered honestly: CI pins the series and resolves whatever patch
        # release is current, so the check is implementation + series.
        pins = json.load(open(os.path.join(STUDY, "harness", "PINS.json")))
        loosened = json.loads(json.dumps(pins))
        loosened["python"]["version"] = "3.12.999"
        self.assertTrue(integrity.verify_interpreter(loosened))


class InlinedPolicy(unittest.TestCase):
    """§2.1's inlining claim, stated exactly rather than as 'verbatim'.

    `policy/POLICY.md` ends in LF and the prompt carries no trailing newline,
    so the prompt holds the policy's bytes with that final LF removed. The
    relation is exact and checkable; 'verbatim' was not.
    """

    def test_the_prompt_carries_the_policy_bytes_less_the_final_newline(self):
        with open(os.path.join(TEN, "policy", "POLICY.md"), "rb") as handle:
            policy = handle.read()
        with open(os.path.join(STUDY, "transcription", "PROMPT.txt"), "rb") as handle:
            prompt = handle.read()
        self.assertTrue(policy.endswith(b"\n"))
        self.assertNotIn(policy, prompt)
        self.assertIn(policy[:-1], prompt)
        self.assertFalse(prompt.endswith(b"\n"))


class FamilyCoherence(unittest.TestCase):
    """C2."""

    def setUp(self):
        lock = json.load(open(os.path.join(TEN, "PROTOCOL-LOCK.json")))
        pack_path = os.path.join(TEN, "packs", "vendor-screening-correct.pack.json")
        self.assertEqual(digest(pack_path),
                         lock["lockedInputs"]["packs/vendor-screening-correct.pack.json"])
        self.pack = json.load(open(pack_path))
        self.family = json.load(open(os.path.join(STUDY, "FAMILY.json")))

    def resolve(self, pointer: str):
        """RFC 6901, the subset the family uses: object members and array
        indexes, no escapes needed by these pointers."""
        node = self.pack
        for token in pointer.split("/")[1:]:
            node = node[int(token)] if isinstance(node, list) else node[token]
        return node

    def assign(self, document, pointer: str, value) -> None:
        node = document
        tokens = pointer.split("/")[1:]
        for token in tokens[:-1]:
            node = node[int(token)] if isinstance(node, list) else node[token]
        last = tokens[-1]
        if isinstance(node, list):
            node[int(last)] = value
        else:
            node[last] = value

    def test_every_patch_preimage_is_present_byte_exact_in_pack_c(self):
        for mutation in self.family["mutations"]:
            for patch in mutation["patch"]:
                found = self.resolve(patch["path"])
                self.assertEqual(json.dumps(found, sort_keys=True),
                                 json.dumps(patch["old"], sort_keys=True),
                                 "mutation %d's preimage is not at %s"
                                 % (mutation["index"], patch["path"]))

    def test_every_mutation_actually_changes_the_pack(self):
        """010's gate ran two clauses, and this is the second: a patch whose
        result equals pack C plants nothing, so the class it names would be a
        class of a defect that does not exist. It needs only the pack bytes
        and the patch — no evaluator — so there was no reason to drop it."""
        for mutation in self.family["mutations"]:
            patched = json.loads(json.dumps(self.pack))
            for patch in mutation["patch"]:
                self.assign(patched, patch["path"], patch["new"])
            self.assertNotEqual(patched, self.pack,
                                "mutation %d does not change the pack" % mutation["index"])

    def test_the_six_indexes_are_contiguous(self):
        self.assertEqual([mutation["index"] for mutation in self.family["mutations"]],
                         list(range(6)))

    def test_the_classes_the_scorer_reads_are_those_six_predicates(self):
        pins = score_rates.load_json(os.path.join(STUDY, "harness", "PINS.json"))
        classes = score_rates.load_family(os.path.join(STUDY, "FAMILY.json"),
                                          pins["family"]["sha256"])
        self.assertEqual(len(classes), 6)
        for entry, mutation in zip(classes, self.family["mutations"]):
            self.assertEqual(entry["predicate"], mutation["predicate"])


if __name__ == "__main__":
    unittest.main()
