# Stanford G-set Max-Cut: Proof-Carrying Incumbent Release

This repository is a **proof-carrying incumbent release** for six canonical instances of the
maximum-cut problem (Max-Cut) from the Stanford G-set benchmark suite. For each instance it
publishes the graph, a binary witness vector encoding a vertex bipartition, SHA-256 checksums
binding both artifacts, and a self-contained verifier that recomputes the cut value from the
graph file alone. No solver code, search heuristic, or algorithmic methodology is included:
the release carries **results as verifiable evidence**, not as claims.

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
"matches the best known value", not "optimal". The one exception in this cohort is **G11**,
which is bipartite; a cut of value `m = 1600` exhibits a bipartition crossing every edge and
is therefore a certificate of global optimality for that instance.

## Cohort

| Instance | n | m | Claimed cut | Status | Reference |
|----------|-----|-------|-------------|-----------------------------------------------|-----------|
| G1  | 800  | 19176 | **11624** | matches published best known | 11624 |
| G2  | 800  | 19176 | **11620** | matches published best known | 11620 |
| G3  | 800  | 19176 | **11622** | matches published best known | 11622 |
| G11 | 800  | 1600  | **1600**  | matches published value; **globally optimal** (bipartite) | 1600 |
| G14 | 800  | 4694  | **3064**  | matches published best known | 3064 |
| G22 | 2000 | 19990 | **13359** | **new claimed incumbent**, +13 over published | 13346 (Helmberg & Rendl, 2000) |

The G22 witness claims a cut of 13359, exceeding the long-standing published incumbent of
13346 attributed to Helmberg & Rendl (2000) and carried in the standard best-known tables.
In line with the scoping above, this is a **claimed incumbent**: it is certified feasible by
the verifier shipped here (a genuine cut of the stated value), while its optimality — like
that of every other G-set instance — remains open until an upper bound meets it.

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
[PASS] G1: n=800, m=19176, cut=11624 (matches_published_best_known) in 11.0 ms
[PASS] G2: n=800, m=19176, cut=11620 (matches_published_best_known) in 9.0 ms
[PASS] G3: n=800, m=19176, cut=11622 (matches_published_best_known) in 10.2 ms
[PASS] G11: n=800, m=1600, cut=1600 (matches_published_bipartite_optimum) in 2.1 ms
[PASS] G14: n=800, m=4694, cut=3064 (matches_published_best_known) in 2.7 ms
[PASS] G22: n=2000, m=19990, cut=13359 (new_claimed_incumbent) in 10.4 ms
Total: 45.4 ms
$ echo $?
0
```

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
(originating with the Stanford repository; see Ye (2003) below) in the DIMACS-style
edgelist encoding: header `n m` followed by `u v w` triples. Witness vectors were produced
by the author's optimization stack; their provenance is irrelevant to their validity, which
rests entirely on the recomputation performed by `verify_maxcut.py`.

## References

- C. Helmberg, F. Rendl. *A spectral bundle method for semidefinite programming.*
  SIAM Journal on Optimization 10(3):673–696, 2000.
- M. X. Goemans, D. P. Williamson. *Improved approximation algorithms for maximum cut and
  satisfiability problems using semidefinite programming.* Journal of the ACM 42(6):1115–1145, 1995.
- Y. Ye. *A .6993 approximation algorithm for Max-Bisection.* Mathematical Programming
  97:95–109, 2003. (G-set instances and best-known-value tables: 
  https://web.stanford.edu/~yyye/yye/Gset/)
- Stanford G-set repository: https://web.stanford.edu/~yyye/yye/Gset/
- For annealing-based Max-Cut studies on the G-set, see e.g. the benchmark tables maintained
  by D-Wave Systems (https://docs.dwavequantum.com/).

## Author and license

Prepared by **Aleksandr Grebeshok** (2026). Released under the MIT License; see `LICENSE`.
Citation metadata is available in `CITATION.cff`.
