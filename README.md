# Stanford G-set Max-Cut: Proof-Carrying Incumbent Release

This repository is a **proof-carrying incumbent release** for five canonical unweighted
instances of the maximum-cut problem (Max-Cut) from the Stanford G-set benchmark suite.
For each instance it publishes the graph, a binary witness vector encoding a vertex
bipartition, SHA-256 checksums binding both artifacts, and a self-contained verifier that
recomputes the cut value from the graph file alone. No solver code, search heuristic, or
algorithmic methodology is included: the release carries **results as verifiable evidence**,
not as claims.

## What this repository certifies — and what it does not

For every instance, the verifier establishes, unconditionally and by direct recomputation:

1. the published graph file matches its SHA-256 checksum recorded in `manifest.json`;
2. the published witness is exactly `n` bytes, each strictly `0x00` or `0x01`;
3. the graph is well-formed (declared `n`, `m` consistent, no self-loops, vertices in range);
4. the cut value `Cut(s) = |{(u,v) ∈ E : s_u ≠ s_v}|` of the witness equals the claimed value.

A witness that passes these checks constitutes a **certified feasible solution**, i.e. a
machine-checkable **lower bound** on the (unknown) optimum: `OPT(G) ≥ Cut(s)`.

The repository **does not** certify global optimality. A proof of optimality for Max-Cut
requires an upper-bound argument (e.g. an SDP relaxation à la Goemans–Williamson solved to
tolerance, or exhaustive enumeration), which is outside the scope of this release. Where a
witness achieves a value equal to the best published incumbent, the correct statement is
"matches the best known value", not "optimal".

## Cohort

| Instance | n | m | Claimed cut | Status | Reference |
|----------|-----|-------|-------------|-----------------------------------------------|-----------|
| G1  | 800  | 19176 | **11624** | matches published best known | 11624 |
| G2  | 800  | 19176 | **11620** | matches published best known | 11620 |
| G3  | 800  | 19176 | **11622** | matches published best known | 11622 |
| G14 | 800  | 4694  | **3064**  | matches published best known | 3064 |
| G22 | 2000 | 19990 | **13359** | matches published best known | 13359 |

The cohort is restricted to **unweighted** G-set instances. The G22 witness achieves a cut
of 13359, which matches the established modern best known solution (BKS) of the literature
(e.g. Benlic & Hao, 2013). As for every other instance in this release, the witness is
certified feasible by the verifier shipped here (a genuine cut of the stated value), while
its optimality remains open until an upper bound meets it.

## Repository layout

```
instances/<ID>/graph.edgelist   # canonical graph: first line "n m", then one "u v w" per edge (1-based)
instances/<ID>/graph.sha256     # SHA-256 of graph.edgelist
witnesses/<ID>/cut.bin          # witness vector: exactly n bytes, each 0x00 or 0x01
witnesses/<ID>/cut.sha256       # SHA-256 of cut.bin
witnesses/<ID>/certificate.json # per-instance metadata (schema pc-maxcut-certificate-v1)
manifest.json                   # canonical manifest (schema pc-maxcut-manifest-v1)
verify_maxcut.py                # autonomous verifier, pure Python 3.8+ stdlib
```

## Reproducibility

The verifier has no dependencies beyond the Python 3.8+ standard library and runs in well
under a second on commodity hardware:

```console
$ python3 verify_maxcut.py
[PASS] G1: n=800, m=19176, cut=11624 (matches_published_best_known) in 20.4 ms
[PASS] G2: n=800, m=19176, cut=11620 (matches_published_best_known) in 22.8 ms
[PASS] G3: n=800, m=19176, cut=11622 (matches_published_best_known) in 18.4 ms
[PASS] G14: n=800, m=4694, cut=3064 (matches_published_best_known) in 5.0 ms
[PASS] G22: n=2000, m=19990, cut=13359 (matches_published_best_known) in 17.4 ms
Total: 84.1 ms
$ echo $?
0
```

(Timings are machine-dependent; the pass/fail outcome and exit code are not.)

An adversarial self-test suite demonstrates that the verifier rejects tampered inputs
deterministically: truncated or wrong-length witnesses, out-of-domain bytes (0x02 or ASCII
'0'), manifest checksum forgeries, inflated claimed cut values, single-bit witness flips
(which necessarily change the recomputed cut), self-loops, and edge-count inconsistencies:

```console
$ python3 verify_maxcut.py --negative-tests
... every attack reports "[PASS] rejected ..." ...
$ echo $?
0
```

The verifier exits `0` if and only if every check passes (`--negative-tests` additionally
requires every synthetic attack to be rejected), making it directly usable in CI.

## Data provenance

Graph files are the standard G-set instances distributed by the research community
(originating with the Stanford repository; see Ye (2001) below) in the DIMACS-style
edgelist encoding: header `n m` followed by `u v w` triples. Witness vectors were produced
by the author's optimization stack; their provenance is irrelevant to their validity, which
rests entirely on the recomputation performed by `verify_maxcut.py`.

## References

- U. Benlic, J.-K. Hao. *Breakout local search for the Max-Cut problem.* Engineering
  Applications of Artificial Intelligence 26(3):1162–1173, 2013. (Modern best-known values
  for the G-set, incl. 13359 for G22.)
- M. X. Goemans, D. P. Williamson. *Improved approximation algorithms for maximum cut and
  satisfiability problems using semidefinite programming.* Journal of the ACM 42(6):1115–1145, 1995.
- Y. Ye. *A .699-approximation algorithm for Max-Bisection.* Mathematical Programming
  90(1):101–111, 2001. (Author's archive hosting the G-set benchmark suite:
  https://web.stanford.edu/~yyye/yyye/Gset/)
- Stanford G-set repository: https://web.stanford.edu/~yyye/yyye/Gset/
- For annealing-based Max-Cut studies on the G-set, see e.g. the benchmark tables maintained
  by D-Wave Systems (https://docs.dwavequantum.com/).

## Author and license

Prepared by **Aleksandr Grebeshok** (2026). Released under the MIT License; see `LICENSE`.
Citation metadata is available in `CITATION.cff`.
