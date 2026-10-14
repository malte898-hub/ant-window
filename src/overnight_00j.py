"""calib-00j Part B. HITL GO 00j. Z5 → Jev coin 0.30 → Jev coin 0.10. Llama dropped. v4.0.1."""
from __future__ import annotations
import csv, json, os, shutil, sys, time, traceback
from concurrent.futures import ProcessPoolExecutor, as_completed
from run import run_cell

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "out", "calib-00j")
DROP = os.path.join(ROOT, "out_drop")
CSV_NAME = "grid.csv"
SEEDS = list(range(500, 512))
WIDE = 4
CAP_H = 3.0
CHECKER = os.path.join(os.path.dirname(ROOT), "checkers", "verify_calib00j.py")

CFG = {
    "n_agents": 30,
    "n_ticks": 200,
    "L_short": 2,
    "L_long": 4,
    "T_open": 40,
    "k_deneubourg": 20,
    "n_deneubourg": 2,
    "top_k": 7,
    "weight_drop": 0.05,
}

CSV_FIELDS = [
    "block", "agent", "noise", "variant", "ttl", "seed", "mapping",
    "frac_short_last50", "re_decided", "converged", "lock_in",
    "invalid", "api_error_rate", "parse_fail_rate_depart", "parse_fail_rate_return",
    "model_id", "n_depart_calls", "n_coin", "wall_clock_s",
    "label_short", "label_long", "cell",
]


def drops():
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(DROP, exist_ok=True)
    return [DROP]


def log(msg):
    print(msg, flush=True)
    os.makedirs(OUT, exist_ok=True)
    p = os.path.join(OUT, "overnight.log")
    with open(p, "a") as fh:
        fh.write(msg + "\n")
    for d in drops():
        try:
            shutil.copy2(p, os.path.join(d, "overnight.log"))
        except OSError:
            pass


def cell_name(variant, ttl, seed, agent, noise):
    if agent == "ant":
        return "ant_%s_ttl%s_s%s" % (variant, ttl, seed)
    return "jev_eps%s_%s_ttl%s_s%s" % (noise, variant, ttl, seed)


def dest_for(name):
    return os.path.join(OUT, name)


def jobs_all():
    out = []
    for seed in SEEDS:
        for variant, ttl in (("A", "2.5"), ("B", "2.5"), ("B", "3")):
            j = {"block": "Z5", "variant": variant, "ttl": ttl, "seed": seed, "agent": "ant", "noise": ""}
            j["name"] = cell_name(variant, ttl, seed, "ant", "")
            out.append(j)
    for seed in SEEDS:
        for variant, ttl in (("A", "2.5"), ("B", "2.5"), ("B", "3")):
            j = {"block": "J30", "variant": variant, "ttl": ttl, "seed": seed, "agent": "jev", "noise": 0.30}
            j["name"] = cell_name(variant, ttl, seed, "jev", "0.30")
            out.append(j)
    for seed in SEEDS:
        for variant, ttl in (("B", "2.5"), ("B", "3")):
            j = {"block": "J10", "variant": variant, "ttl": ttl, "seed": seed, "agent": "jev", "noise": 0.10}
            j["name"] = cell_name(variant, ttl, seed, "jev", "0.10")
            out.append(j)
    return out


def run_one(job):
    name = job["name"]
    dest = dest_for(name)
    os.makedirs(dest, exist_ok=True)
    metrics_path = os.path.join(dest, "metrics.json")
    if os.path.exists(metrics_path):
        m = json.load(open(metrics_path))
        return {"name": name, "metrics": m, "wall": m.get("wall_clock_s") or 0, "skipped": True, "job": job}
    cfg = dict(CFG)
    if job["agent"] == "jev":
        cfg["jev_argmax"] = True
        cfg["coin_eps"] = float(job["noise"])
    t0 = time.time()
    m = run_cell(cfg, job["variant"], job["agent"], job["ttl"], job["seed"], dest, n_agents=30, top_k=7, n_ticks=200)
    wall = time.time() - t0
    m["wall_clock_s"] = wall
    m["block"] = job["block"]
    m["noise"] = job["noise"]
    with open(metrics_path, "w") as fh:
        json.dump(m, fh, indent=2)
    return {"name": name, "metrics": m, "wall": wall, "skipped": False, "job": job}


def slim_row(job, m, wall, name):
    return {
        "block": job["block"], "agent": job["agent"], "noise": job["noise"],
        "variant": job["variant"], "ttl": job["ttl"], "seed": job["seed"],
        "mapping": m.get("mapping"),
        "frac_short_last50": m.get("frac_short_last50"), "re_decided": m.get("re_decided"),
        "converged": m.get("converged"), "lock_in": m.get("lock_in"),
        "invalid": m.get("invalid"), "api_error_rate": m.get("api_error_rate"),
        "parse_fail_rate_depart": m.get("parse_fail_rate_depart"),
        "parse_fail_rate_return": m.get("parse_fail_rate_return"),
        "model_id": m.get("model_id"), "n_depart_calls": m.get("n_depart_calls"),
        "n_coin": m.get("n_coin"), "wall_clock_s": wall,
        "label_short": m.get("label_short"), "label_long": m.get("label_long"), "cell": name,
    }


def append_csv(row):
    path = os.path.join(OUT, CSV_NAME)
    exists = os.path.exists(path) and os.path.getsize(path) > 0
    with open(path, "a", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=CSV_FIELDS)
        if not exists:
            w.writeheader()
        w.writerow(row)
    for d in drops():
        try:
            shutil.copy2(path, os.path.join(d, CSV_NAME))
        except OSError:
            pass


def sync_cell(name):
    src = dest_for(name)
    for d in drops():
        dst = os.path.join(d, name)
        os.makedirs(dst, exist_ok=True)
        for fn in ("metrics.json", "decisions.csv"):
            mp = os.path.join(src, fn)
            if os.path.exists(mp):
                shutil.copy2(mp, os.path.join(dst, fn))


def record(res):
    job, name, m, wall = res["job"], res["name"], res["metrics"], res["wall"]
    append_csv(slim_row(job, m, wall, name))
    sync_cell(name)
    log("DONE %s last50=%s noise=%s n_coin=%s api_err=%s invalid=%s %.1fs skipped=%s" % (
        name, m.get("frac_short_last50"), job.get("noise"), m.get("n_coin"),
        m.get("api_error_rate"), m.get("invalid"), wall, res["skipped"]))


def csv_names():
    path = os.path.join(OUT, CSV_NAME)
    if not os.path.exists(path):
        return set()
    return {r.get("cell") for r in csv.DictReader(open(path))}


def write_stop(reason, extra=None):
    rec = {"stop": True, "reason": reason}
    if extra:
        rec.update(extra)
    json.dump(rec, open(os.path.join(OUT, "STOP.json"), "w"), indent=2)
    for d in drops():
        try:
            shutil.copy2(os.path.join(OUT, "STOP.json"), os.path.join(d, "STOP.json"))
        except OSError:
            pass
    log("STOP " + reason)


def ant_ok():
    rows = list(csv.DictReader(open(os.path.join(OUT, CSV_NAME)))) if os.path.exists(os.path.join(OUT, CSV_NAME)) else []
    def med(var, ttl):
        xs = [float(r["frac_short_last50"]) for r in rows
              if r.get("agent") == "ant" and r.get("variant") == var and str(r.get("ttl")) == str(ttl)
              and r.get("frac_short_last50") not in ("", None)]
        if not xs:
            return None, 0
        xs.sort()
        n = len(xs)
        m = xs[n // 2] if n % 2 else 0.5 * (xs[n // 2 - 1] + xs[n // 2])
        return m, n
    a, na = med("A", "2.5")
    b, nb = med("B", "2.5")
    c, nc = med("B", "3")
    rec = {"A25": a, "nA": na, "B25": b, "nB": nb, "B3": c, "nC": nc}
    ok = (na == 12 and nb == 12 and nc == 12 and a is not None and b is not None and c is not None
          and a >= 0.85 and b >= 0.85 and c <= 0.25)
    rec["ok"] = ok
    log("Z5 " + json.dumps(rec))
    return ok, rec


def run_pool(jobs, wide, label, t0):
    for j in jobs:
        mp = os.path.join(dest_for(j["name"]), "metrics.json")
        if os.path.exists(mp) and j["name"] not in csv_names():
            m = json.load(open(mp))
            record({"job": j, "name": j["name"], "metrics": m, "wall": m.get("wall_clock_s") or 0, "skipped": True})
    pending = [j for j in jobs if not os.path.exists(os.path.join(dest_for(j["name"]), "metrics.json"))]
    log("POOL %s n=%s pending=%s wide=%s" % (label, len(jobs), len(pending), wide))
    if not pending:
        return True
    with ProcessPoolExecutor(max_workers=wide) as ex:
        futs = {ex.submit(run_one, j): j for j in pending}
        for fut in as_completed(futs):
            j = futs[fut]
            if (time.time() - t0) / 3600.0 > CAP_H:
                write_stop("wall cap %sh" % CAP_H)
                return False
            try:
                res = fut.result()
            except Exception:
                log("FAIL %s\n%s" % (j["name"], traceback.format_exc()))
                write_stop("cell fail " + j["name"])
                return False
            if j["name"] not in csv_names():
                record(res)
            else:
                log("SKIP csv %s" % j["name"])
    return True


def run_checker():
    import subprocess
    grid = os.path.join(OUT, CSV_NAME)
    outp = os.path.join(OUT, "VERIFY.md")
    cmd = [sys.executable, "-I", CHECKER, grid, "--out", outp]
    r = subprocess.run(cmd, capture_output=True, text=True)
    log("CHECKER rc=%s\n%s" % (r.returncode, (r.stdout or "")[-2500:]))
    if r.stderr:
        log("CHECKER_ERR " + r.stderr[-500:])
    for d in drops():
        if os.path.exists(outp):
            try:
                shutil.copy2(outp, os.path.join(d, "VERIFY.md"))
                shutil.copy2(grid, os.path.join(d, CSV_NAME))
            except OSError:
                pass


def main():
    drops()
    t0 = time.time()
    log("START calib-00j HITL GO 00j. v4.0.1. Z5 → Jev argmax+coin 0.30 → 0.10. llama DROP. seeds 500-511. 4-wide. 3h cap.")
    allj = jobs_all()
    z = [j for j in allj if j["agent"] == "ant"]
    j30 = [j for j in allj if j["block"] == "J30"]
    j10 = [j for j in allj if j["block"] == "J10"]
    if not run_pool(z, WIDE, "Z5", t0):
        return 2
    ok, rec = ant_ok()
    json.dump(rec, open(os.path.join(OUT, "z5.json"), "w"), indent=2)
    for d in drops():
        try:
            shutil.copy2(os.path.join(OUT, "z5.json"), os.path.join(d, "z5.json"))
        except OSError:
            pass
    if not ok:
        write_stop("Z5 ants missed VALID medians", {"z5": rec})
        return 2
    if not run_pool(j30, WIDE, "J30", t0):
        return 2
    if not run_pool(j10, WIDE, "J10", t0):
        return 2
    run_checker()
    open(os.path.join(OUT, "ALL_DONE"), "w").write("ok\n")
    for d in drops():
        try:
            shutil.copy2(os.path.join(OUT, "ALL_DONE"), os.path.join(d, "ALL_DONE"))
        except OSError:
            pass
    log("ALL DONE wall_h=%.2f" % ((time.time() - t0) / 3600.0))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
