"""`LEAK_TOKENS` re-derived from the stimulus prose — SCAFFOLD item G3.

The registration's standard for this list is not "someone wrote a good list": it
is that the list is DERIVED from the frozen prose, that the derivation is
committed, and that a checker shows the list has power on mutated inputs. These
cases hold all three, and one of them holds the derivation against a part of the
source the derivation never reads — the design notes' own enumeration of the six
numeric thresholds — so "the rules found the right numerals" is checked against
the document rather than against the rules.
"""
import copy
import os
import re

import pytest

import batch
import leak_tokens
import transcript_check

HARNESS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WRAPPER = os.path.join(HARNESS, "authoring_call.sh")


@pytest.fixture(scope="module")
def text():
    return leak_tokens.source_text()


@pytest.fixture(scope="module")
def slice_text(text):
    return leak_tokens.stimulus(text)


# --- the slice --------------------------------------------------------------

def test_the_slice_is_the_sources_own_boundary(text, slice_text):
    """The source marks the boundary itself — everything after
    `## Design notes (not part of the stimulus)` is not the stimulus, and
    deriving tokens from it would deny the model the vocabulary of a document it
    never sees."""
    assert slice_text.startswith(leak_tokens.STIMULUS_BEGIN)
    assert leak_tokens.STIMULUS_END not in slice_text
    # the design notes really do carry vocabulary the stimulus does not
    assert "asymmetry ledger" in text
    assert "asymmetry ledger" not in slice_text


def test_a_source_whose_markers_are_not_unique_refuses(slice_text):
    for mutated in (slice_text,                                   # no END marker
                    leak_tokens.STIMULUS_BEGIN + slice_text
                    + leak_tokens.STIMULUS_END + leak_tokens.STIMULUS_END):
        with pytest.raises(leak_tokens.LeakTokenError) as caught:
            leak_tokens.stimulus(mutated)
        assert "occurring once" in str(caught.value)


def test_the_source_is_the_frozen_prose_when_it_exists():
    """`SOURCES` is ordered: `policy/POLICY.md` supersedes the draft the moment
    the freeze copies it into place, with no edit to this module."""
    assert leak_tokens.SOURCES[0] == "policy/POLICY.md"
    assert leak_tokens.SOURCES[1] == "design/POLICY-DRAFT.md"
    assert os.path.basename(leak_tokens.source_path()) in (
        "POLICY.md", "POLICY-DRAFT.md")


# --- R1, R2, R3 -------------------------------------------------------------

def test_the_domain_nouns_are_the_proses_own_markup(slice_text):
    nouns = leak_tokens.derive(slice_text)["byRule"]["R1 domain nouns"]
    # every input the policy names, from the `### Inputs` list's bold lead-ins
    for name in ("risk score", "requested spend", "sanctions screening result",
                 "country risk", "new vendor", "critical supplier",
                 "prior enforcement action", "financial evidence",
                 "insurance certificate"):
        assert name in nouns, name
    # the four outcome ids and the unresolved kind
    for name in ("approve", "review", "enhanced review", "reject", "unresolved"):
        assert name in nouns, name
    # a clause heading contributes its LABEL, not its id (rule R2 owns the id)
    assert "financial evidence" in nouns and "p1 — financial evidence" not in nouns
    assert "critical-supplier override" in nouns
    # …and the backticked identifier the prose carries
    assert "vendor-compliance-desk" in nouns


def test_the_clause_ids_are_derived_not_listed(slice_text):
    ids = leak_tokens.derive(slice_text)["byRule"]["R2 clause ids"]
    assert set(ids) == {"p1", "d1", "d2", "d3", "d4", "d5", "d6", "d6a", "d6b",
                        "d6c", "d7", "d8", "o1", "o2", "o3", "u1"}


def test_the_thresholds_are_the_six_the_design_notes_enumerate(text, slice_text):
    """The strongest available cross-check, and it is not circular: the
    derivation reads ONLY the stimulus slice, and this expectation is parsed out
    of the design notes AFTER that slice — the source's own count of its numeric
    thresholds, written for a reader and never read by the rules."""
    notes = text[text.index(leak_tokens.STIMULUS_END):]
    row = [line for line in notes.splitlines()
           if "6 numeric thresholds" in line]
    assert len(row) == 1, "the design notes' threshold row is not unique"
    enumerated = set(leak_tokens.NUMERAL.findall(row[0]))
    enumerated.discard("6")
    assert set(leak_tokens.threshold_literals(slice_text)) == enumerated
    assert enumerated == {"40", "70", "90", "100,000.00", "500,000.00",
                          "2,000,000.00"}


def test_every_threshold_carries_its_spellings(slice_text):
    tokens = set(leak_tokens.derive(slice_text)["tokens"])
    for word in ("forty", "seventy", "ninety", "one hundred thousand",
                 "five hundred thousand", "two million"):
        assert word in tokens, word
    for form in ("2,000,000.00", "$2,000,000.00", "2,000,000", "2000000"):
        assert form in tokens, form


def test_the_word_forms_are_derived_and_bounded():
    assert leak_tokens.words(40) == "forty"
    assert leak_tokens.words(70) == "seventy"
    assert leak_tokens.words(100000) == "one hundred thousand"
    assert leak_tokens.words(2000000) == "two million"
    assert leak_tokens.words(2500042) == "two million five hundred thousand forty-two"
    assert leak_tokens.words(0) == "zero"
    with pytest.raises(leak_tokens.LeakTokenError):
        leak_tokens.words(10 ** 12)


def test_a_numeral_never_ends_on_its_separator(slice_text):
    """`below 70, and` carries the numeral `70` and a clause comma; a pattern
    that swallowed the comma derived `70,`, a spelling the prose does not
    contain."""
    assert all(not literal.endswith(",")
               for literal in leak_tokens.threshold_literals(slice_text))
    assert not any(token.endswith(",")
                   for token in leak_tokens.derive(slice_text)["tokens"])


# --- admissibility ----------------------------------------------------------

def test_a_bare_two_digit_numeral_is_not_evidence(slice_text):
    """The rule that keeps `40`, `70` and `90` out. The wrapper screens the
    SCRATCH PATH with this list and that path ends in the wrapper's own pid, so a
    two-digit token would refuse honest calls for a reason that is not about the
    call."""
    dropped = {candidate: reason
               for _rule, candidate, reason in leak_tokens.derive(slice_text)["dropped"]}
    for numeral in ("40", "70", "90"):
        assert numeral in dropped
    assert leak_tokens.admissible("2000000") is None
    assert "digit run" in leak_tokens.admissible("40")
    # …and a numeral written with separators is NOT a bare numeral
    assert leak_tokens.admissible("2,000,000.00") is None
    assert leak_tokens.admissible("$500,000.00") is None


def test_a_sentence_is_not_a_token(slice_text):
    dropped = [candidate
               for _rule, candidate, reason in leak_tokens.derive(slice_text)["dropped"]
               if "a sentence is not a token" in reason]
    assert len(dropped) == 1
    assert dropped[0].startswith("if every readable value")


def test_the_short_words_the_policy_bolds_are_dropped(slice_text):
    dropped = {candidate
               for _rule, candidate, reason in leak_tokens.derive(slice_text)["dropped"]
               if "shorter than" in reason}
    assert "no" in dropped
    assert "no" not in leak_tokens.derive(slice_text)["tokens"]


def test_clause_ids_are_the_one_registered_exemption(slice_text):
    """Short by construction, exempted BY NAME and reported, rather than
    smuggled past the length floor."""
    result = leak_tokens.derive(slice_text)
    assert set(result["shortExempt"]) == {
        token for token in result["tokens"]
        if len(token) < leak_tokens.MIN_TOKEN_CHARS}
    assert all(leak_tokens.is_clause_id(token) for token in result["shortExempt"])


def test_every_drop_carries_its_reason(slice_text):
    """A derivation whose filter is invisible is a curated list wearing a
    derivation's clothes."""
    for rule, candidate, reason in leak_tokens.derive(slice_text)["dropped"]:
        assert rule.startswith("R")
        assert reason and isinstance(reason, str)
        assert leak_tokens.admissible(
            candidate, clause_id=rule.startswith("R2")) == reason


# --- power ------------------------------------------------------------------

def test_the_derived_list_catches_every_witness():
    report = leak_tokens.check_power()
    assert report["baselineUncaught"] == ()
    assert report["baselineCaught"] == report["witnesses"] > 50
    assert report["emptyCaught"] == 0
    assert report["scrambledCaught"] < report["baselineCaught"]


def test_the_witness_rule_and_the_token_rule_are_different_rules(slice_text):
    """The coverage above would be a tautology if witnesses were selected by the
    same filter the tokens survive. They are not: a witness is a sentence whose
    RAW markup names something, chosen before normalization and before
    `admissible()` runs — so a filter that dropped a load-bearing candidate shows
    up as an uncaught witness."""
    sentences = leak_tokens.witnesses(slice_text)
    assert sentences
    # a sentence whose only marked term is the bolded `no` — dropped from the
    # token list by the length floor — is still a witness, and is still caught
    unreported = [line for line in sentences if "treated as **no**" in line]
    assert unreported
    assert all(leak_tokens.catches(leak_tokens.LEAK_TOKENS, line)
               for line in unreported)


def test_a_mutated_token_list_fails_the_checker(monkeypatch, slice_text):
    """The registered demonstration: the checker must FAIL on a list that has
    been weakened, or it is not measuring the list."""
    original = leak_tokens.derive

    def mutated(text):
        result = copy.deepcopy(original(text))
        result["tokens"] = leak_tokens.scramble(result["tokens"])
        return result

    monkeypatch.setattr(leak_tokens, "derive", mutated)
    with pytest.raises(leak_tokens.LeakTokenError) as caught:
        leak_tokens.check_power()
    assert "witness sentences" in str(caught.value)


def test_an_emptied_list_fails_the_checker(monkeypatch, slice_text):
    monkeypatch.setattr(leak_tokens, "derive",
                        lambda text: {"tokens": (), "byRule": {}, "dropped": (),
                                      "shortExempt": ()})
    with pytest.raises(leak_tokens.LeakTokenError):
        leak_tokens.check_power()


def test_scrambling_lengthens_rather_than_truncates():
    """A truncated token is a SUBSTRING of the original and matches more, which
    would make the mutant look stronger than the list it weakens."""
    scrambled = leak_tokens.scramble(("review", "d6b"))
    assert scrambled == ("revie§", "d6§")
    assert not leak_tokens.catches(scrambled, "clause D6b refers a review")


def test_the_list_is_a_function_of_the_prose():
    """Move a threshold in the source and the derived list moves with it. A
    curated list would not, which is the property that distinguishes this module
    from the tuple it supersedes."""
    result = leak_tokens.check_rederivation()
    assert result["threshold"] == "2,000,000.00"
    assert "three million" in result["gained"]
    assert "two million" in result["lost"]


# --- the screening site -----------------------------------------------------

def test_no_token_fires_on_a_name_the_wrapper_builds():
    """The list would refuse honest runs if any token matched the scratch, home
    or per-run-binary names the wrapper constructs. Checked over every arm and
    every registered slot index."""
    assert leak_tokens.check_negative_corpus() > 1000
    assert leak_tokens.check_negative_corpus(leak_tokens.SCRATCH_TOKENS) > 1000


def test_the_screen_still_fires_on_a_path_that_carries_policy_vocabulary():
    """The other direction, so the case above is not passing because the list is
    inert: a scratch parent named after the stimulus refuses."""
    path = "/tmp/vendor-compliance-desk-scratch/s019-authoring-A-run-001-4242"
    assert leak_tokens.catches(leak_tokens.SCRATCH_TOKENS, path)


def test_the_wrapper_screens_with_this_module():
    """The wiring, read out of the wrapper's own bytes: SCAFFOLD G3's step is to
    replace the design-time tuple at the screening site, and a test that only
    checked the module would not notice if the wrapper still imported the other
    one."""
    with open(WRAPPER, "rb") as handle:
        body = handle.read().decode("utf-8")
    assert "import leak_tokens" in body
    assert "leak_tokens.SCRATCH_TOKENS" in body
    assert "transcript_check.LEAK_TOKENS" not in body


def test_the_screened_list_is_the_union_and_can_only_grow():
    """The derivation covers the STIMULUS, which by construction says nothing
    about jpack, the preregistration or the mutant machinery — a scratch path
    naming those would blunt the transcript screen exactly as a policy term
    would, so the wrapper takes the union and neither list alone."""
    assert set(leak_tokens.SCRATCH_TOKENS) == \
        set(leak_tokens.LEAK_TOKENS) | set(transcript_check.LEAK_TOKENS)
    assert len(leak_tokens.SCRATCH_TOKENS) > len(leak_tokens.LEAK_TOKENS)
    assert "jpack" in leak_tokens.SCRATCH_TOKENS


def test_the_freeze_step_is_a_diff_and_not_a_memory():
    """`transcript_check.LEAK_TOKENS` is still the design-time list, and the
    freeze must replace it. What must move is computed, not remembered."""
    gap = leak_tokens.design_time_gap()
    assert gap["missingFromDesignTime"], "the derivation adds nothing?"
    assert set(gap["missingFromDesignTime"]) == \
        set(leak_tokens.LEAK_TOKENS) - set(transcript_check.LEAK_TOKENS)
    assert set(gap["designTimeOnly"]) == \
        set(transcript_check.LEAK_TOKENS) - set(leak_tokens.LEAK_TOKENS)


def test_the_report_names_the_source_it_was_derived_from():
    """A published list whose source digest is not published is a list somebody
    has to trust."""
    report = leak_tokens.report()
    assert report["source"]["sha256"].startswith("sha256:")
    assert report["source"]["path"] in leak_tokens.SOURCES
    assert report["tokens"] == list(leak_tokens.LEAK_TOKENS)


def test_the_module_entry_point_runs_every_check():
    assert leak_tokens.main(["leak_tokens.py"]) == 0


def test_the_driver_does_not_carry_a_second_copy_of_the_list():
    """One list for the study. `batch.py` neither defines nor re-exports a leak
    vocabulary: the screening site is the wrapper's, and the derivation is this
    module's."""
    assert not hasattr(batch, "LEAK_TOKENS")
    assert not hasattr(batch, "SCRATCH_TOKENS")
