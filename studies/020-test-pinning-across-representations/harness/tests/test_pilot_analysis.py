"""The post-pilot analysis pass — round-2 findings R2-11 (its C4 reference
half) and R2-13 (its dispersion half), driven over a SEALED pilot tree
(`pilot_fixture`) with the scorer stubbed to emit kill records built
consistently from the real corpus, so `family.unit_from_kill_record()`'s
cross-check holds and every family function runs for real.

The dispersion table is the instrument the maintainer's 0.20 declaration
leans on for thin-but-alive arms, and the reviewer's blessing of 0.20 was
conditional on it existing. What these tests buy: the schema is CLOSED and
the no-peek gate discriminates (U1); exactly the eighteen members (U2); each
member's sigma is on its registered basis (U3); a NO-GO pilot publishes
nothing (U4); the chi-square interval reproduces the independently computed
factors (U5); NO contrast is ever computed (U6); the freeze gate names each
departure (U7); the pending pin reaches `--freeze` (U8); the published record
carries no per-run identity vocabulary (U9); and the prose moved as
registered (U10/U11)."""

import hashlib
import json
import os
import shutil
import sys
import unittest
from unittest import mock

import batch
import make_manifest
import pilot_analysis
import pilot_fixture
import pilot_rates
import score
import sweep_rates
from e4lib import dispersion
from e4lib import e4
from e4lib import family
from e4lib import transfer

HERE = os.path.dirname(os.path.abspath(__file__))
HARNESS = os.path.dirname(HERE)
STUDY = os.path.dirname(HARNESS)


def real_corpus():
    mutants = e4.load_mutants(
        os.path.join(STUDY, "mutants", "MANIFEST-jps.json"),
        os.path.join(STUDY, "mutants", "MANIFEST-rego.json"),
        os.path.join(STUDY, "mutants", "jps"),
        os.path.join(STUDY, "mutants", "rego"))
    table, _ = e4.build_pairing(mutants)
    supplied = dict((language, e4.engine_supplied_ids(mutants, language))
                    for language in family.LANGUAGES)
    return family.build_corpus(table, supplied)


def kill_block(corpus, language, covered_classes):
    """A kill record whose survivor vector covers exactly `covered_classes`
    (by index) in the given language, with the counts the corpus derives —
    so the cross-check in `unit_from_kill_record()` holds."""
    covered = set(covered_classes)
    survivors = []
    killed = {"included": 0, "excluded": 0}
    for index in range(len(corpus.classes)):
        for column in ("included", "excluded"):
            members = corpus.members(index, language, column)
            if index in covered:
                killed[column] += len(members)
        if index not in covered:
            survivors.extend(corpus.members(index, language, "included"))
    return {"survivorsPaired": sorted(set(survivors)),
            "killedPaired": killed["included"],
            "killedPairedExcludingEngineSupplied": killed["excluded"]}


class AnalysisFixture(unittest.TestCase):
    """A sealed GO pilot with a rates record, the scorer stubbed."""

    LABEL = "2026-08-24-pilot"

    def setUp(self):
        self.root = os.path.realpath(os.path.join(
            os.environ.get("TMPDIR", "/tmp"), "pilot-analysis-%d" % os.getpid()))
        shutil.rmtree(self.root, ignore_errors=True)
        os.makedirs(os.path.join(self.root, "harness"))
        self.addCleanup(shutil.rmtree, self.root, True)
        self.corpus = real_corpus()
        self.pins = {"calibration": {"minimumViable": 0.20,
                                     "minimumViableBasis": "identityFloor"},
                     "codex": {"reasoningEffort": "s020-stand-in-effort"},
                     "golden": {"sha256": "sha256:" + "3" * 64},
                     "batch": {"n": 60},
                     "family": {}}
        self.calibration = os.path.join(self.root, "calibration")
        patches = [
            mock.patch.object(pilot_analysis, "STUDY", self.root),
            mock.patch.object(pilot_analysis, "CALIBRATION_ROOT",
                              self.calibration),
            mock.patch.object(pilot_rates, "STUDY", self.root),
            mock.patch.object(pilot_rates, "CALIBRATION_ROOT",
                              self.calibration),
            mock.patch.object(sweep_rates, "STUDY", self.root),
            pilot_fixture.stub_transcript(),
            mock.patch.object(score, "scoring_context", self.fake_context),
            mock.patch.object(score, "score_run", self.fake_score_run),
        ]
        for patched in patches:
            patched.start()
            self.addCleanup(patched.stop)
        self.tree = pilot_fixture.build(self.root, self.LABEL, self.pins)
        self.publish_rates(identity={"A": 12, "B": 12, "C": 9})

    # -- the stubs -------------------------------------------------------------

    def fake_context(self, tools, pins, refusals, workspace):
        mutants = e4.load_mutants(
            os.path.join(STUDY, "mutants", "MANIFEST-jps.json"),
            os.path.join(STUDY, "mutants", "MANIFEST-rego.json"),
            os.path.join(STUDY, "mutants", "jps"),
            os.path.join(STUDY, "mutants", "rego"))
        pairing, paired_ids = e4.build_pairing(mutants)
        supplied = dict((language, e4.engine_supplied_ids(mutants, language))
                        for language in family.LANGUAGES)
        return {"gold": [], "mutants": mutants, "pairedIds": paired_ids,
                "engineSupplied": supplied, "pairing": pairing,
                "classes": [], "pins": pins}

    def fake_score_run(self, tools, arm, slot, context, workdir):
        """Coverage varies with the slot index so sigma is non-degenerate;
        identity fails for the last three of arm C's runs."""
        index = slot["slotIndex"]
        language = "jps" if arm == "A" else "rego"
        covered = list(range(0, 5 + (index % 7)))
        identity = not (arm == "C" and index > 9)
        return {"run": "run-%03d" % index, "arm": arm, "code": slot["code"],
                "admitted": True, "referenceIdentityPass": identity,
                "caseCount": 10 + index,
                "kill": kill_block(self.corpus, language, covered)}

    def score_slot(self, tools, arm, slot_dir, gold, guard, workdir, **kwargs):
        index = int(os.path.basename(slot_dir).split("-")[1])
        identity = not (arm == "C" and index > self.identity_c)
        return {"slot": os.path.relpath(slot_dir, self.root), "arm": arm,
                "code": None, "apparatusCode": None, "goldPerfect": False,
                "goldFailures": 3, "identityPass": identity,
                "identityWhy": None if identity else "kills-reference",
                "suitePresent": True}

    def publish_rates(self, identity):
        self.identity_c = identity["C"]
        with mock.patch.object(sweep_rates, "score_slot", self.score_slot):
            record = pilot_rates.pilot_rates(None, self.LABEL, [], os.path.join(
                self.root, "rates-scratch"), self.pins)
        path = os.path.join(self.calibration, self.LABEL, "PILOT-RATES.json")
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(record, handle, indent=2, sort_keys=True)
        self.record = record

    def run_publish(self):
        return pilot_analysis.publish(None, self.LABEL, self.pins,
                                      os.path.join(self.root, "scratch"))

    def write_both(self):
        reference, table = self.run_publish()
        here = os.path.join(self.calibration, self.LABEL)
        for name, body in ((transfer.REFERENCE_NAME, reference),
                           (pilot_analysis.DISPERSION_NAME, table)):
            with open(os.path.join(here, name), "w", encoding="utf-8") as h:
                json.dump(body, h, indent=2, sort_keys=True)
                h.write("\n")
        return reference, table

    def digest_of(self, name):
        with open(os.path.join(self.calibration, self.LABEL, name), "rb") as h:
            return "sha256:" + hashlib.sha256(h.read()).hexdigest()


class TheDispersionTable(AnalysisFixture):

    def test_the_go_pilot_publishes_eighteen_members_in_registered_order(self):
        """U2. MUTATION: drop M18 from the producer's loop — fails."""
        _reference, table = self.run_publish()
        self.assertEqual([row["id"] for row in table["perMember"]],
                         list(family.MEMBER_IDS))
        self.assertEqual(table["goNoGo"], "GO")
        self.assertIs(table["citable"], False)
        self.assertEqual(table["registeredN"], 60)
        for row in table["perMember"]:
            self.assertGreater(row["sigma"], 0.0)
            self.assertEqual(len(row["sigmaCI95"]), 2)
            self.assertLess(row["sigmaCI95"][0], row["sigma"])
            self.assertGreater(row["sigmaCI95"][1], row["sigma"])
            self.assertGreater(row["mdeAtPilotN"], 0.0)
            self.assertGreater(row["mdeAtRegisteredN"], 0.0)

    def test_each_members_sigma_is_on_its_registered_basis(self):
        """U3. The adjusted members' sigma is the residual SD, the others'
        the pooled within-arm SD — recomputed here from the same rows.
        MUTATION: swap the branch in `dispersion_table()` — fails."""
        _reference, table = self.run_publish()
        rows = dict((row["id"], row) for row in table["perMember"])
        for member in family.MEMBERS:
            basis = "residual" if member.adjusted else "pooledWithinArm"
            self.assertEqual(rows[member.id]["sigmaBasis"], basis, member.id)
        # An adjusted member and its unadjusted twin differ on sigma on this
        # fixture (caseCount varies with coverage here), so the assertion can
        # tell the two bases apart.
        self.assertNotAlmostEqual(rows["M3"]["sigma"], rows["M2"]["sigma"])

    def test_a_no_go_pilot_publishes_nothing(self):
        """U4. MUTATION: delete the GO check in `require_go()` — fails."""
        self.publish_rates(identity={"A": 12, "B": 12, "C": 5})
        self.assertFalse(self.record["goNoGo"]["go"])
        with self.assertRaisesRegex(pilot_analysis.AnalysisError,
                                    "ANALYSIS-NO-GO"):
            self.run_publish()

    def test_the_chi_square_interval_reproduces_the_independent_figures(self):
        """U5. df 15 -> [0.7387, 1.5477]; df 33 -> [0.8066, 1.3163], to four
        places (the round-2 plan's own computation). MUTATION: use N - 1 in
        place of N - k for df — the published df moves and the factor pin
        fails; use df - 1 in the quantile — fails."""
        self.assertEqual([round(v, 4) for v in dispersion.sigma_factors(15)],
                         [0.7387, 1.5477])
        self.assertEqual([round(v, 4) for v in dispersion.sigma_factors(33)],
                         [0.8066, 1.3163])
        _reference, table = self.run_publish()
        rows = dict((row["id"], row) for row in table["perMember"])
        m1 = rows["M1"]                   # ITT, unadjusted: N - k
        self.assertEqual(m1["df"], sum(m1["n"].values()) - 3)
        m3 = rows["M3"]                   # PP, adjusted: N - 4
        self.assertEqual(m3["df"], sum(m3["n"].values()) - 4)
        low, high = dispersion.sigma_factors(m1["df"])
        self.assertAlmostEqual(m1["sigmaCI95"][0], m1["sigma"] * low)
        self.assertAlmostEqual(m1["sigmaCI95"][1], m1["sigma"] * high)

    def test_no_contrast_is_ever_computed(self):
        """U6 — the only test that proves no pre-freeze contrast exists.
        MUTATION: implement the producer via `family_report()` — fails."""
        def boom(*args, **kwargs):
            raise AssertionError("a contrast was computed before the freeze")
        with mock.patch.object(family, "score_member", boom), \
                mock.patch.object(family, "family_report", boom):
            _reference, table = self.run_publish()
        self.assertEqual(len(table["perMember"]), 18)

    def test_the_no_peek_gate_refuses_a_direction(self):
        """U1. MUTATION: delete the `forbidden_members()` call in
        `publish()` — the poisoned table publishes."""
        self.assertEqual(pilot_analysis.forbidden_members(
            {"perMember": [{"id": "M1", "sigma": 0.1, "p": 0.04}]}),
            ["/perMember[0]/p"])
        original = pilot_analysis.dispersion_table
        def poisoned(label, pins, scored):
            table = original(label, pins, scored)
            table["perMember"][0]["difference"] = 0.12
            return table
        with mock.patch.object(pilot_analysis, "dispersion_table", poisoned):
            with self.assertRaisesRegex(pilot_analysis.AnalysisError,
                                        "ANALYSIS-NO-PEEK"):
                self.run_publish()

    def test_the_published_record_carries_no_per_run_identity_member(self):
        """U9. The vocabulary boundary: no `identityPass` and no
        `referenceIdentityPass` at any depth (no per-run row is published),
        and the rates record's bytes are untouched by the pass."""
        before = self.digest_of("PILOT-RATES.json")
        _reference, table = self.run_publish()
        body = json.dumps(table)
        self.assertNotIn('"identityPass"', body)
        self.assertNotIn('"referenceIdentityPass"', body)
        self.assertEqual(self.digest_of("PILOT-RATES.json"), before)

    def test_the_c4_reference_is_the_pilot_side_over_executed_slots(self):
        """R2-11's reference half over the same walk: eight exact rows filled
        from the sealed CALL.json bytes, three arms executed, the two band
        medians present and the token median descriptive."""
        reference, _table = self.run_publish()
        transfer.validate_reference(reference)
        self.assertEqual(reference["label"], self.LABEL)
        self.assertEqual(reference["exact"]["reasoningEffort"],
                         "s020-stand-in-effort")
        for arm in ("A", "B", "C"):
            self.assertEqual(reference["perArm"][arm]["executed"], 12)
            self.assertIsNotNone(
                reference["perArm"][arm]["medians"]["callDurationSeconds"])
            self.assertIsNotNone(
                reference["perArm"][arm]["medians"]["completionBytes"])
        self.assertEqual(reference["descriptiveMedians"],
                         ["reasoningOutputTokens"])


class TheFreezeGateAndPins(AnalysisFixture):

    def calibration_pins(self, **edits):
        calibration = {
            "label": self.LABEL,
            "minimumViable": 0.20, "minimumViableBasis": "identityFloor",
            "c4ReferenceSha256": self.digest_of(transfer.REFERENCE_NAME),
            "dispersionSha256": self.digest_of(pilot_analysis.DISPERSION_NAME),
        }
        calibration.update(edits)
        return calibration

    def test_the_gate_accepts_the_published_pair_and_names_each_departure(self):
        """U7, four branches (plus the reference's). MUTATION per branch:
        delete it — its case fails."""
        import pathlib
        self.write_both()
        root = pathlib.Path(self.root)
        pins = self.calibration_pins()          # snapshot BEFORE mutating
        problems = make_manifest.analysis_artifact_problems(
            root, self.LABEL, pins)
        self.assertEqual(problems, [])
        # absent
        os.rename(os.path.join(self.calibration, self.LABEL,
                               pilot_analysis.DISPERSION_NAME),
                  os.path.join(self.root, "moved.json"))
        problems = make_manifest.analysis_artifact_problems(
            root, self.LABEL, pins)
        self.assertTrue(any("is absent" in p for p in problems), problems)
        os.rename(os.path.join(self.root, "moved.json"),
                  os.path.join(self.calibration, self.LABEL,
                               pilot_analysis.DISPERSION_NAME))
        # digest mismatch
        problems = make_manifest.analysis_artifact_problems(
            root, self.LABEL, dict(pins, dispersionSha256="sha256:" + "0" * 64))
        self.assertTrue(any("dispersionSha256" in p for p in problems), problems)
        # seventeen members
        path = os.path.join(self.calibration, self.LABEL,
                            pilot_analysis.DISPERSION_NAME)
        with open(path) as handle:
            table = json.load(handle)
        table["perMember"] = table["perMember"][:17]
        with open(path, "w") as handle:
            json.dump(table, handle)
        problems = make_manifest.analysis_artifact_problems(
            root, self.LABEL, pins)
        self.assertTrue(any("eighteen" in p for p in problems), problems)
        # a forbidden key
        table["perMember"] = table["perMember"] + [
            {"id": "M18", "sigma": 0.1, "p": 0.03}]
        with open(path, "w") as handle:
            json.dump(table, handle)
        problems = make_manifest.analysis_artifact_problems(
            root, self.LABEL, pins)
        self.assertTrue(any("forbidden member" in p for p in problems), problems)

    def test_the_pending_pins_name_the_three_artifacts_until_pinned(self):
        """U8 / R2-11 T14. With the artifacts present and the pins null,
        `pending_pins()` names each with its digest, so `--freeze` refuses.
        MUTATION: remove a PENDING_PIN_SOURCES row — its name disappears."""
        self.write_both()
        with open(os.path.join(self.root, "harness", "PINS.json"), "w") as h:
            json.dump({"calibration": {"label": self.LABEL,
                                       "outputSha256": None,
                                       "c4ReferenceSha256": None,
                                       "dispersionSha256": None}}, h)
        pending = make_manifest.pending_pins(self.root)
        for dotted in ("calibration.outputSha256",
                       "calibration.c4ReferenceSha256",
                       "calibration.dispersionSha256"):
            self.assertTrue(any(name.startswith(dotted) for name in pending),
                            (dotted, pending))
        expected = self.digest_of(transfer.REFERENCE_NAME).split(":")[1]
        self.assertTrue(any(expected in name for name in pending), pending)


class TheProseMoved(unittest.TestCase):

    def prereg(self):
        with open(os.path.join(STUDY, "PREREGISTRATION.md"), "rb") as handle:
            return handle.read().decode("utf-8")

    def test_the_todo_is_gone_and_the_landed_description_names_the_file(self):
        """U11. MUTATION: leave the TODO — fails; rewrite a 019 sigma in
        place instead of appending — the retained-table assertion fails."""
        text = self.prereg()
        self.assertNotIn("TODO(prereg) — the dispersion re-derived", text)
        flat = " ".join(text.split())
        self.assertIn("PILOT-DISPERSION.json", flat)
        self.assertIn("calibration.dispersionSha256", flat)
        self.assertIn("stands BESIDE the prior", flat)
        self.assertIn("no-peek gate", flat)
        # §5.6's 019 table is retained as published: all eighteen sigmas.
        for sigma in ("0.25427", "0.28934", "0.28439", "0.32159", "0.28966",
                      "0.29826", "0.06938", "0.07895", "0.09397", "0.10516",
                      "0.09040", "0.09479", "0.05068", "0.05767", "0.06114",
                      "0.06849", "0.06049", "0.06420"):
            # Two cells of the retained table are bolded (M10, M3), so the
            # assertion is on the figure, not on its cell delimiters.
            self.assertIn(sigma, text, sigma)
        self.assertIn("retained as published; no figure in it moves", flat)

    def test_the_calibration_pins_are_freeze_pins_in_every_carrier(self):
        """The completeness review's finding beside R2-11: §2a.6's sentence
        was enforced by no label rule. Now the tuple, the registry's rule
        prose and the registration agree."""
        import integrity
        names = [name for name, _ in integrity.FREEZE_PINS]
        for name in ("calibrationLabel", "calibrationOutput",
                     "calibrationDerivedFloor", "c4Reference",
                     "pilotDispersion"):
            self.assertIn(name, names)
        with open(os.path.join(HARNESS, "PINS.json"), "rb") as handle:
            pins = json.loads(handle.read().decode("utf-8"))
        self.assertIn("twenty-three members", pins["registeredLabelRule"])
        self.assertIn("calibration.dispersionSha256 (pilotDispersion)",
                      pins["registeredLabelRule"])
        self.assertIsNone(pins["calibration"]["c4ReferenceSha256"])
        self.assertIsNone(pins["calibration"]["dispersionSha256"])
        self.assertIn("all five calibration", " ".join(self.prereg().split()))
        self.assertEqual(integrity.study_label(pins), "PILOT")
        self.assertIn("c4Reference", integrity.unfilled_pins(pins))


if __name__ == "__main__":
    unittest.main()
