#!/usr/bin/env python3
"""Autonomous verifier for the Proof-Carrying Incumbent Release (Stanford G-set, Max-Cut).
Pure Python 3.8+ stdlib. Exit 0 = all checks pass, 1 = failure. --negative-tests runs the adversarial suite."""
import hashlib, json, sys, time

GREEN, RED, OFF = "\033[32m", "\033[31m", "\033[0m"
def reject(msg): raise AssertionError(msg)
def sha256(data): return hashlib.sha256(data).hexdigest()

def parse_graph(text):
    lines = text.splitlines()
    n, m = (int(x) for x in lines[0].split()[:2])
    edges, zero_based = [], False
    for line in filter(str.strip, lines[1:]):
        u, v = (int(x) for x in line.split()[:2])
        if u == v:
            reject("self-loop edge (%d, %d)" % (u, v))
        zero_based |= (u == 0 or v == 0)
        edges.append((u, v))
    if len(edges) != m:
        reject("edge count %d != declared m=%d" % (len(edges), m))
    lo, hi = (0, n - 1) if zero_based else (1, n)
    if any(not (lo <= u <= hi and lo <= v <= hi) for u, v in edges):
        reject("vertex out of range")
    return n, m, edges, zero_based

def cut_value(edges, vec, off): return sum(1 for u, v in edges if vec[u - off] != vec[v - off])

def verify_instance(graph_b, wit_b, meta):
    if sha256(graph_b) != meta["graph_sha256"]:
        reject("graph SHA-256 mismatch vs manifest")
    if sha256(wit_b) != meta["witness_sha256"]:
        reject("witness SHA-256 mismatch vs manifest")
    n, m, edges, zb = parse_graph(graph_b.decode())
    off = 0 if zb else 1
    if (n, m) != (meta["n"], meta["m"]):
        reject("graph header (%d,%d) != manifest n=%d, m=%d" % (n, m, meta["n"], meta["m"]))
    if len(wit_b) != n:
        reject("witness length %d != n=%d" % (len(wit_b), n))
    if not set(wit_b) <= {0, 1}:
        reject("witness byte outside {0x00, 0x01}")
    cut = cut_value(edges, wit_b, off)
    if cut_value(edges, bytes(b ^ 1 for b in wit_b), off) != cut:
        reject("inversion invariant Cut(s) != Cut(1-s)")
    if cut != meta["claimed_cut"]:
        reject("recomputed cut %d != claimed %d" % (cut, meta["claimed_cut"]))
    return cut

def negative_tests(manifest):
    g1 = next(i for i in manifest["instances"] if i["id"] == "G1")
    graph, wit = open(g1["graph"], "rb").read(), open(g1["witness"], "rb").read()
    resha = lambda g, w: dict(g1, graph_sha256=sha256(g), witness_sha256=sha256(w))
    junk, junk2, flip = (bytearray(wit) for _ in range(3))
    junk[0], junk2[0], flip[0] = 2, ord("0"), wit[0] ^ 1
    gl = graph.decode().splitlines()
    loop_g = "\n".join(gl[:1] + ["1 1 1"] + gl[2:]).encode()
    extra_g = ("\n".join(gl + ["2 3 1"]) + "\n").encode()
    attacks = [
        ("a truncated witness (len != n)", graph, wit[:-1], resha(graph, wit[:-1])),
        ("b garbage byte 0x02", graph, bytes(junk), resha(graph, bytes(junk))),
        ("b garbage byte ASCII '0'", graph, bytes(junk2), resha(graph, bytes(junk2))),
        ("c tampered graph SHA-256 in manifest", graph, wit, dict(g1, graph_sha256="0" * 64)),
        ("c tampered witness SHA-256 in manifest", graph, wit, dict(g1, witness_sha256="0" * 64)),
        ("d tampered claimed_cut (+1)", graph, wit, dict(g1, claimed_cut=g1["claimed_cut"] + 1)),
        ("e single bit flip in witness", graph, bytes(flip), resha(graph, bytes(flip))),
        ("f self-loop edge in graph", loop_g, wit, resha(loop_g, wit)),
        ("g extra edge beyond m", extra_g, wit, resha(extra_g, wit)),
    ]
    ok = True
    for name, gb, wb, meta in attacks:
        try:
            verify_instance(gb, wb, meta)
            ok = False
            print("%s[FAIL] ACCEPTED negative-test %s%s" % (RED, name, OFF))
        except Exception as exc:
            print("%s[PASS] rejected negative-test %s: %s%s" % (GREEN, name, exc, OFF))
    return ok

def main():
    with open("manifest.json") as fh:
        manifest = json.load(fh)
    t0, ok = time.perf_counter(), True
    for meta in manifest["instances"]:
        t = time.perf_counter()
        try:
            cut = verify_instance(open(meta["graph"], "rb").read(), open(meta["witness"], "rb").read(), meta)
            print("%s[PASS] %s: n=%d, m=%d, cut=%d (%s) in %.1f ms%s" % (GREEN, meta["id"], meta["n"],
                  meta["m"], cut, meta["status"], (time.perf_counter() - t) * 1e3, OFF))
        except Exception as exc:
            ok = False
            print("%s[FAIL] %s: %s%s" % (RED, meta["id"], exc, OFF))
    if "--negative-tests" in sys.argv:
        ok &= negative_tests(manifest)
    print("Total: %.1f ms" % ((time.perf_counter() - t0) * 1e3))
    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()
