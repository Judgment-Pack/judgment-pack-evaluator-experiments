"""The carried census arithmetic, replayed against bytes Study 012 published.

WHAT THIS FILE DOES
-------------------
`harness/e4lib/census.py` carries four things verbatim out of Study 012's
`harness/census.py`: `_token()`, `show_signature()`, `encoding_key()`, and
`_x4().signature()` — landed here as `signature_groups()` with its ordering key
`(-runs, rendering)` unchanged. Study 012 PUBLISHED what those functions produce,
at `studies/012-policy-perturbation/RESULTS.json` →
`census[arm].x4.signatures.{probe,profile}.{distinct,groups}`.

So the carried arithmetic can be replayed. For each arm and each of 012's two
signature views this file

1. parses every published `signature` string back into the multiset it renders,
2. requires `show_signature()` to re-render that multiset to the SAME BYTES,
3. expands each group into one answer vector per run the group claims, giving a
   reconstructed population for the arm,
4. feeds that population through this study's `signature_groups()`, and
5. requires the ordered `(signature, runs)` list and the `distinct` count to
   reproduce 012's published values exactly.

Nothing is transcribed. Both the input and the expected output are read from
012's own frozen bytes; what this file supplies is only the reconstruction and
the call into THIS study's code. A drifted port fails here; a mistyped constant
cannot, because there is no constant to mistype.

WHAT THIS FILE DELIBERATELY DOES NOT DO
---------------------------------------
* **It is not §7 C3.1.** The archived E1-line's C3.1 replicated Study 011's
  `49 x 16 = 784` and `probesPerClass (2, 6, 2, 24, 26, 2)`. Those numbers are
  produced by 011's probe-class vocabulary — `_policy_mirror`, `probe`, `band`,
  `deciding_clause`, X1-X6 — and `e4lib/census.py`'s enumerated change 2
  declines to carry every one of them, on the registered ground that "carrying
  those functions would give this study six registered endpoints it did not
  register". Replicating C3.1 here would mean first porting the machinery the
  port refuses. This file replicates what canonical actually carried instead.
* **It controls no number 012 computed from raw records.** The reconstruction
  starts from 012's *rendered* signatures, so 012's own record loading, its
  probe and profile derivations, and its population arithmetic are upstream of
  everything asserted here. What is controlled is the arithmetic on this side of
  that boundary: `encoding_key`, `show_signature`, `_token`, and the ordering key.
* **It does not touch the two registered E5 rows.** A multiset destroys the
  order of a run's answers, so a reconstructed vector is not the vector 012 had
  — only its multiset is. `pairwise_disagreement()`, `cover_greedily()` and
  `census()` all read something a multiset cannot restore, and none of them is
  called here.
* **It compares `(signature, runs)` and `distinct` only.** `signature_groups()`
  adds a `runIds` member 012 did not publish; run identity is an artefact of the
  reconstruction and is not evidence.
* **It registers no endpoint and publishes nothing.** PREREGISTRATION.md §5
  registers E5 as exactly two rows and registers no replication control at all
  — §7 registers port fidelity as digest equality, in the two-sided `PORTS.md`
  table. This is a harness test and is admissible as one; it is not a result and
  no §5 row reads it.
* **It imports nothing from Study 012** and adds no `sys.path` entry for it. The
  sibling is read as JSON bytes, which is the weakest coupling that does the job;
  `integrity.TWELVE` is the precedent for reading 012's tree at all. When the
  sibling is absent the whole module SKIPS, with the path in the reason.
"""
from __future__ import annotations

import collections
import json
import os
import re

import pytest

from e4lib import census

HERE = os.path.dirname(os.path.abspath(__file__))
STUDY = os.path.dirname(os.path.dirname(HERE))
TWELVE_RESULTS = os.path.normpath(
    os.path.join(STUDY, "..", "012-policy-perturbation", "RESULTS.json"))

#: 012's two whole-run signature views. Both are distributions over distinct
#: whole-run multisets — the shape `signature_groups()` carries — and both are
#: replayed, because the port is one function and a view that exercised only
#: singleton groups would never reach the descending-run-count half of the
#: ordering key.
VIEWS = ("probe", "profile")

#: The arms 012 published a census for, read off the frozen document and pinned
#: so that a sibling that grew or lost an arm is a loud failure rather than a
#: quietly narrower control. Study 012 is frozen, so drift here is a finding.
PUBLISHED_ARMS = ("A", "B", "C", "D", "E")

#: `"(a, b) x3"`. Non-greedy so that a token containing its own parenthesis —
#: 012's profile view renders bands as `[40,70)` — ends at the first `") x"`
#: rather than at the last. The parse is not trusted on the strength of this
#: regex: every parsed multiset is re-rendered and required to match its source
#: bytes, and the matched spans are required to tile the whole string.
_ENTRY = re.compile(r"\((.*?)\) x(\d+)")


def _skip_reason():
    if not os.path.isfile(TWELVE_RESULTS):
        return ("Study 012's published results are not in this checkout: %s"
                % TWELVE_RESULTS)
    return None


_SKIP = _skip_reason()
pytestmark = pytest.mark.skipif(_SKIP is not None, reason=_SKIP or "")


def _published():
    with open(TWELVE_RESULTS, "rb") as handle:
        return json.loads(handle.read().decode("utf-8"))["census"]


def _arm_views():
    if _SKIP is not None:
        # One placeholder pair, so the module still collects and every case
        # reports the skip reason above rather than vanishing from the run.
        return [("(012 unread)", VIEWS[0])]
    return [(entry["arm"], view) for entry in _published() for view in VIEWS]


ARM_VIEWS = _arm_views()
IDS = ["%s-%s" % pair for pair in ARM_VIEWS]


def _parse_signature(text: str) -> tuple:
    """One published rendering, back to the multiset `show_signature()` renders.

    Returns the multiset in the order it was written, which is the order
    `show_signature()` consumes — `encoding_key()` re-sorts anyway, so the
    ordering carried out of here is asserted, never assumed.

    `"true"` and `"false"` become real booleans: 012's flags were booleans, and
    `_token()`'s one job is to lower-case them, so parsing them back as strings
    would leave that branch of the carried renderer untouched by the replay.
    """
    parsed = []
    position = 0
    separator_pending = False
    for match in _ENTRY.finditer(text):
        if match.start() != position:
            raise AssertionError(
                "the published signature does not tile into `(...) xN` entries; "
                "unparsed at offset %d: %r" % (position, text[position:]))
        parts = tuple(True if part == "true"
                      else False if part == "false"
                      else part
                      for part in match.group(1).split(", "))
        parsed.append((parts, int(match.group(2))))
        position = match.end()
        separator_pending = text[position:position + 2] == ", "
        if separator_pending:
            position += 2
    if separator_pending:
        raise AssertionError(
            "the published signature ends on a separator with no entry after "
            "it, so an entry was lost before this parse saw the bytes: %r" % text)
    if position != len(text):
        raise AssertionError("trailing bytes the parse did not consume: %r"
                             % text[position:])
    return tuple(parsed)


def _reconstruct(groups: list) -> dict:
    """The published group table, back to a population `{run id: vector}`.

    Each group claims `runs` runs carrying one multiset, so it expands to that
    many identical vectors. Run ids are synthetic and deterministic; they reach
    no assertion, because `signature_groups()` orders by `(-runs, rendering)`
    and never by run identity.
    """
    per_run = {}
    for index, group in enumerate(groups):
        multiset = _parse_signature(group["signature"])
        vector = [key for key, count in multiset for _ in range(count)]
        for copy in range(group["runs"]):
            per_run["g%03d-r%03d" % (index, copy)] = list(vector)
    return per_run


@pytest.fixture(scope="module")
def published():
    return {entry["arm"]: entry for entry in _published()}


def _view(published, arm, view):
    return published[arm]["x4"]["signatures"][view]


# --- the replay -------------------------------------------------------------

@pytest.mark.parametrize("arm,view", ARM_VIEWS, ids=IDS)
def test_the_published_signatures_round_trip_through_the_carried_renderer(
        published, arm, view):
    """`show_signature()` and `_token()`, replayed on 012's own bytes.

    The parse is the reconstruction's weak point, so it is checked the only way
    that costs nothing: the multiset it produces is handed straight back to this
    study's renderer, and the bytes must be identical to the ones 012 published.
    A renderer that changed its separator, its `xN` suffix, its `none` case or
    its boolean casing fails here before any grouping is attempted.
    """
    groups = _view(published, arm, view)["groups"]
    assert groups, "012 published no signature groups for arm %s %s" % (arm, view)
    for group in groups:
        multiset = _parse_signature(group["signature"])
        assert census.show_signature(multiset) == group["signature"]


@pytest.mark.parametrize("arm,view", ARM_VIEWS, ids=IDS)
def test_the_reconstructed_population_is_the_one_012_censused(
        published, arm, view):
    """The reconstruction is a faithful population, checked against 012's own
    published population size rather than against itself.

    This asserts nothing about the port. It asserts that the groups partition
    the arm — if they did not, the replay below would reproduce a group table
    over a population 012 never had, and would pass while meaning nothing.
    """
    entry = published[arm]
    per_run = _reconstruct(_view(published, arm, view)["groups"])
    assert len(per_run) == entry["population"]["runs"]
    lengths = {len(vector) for vector in per_run.values()}
    assert lengths == {entry["population"]["recordsPerRun"]["min"]}
    assert (entry["population"]["recordsPerRun"]["min"]
            == entry["population"]["recordsPerRun"]["max"])


@pytest.mark.parametrize("arm,view", ARM_VIEWS, ids=IDS)
def test_the_carried_grouping_reproduces_012s_published_group_table(
        published, arm, view):
    """The replication itself.

    `signature_groups()` — 012's `_x4().signature()` — run on the reconstructed
    population must produce 012's published table: the same groups, with the
    same run counts, in the same order, and the same `distinct` count.
    """
    view_record = _view(published, arm, view)
    groups = census.signature_groups(_reconstruct(view_record["groups"]))
    assert ([(group["signature"], group["runs"]) for group in groups]
            == [(group["signature"], group["runs"])
                for group in view_record["groups"]])
    assert len(groups) == view_record["distinct"]


@pytest.mark.parametrize("arm,view", ARM_VIEWS, ids=IDS)
def test_the_encoding_key_reads_a_run_as_a_multiset_on_012s_data(
        published, arm, view):
    """The property that licenses the reconstruction, checked on real data.

    `encoding_key()`'s docstring says two runs that answered the same stimulus
    the same way in a different internal order are ONE encoding. That is exactly
    why a rendered multiset can stand in for the vector 012 held — and it is why
    this file cannot control the two registered E5 rows. Reversing every vector
    must leave the whole group table byte-identical.
    """
    per_run = _reconstruct(_view(published, arm, view)["groups"])
    reversed_population = {run: list(reversed(vector))
                           for run, vector in per_run.items()}
    assert (census.signature_groups(reversed_population)
            == census.signature_groups(per_run))


@pytest.mark.parametrize("arm,view", ARM_VIEWS, ids=IDS)
def test_the_replayed_table_agrees_with_012s_derived_group_members(
        published, arm, view):
    """A second, redundant reading of the same replay.

    `groupSizes`, `runsSharing` and `singletons` are 012's arithmetic and are
    NOT carried into this study — nothing here computes them. Recomputing them
    from the replayed table and requiring them to match what 012 published is
    therefore free redundancy: it reads the reproduction through three numbers
    the equality above does not use, so a reproduction that agreed on the
    ordered list by coincidence would still have to agree on these.
    """
    view_record = _view(published, arm, view)
    groups = census.signature_groups(_reconstruct(view_record["groups"]))
    sizes = sorted((group["runs"] for group in groups if group["runs"] > 1),
                   reverse=True)
    assert sizes == view_record["groupSizes"]
    assert sum(sizes) == view_record["runsSharing"]
    assert (sum(1 for group in groups if group["runs"] == 1)
            == view_record["singletons"])


# --- the control has teeth --------------------------------------------------

def test_the_published_order_constrains_both_halves_of_the_ordering_key(
        published):
    """The replay above would pass under a weaker sort. This says it would not.

    `signature_groups()` orders by `(-runs, rendering)`. A port that had kept
    only the rendering, or only the run count with an arbitrary tie-break, would
    still reproduce a group table — so this file's central equality is only
    worth its bytes if 012's published order actually distinguishes those. It
    does, and here is the demonstration: at least one published view is ordered
    neither by rendering alone, nor by run count alone in the order the document
    happens to list the groups in.
    """
    by_rendering_only = []
    by_runs_only = []
    for arm in PUBLISHED_ARMS:
        for view in VIEWS:
            groups = _view(published, arm, view)["groups"]
            renderings = [group["signature"] for group in groups]
            counts = [group["runs"] for group in groups]
            by_rendering_only.append(renderings == sorted(renderings))
            by_runs_only.append(len(set(counts)) == 1)
    assert not all(by_rendering_only), (
        "no published view is out of pure rendering order, so the run-count "
        "half of the ordering key is not exercised by this file")
    assert not all(by_runs_only), (
        "every published view is single-valued in run count, so the rendering "
        "half of the ordering key is not exercised by this file")


def test_the_replay_covers_every_arm_and_view_012_published(published):
    """The control ran on something, and on all of it.

    A replication whose input silently narrowed to one arm would still be green.
    """
    assert tuple(sorted(published)) == PUBLISHED_ARMS
    for arm in PUBLISHED_ARMS:
        for view in VIEWS:
            record = _view(published, arm, view)
            assert record["groups"], "arm %s %s published no groups" % (arm, view)
            assert record["distinct"] == len(record["groups"])
    assert len(ARM_VIEWS) == len(PUBLISHED_ARMS) * len(VIEWS)


def test_the_parser_refuses_bytes_it_did_not_fully_consume():
    """The reconstruction's one piece of new code, and its refusal.

    A parse that silently dropped a trailing entry would shorten every vector it
    touched and could still round-trip the prefix it did read, so the tiling
    check is asserted directly rather than trusted.
    """
    multiset = _parse_signature("(a, b) x2, (c) x1")
    assert multiset == ((("a", "b"), 2), (("c",), 1))
    assert census.show_signature(multiset) == "(a, b) x2, (c) x1"
    assert _parse_signature("(false, true, [40,70)) x3") == (
        ((False, True, "[40,70)"), 3),)
    for bad in ("(a) x1 leftover", "(a) x1, ", "leading (a) x1", "(a)"):
        with pytest.raises(AssertionError):
            _parse_signature(bad)


def test_the_boolean_tokens_reach_the_carried_token_renderer():
    """`_token()`'s only job is the boolean case, and the replay must reach it.

    If `_parse_signature()` ever stopped producing real booleans, every
    assertion above would still pass — strings named `"true"` render as
    themselves — and `_token()` would be replayed by nothing.
    """
    parsed = _parse_signature("(true, false) x1")
    values = parsed[0][0]
    assert values == (True, False)
    assert [type(value) for value in values] == [bool, bool]
    assert census.show_signature(parsed) == "(true, false) x1"
    assert collections.Counter(values) == collections.Counter([True, False])


def test_cover_greedily_ignores_insertion_order():
    """The greedy cover's tie-break is `max(sorted(...))`, so which probe wins a
    tie is a fact about the probe names and not about dict insertion order. The
    independent mutation audit (N1) dropped the `sorted` and found a population
    where forward and backward insertion of THE SAME mapping return covering
    sets of different sizes -- a published `minimalCoveringSet` that depends on
    the order records happened to arrive. This is that population, both ways."""
    population = {
        "k00": {0, 3, 4, 5}, "k01": {2, 5}, "k02": {0, 3},
        "k03": {0, 1, 4, 5}, "k04": {0, 1, 3, 4}, "k05": {0, 3, 5},
    }
    forward = census.cover_greedily({k: population[k] for k in sorted(population)})
    backward = census.cover_greedily(
        {k: population[k] for k in sorted(population, reverse=True)})
    assert forward == backward == 3
