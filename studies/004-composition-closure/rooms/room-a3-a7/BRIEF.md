# Brief

These packs encode decisions from this policy. Using the graph format this tool provides,
declare the relationships the policy states between these decisions; the graph must validate
against these packs. For any policy sentence relating these decisions that you cannot represent
as a declared relationship, record the sentence verbatim with what you did instead. You may not
modify the packs.

Standing rules:
- Work only inside this directory; read only the files in it. Do not access the network, any
  repository, or any file outside this directory.
- The tool is at `bin/jpack`. Its `--help` texts and `bin/jpack experimental graph schema`
  describe the graph format. The project configuration is `jpack.json`; you may read it and
  must not modify it.
- Deliverables, in this directory: `relationships.graph.json` (the graph document; it must
  pass `bin/jpack experimental graph validate relationships.graph.json --config jpack.json`)
  and `RESIDUE.md` (the verbatim sentences you could not represent, each with what you did
  instead). If the policy states no relationship between these decisions, a graph with no
  edges plus a RESIDUE.md saying so is a valid deliverable.
