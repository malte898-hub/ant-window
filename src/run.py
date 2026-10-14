"""Run one (variant, agent_type, ttl, n_agents, seed) cell. v1.4."""
import json
import os
import sqlite3

from trail import Trail
from world import World
from agent_ant import AntAgent
from agent_random import RandomAgent
from agent_llm import LLMAgent
from agent_jev import JevAgent

SNAPSHOT_TICKS = (50, 100, 150)


def parse_ttl(s):
    if s is None or str(s).lower() in ("inf", "none", "infinity"):
        return None
    return float(s)


def run_cell(cfg, variant, agent_type, ttl, seed, out_dir, n_agents=None, top_k=None, n_ticks=None):
    n_agents = cfg["n_agents"] if n_agents is None else n_agents
    top_k = cfg["top_k"] if top_k is None else top_k
    n_ticks = cfg["n_ticks"] if n_ticks is None else n_ticks
    ttl_val = parse_ttl(ttl)
    world = World(
        n_agents=n_agents,
        n_ticks=n_ticks,
        L_short=cfg["L_short"],
        L_long=cfg["L_long"],
        T_open=cfg["T_open"],
        seed=seed,
        variant=variant,
    )
    trail = Trail(ttl=ttl_val, weight_drop=cfg["weight_drop"], top_k=top_k)
    if agent_type == "ant":
        agent = AntAgent(world.rng, k=cfg["k_deneubourg"], n=cfg["n_deneubourg"])
    elif agent_type == "random":
        agent = RandomAgent(world.rng)
    elif agent_type == "llm":
        root = os.path.dirname(os.path.abspath(__file__))
        dep_name = cfg.get("depart_prompt", "depart.txt")
        ret_name = cfg.get("return_prompt", "return.txt")
        with open(os.path.join(root, "prompts", dep_name)) as fh:
            depart_p = fh.read()
        with open(os.path.join(root, "prompts", ret_name)) as fh:
            return_p = fh.read()
        agent = LLMAgent(
            world.rng,
            base_url=cfg.get("model_base_url") or "http://127.0.0.1:11434/v1",
            model=cfg.get("model_id") or "llama3.1:8b",
            depart_prompt=depart_p,
            return_prompt=return_p,
        )
        agent.backend = cfg.get("llm_backend") or "openai"
        agent.ollama_model = cfg.get("ollama_model") or cfg.get("model_id")
        agent.notes_llm = []
        agent.show_weights = bool(cfg.get("show_weights"))
        if cfg.get("neutral_tokens"):
            t0 = "rt-%03x" % world.rng.randrange(0x100, 0xFFF)
            t1 = "rt-%03x" % world.rng.randrange(0x100, 0xFFF)
            while t1 == t0:
                t1 = "rt-%03x" % world.rng.randrange(0x100, 0xFFF)
            if seed % 2 == 0:
                world.label = {"short": t0, "long": t1}
            else:
                world.label = {"short": t1, "long": t0}
            world.internal = {world.label["short"]: "short", world.label["long"]: "long"}
    elif agent_type == "jev":
        agent = JevAgent(
            world.rng,
            argmax=bool(cfg.get("jev_argmax")),
            coin_eps=float(cfg.get("coin_eps") or 0.0),
            cell_seed=seed,
        )
        t0 = "rt-%03x" % world.rng.randrange(0x100, 0xFFF)
        t1 = "rt-%03x" % world.rng.randrange(0x100, 0xFFF)
        while t1 == t0:
            t1 = "rt-%03x" % world.rng.randrange(0x100, 0xFFF)
        if seed % 2 == 0:
            world.label = {"short": t0, "long": t1}
        else:
            world.label = {"short": t1, "long": t0}
        world.internal = {world.label["short"]: "short", world.label["long"]: "long"}
    else:
        raise ValueError("unknown agent: %s" % agent_type)

    os.makedirs(out_dir, exist_ok=True)
    db_path = os.path.join(out_dir, "events.sqlite")
    if os.path.exists(db_path):
        os.remove(db_path)
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.executescript(
        """
        CREATE TABLE depart(
          tick INTEGER, agent_id INTEGER, agent_type TEXT, route TEXT,
          read_ids TEXT, prompt_tokens INTEGER, completion_tokens INTEGER, parse_fail INTEGER
        );
        CREATE TABLE ret(
          tick INTEGER, agent_id INTEGER, route TEXT, trip_ticks INTEGER,
          entry_id INTEGER, source TEXT, reinforced_ids TEXT,
          prompt_tokens INTEGER, completion_tokens INTEGER, parse_fail INTEGER
        );
        CREATE TABLE ticklog(
          tick INTEGER, open_routes TEXT, pheromone_short REAL, pheromone_long REAL, n_entries INTEGER
        );
        CREATE TABLE snapshot(tick INTEGER, entries TEXT);
        CREATE TABLE jev_decision(
          tick INTEGER, agent_id INTEGER, route TEXT, wait INTEGER,
          marks TEXT, weights TEXT, probabilities TEXT, sampled TEXT, model TEXT, error TEXT,
          coin INTEGER
        );
        """
    )

    trips_before_open = 0
    depart_short = []  # list of (tick, is_short)

    for t in range(n_ticks):
        # (1) decay
        trail.decay()
        # (2) returns
        for f in world.foragers:
            if f.idle or f.return_tick != t:
                continue
            route = f.route
            N = world.round_trip(route)
            label = world.label[route]
            if agent_type == "llm":
                text, source, pt, ct, pf = agent.note(label, N)
            else:
                text, source = agent.note(label, N)
                pt, ct, pf = 0, 0, 0
            entry = trail.deposit(route, text, t, f.id, N, source)
            reinforced = trail.reinforce(f.read_ids, route, t)
            if variant == "B" and t < cfg["T_open"]:
                trips_before_open += 1
            c.execute(
                "INSERT INTO ret VALUES (?,?,?,?,?,?,?,?,?,?)",
                (
                    t,
                    f.id,
                    route,
                    N,
                    entry["id"],
                    source,
                    json.dumps(reinforced),
                    pt,
                    ct,
                    pf,
                ),
            )
            f.idle = True
            f.route = None
            f.read_ids = []
            f.return_tick = None
            f.depart_tick = None
        # (3) departures
        open_routes = world.open_routes(t)
        for f in world.foragers:
            if not f.idle:
                continue
            read = trail.read_set()
            read_ids = [e["id"] for e in read]
            if agent_type == "llm":
                open_labels = [world.label[r] for r in open_routes]
                route, pt, ct, pf = agent.choose(
                    open_routes, trail, world.label, open_labels
                )
            elif agent_type == "jev":
                route, rec = agent.choose(open_routes, trail, world.label, agent_id=f.id, tick=t)
                pt, ct, pf = 0, 0, int(not rec.get("ok"))
                c.execute(
                    "INSERT INTO jev_decision VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                    (
                        t,
                        f.id,
                        rec.get("route"),
                        int(route is None),
                        json.dumps(rec.get("marks")),
                        json.dumps(rec.get("weights")),
                        json.dumps(rec.get("probabilities")),
                        rec.get("sampled"),
                        rec.get("model"),
                        rec.get("error"),
                        int(rec.get("coin_fired") or 0),
                    ),
                )
                if route is None:
                    continue
            else:
                route = agent.choose(open_routes, trail)
                pt, ct, pf = 0, 0, 0
            c.execute(
                "INSERT INTO depart VALUES (?,?,?,?,?,?,?,?)",
                (t, f.id, agent_type, route, json.dumps(read_ids), pt, ct, pf),
            )
            depart_short.append((t, 1 if route == "short" else 0))
            f.idle = False
            f.route = route
            f.read_ids = read_ids
            f.depart_tick = t
            f.return_tick = t + world.round_trip(route)
        # (4) log
        c.execute(
            "INSERT INTO ticklog VALUES (?,?,?,?,?)",
            (
                t,
                json.dumps(open_routes),
                trail.total_weight("short"),
                trail.total_weight("long"),
                len(trail.entries),
            ),
        )
        if t in SNAPSHOT_TICKS or t == n_ticks - 1:
            c.execute(
                "INSERT INTO snapshot VALUES (?,?)",
                (t, json.dumps(trail.snapshot())),
            )

    conn.commit()

    def window_frac(t0, t1):
        xs = [s for (tt, s) in depart_short if t0 <= tt <= t1]
        if not xs:
            return None
        return sum(xs) / float(len(xs))

    last50 = window_frac(max(0, n_ticks - 50), n_ticks - 1)
    drop = float(cfg.get("weight_drop", 0.05))
    if ttl_val is None:
        mlr = None
    elif drop <= 0:
        mlr = "inf"
    else:
        import math
        mlr = ttl_val * math.log(1.0 / drop) / 8.0
    if variant == "B" and last50 is not None:
        re_decided = last50 >= 0.8
        lock_in = last50 <= 0.2
        undecided = (not re_decided) and (not lock_in)
    else:
        re_decided = False
        lock_in = False
        undecided = False
    metrics = {
        "variant": variant,
        "agent": agent_type,
        "ttl": "inf" if ttl_val is None else ttl_val,
        "seed": seed,
        "n_agents": n_agents,
        "n_ticks": n_ticks,
        "n_departures": len(depart_short),
        "frac_short_last50": last50,
        "drop_threshold": drop,
        "memory_lifetime_ratio": mlr,
        "converged": bool(variant == "A" and last50 is not None and last50 >= 0.8),
        "re_decided": bool(re_decided),
        "lock_in": bool(lock_in),
        "undecided": bool(undecided),
        "trips_before_open": trips_before_open if variant == "B" else None,
        "frac_short_t0": window_frac(0, 0),
        "t_redecide": None,
        "label_short": world.label["short"],
        "label_long": world.label["long"],
        "mapping": "even" if seed % 2 == 0 else "odd",
        "db": db_path,
    }
    if variant == "B":
        t_redecide = None
        for tt in range(cfg["T_open"], n_ticks):
            wf = window_frac(max(0, tt - 49), tt)
            if wf is not None and wf >= 0.8:
                t_redecide = tt
                break
        metrics["t_redecide"] = t_redecide
        xs4060 = [s for (tt, s) in depart_short if 40 <= tt <= 60]
        metrics["novel_route_rate"] = (sum(xs4060) / float(len(xs4060))) if xs4060 else None
    if agent_type == "llm":
        nd = max(1, agent.n_depart)
        nr = max(1, agent.n_return)
        pd = agent.parse_fail_depart / float(nd)
        pr = agent.parse_fail_return / float(nr)
        notes = getattr(agent, "notes_llm", []) or []
        import re as _re
        dur = 0
        invented = 0
        inv_re = _re.compile(
            r"oak|stream|berry|berries|wasp|rabbit|garlic|fern|fungi|predator|"
            r"insect|rain|colou?r|\bred\b|\bgreen\b|thorn|clearing|slope|ginger|"
            r"dandelion|chamomile|mushroom|bird|nest|wall|path|forest|overgrowth|"
            r"patch|swarm",
            _re.I,
        )
        for nt in notes:
            if _re.search(r"\d+|tick", nt, _re.I):
                dur += 1
            if inv_re.search(nt):
                invented += 1
        tmpl = 0
        tot_ret = 0
        for src, in c.execute("select source from ret"):
            tot_ret += 1
            if src == "template":
                tmpl += 1
        from collections import defaultdict
        by_t = defaultdict(list)
        for tt, s in depart_short:
            by_t[tt].append(s)
        curve = [{"tick": t, "frac_short": sum(v) / float(len(v))} for t, v in sorted(by_t.items())]
        metrics.update(
            {
                "model_id": cfg.get("model_id"),
                "model_base_url": cfg.get("model_base_url"),
                "prompt_tokens": agent.prompt_tokens,
                "completion_tokens": agent.completion_tokens,
                "n_depart_calls": agent.n_depart,
                "n_return_calls": agent.n_return,
                "parse_fail_rate_depart": pd,
                "parse_fail_rate_return": pr,
                "invalid": bool(pd > 0.10 or pr > 0.10),
                "p_first_listed": agent.n_first_listed / float(nd),
                "note_diversity": (len(set(notes)) / float(len(notes))) if notes else None,
                "n_llm_notes": len(notes),
                "n_distinct_notes": len(set(notes)),
                "notes_mentioning_duration": (dur / float(len(notes))) if notes else None,
                "invented_content_rate": (invented / float(len(notes))) if notes else None,
                "template_fraction": (tmpl / float(tot_ret)) if tot_ret else None,
                "frac_short_last20": window_frac(max(0, n_ticks - 20), n_ticks - 1),
                "frac_short_curve": curve,
                "sample_notes": notes[:10],
            }
        )
    if agent_type == "jev":
        ncall = agent.n_ok + agent.n_fail
        api_err = (agent.n_fail / float(ncall)) if ncall else 0.0
        from collections import Counter
        mc = Counter(agent.models)
        model_s = mc.most_common(1)[0][0] if mc else None
        metrics.update(
            {
                "model_id": model_s,
                "api_error_rate": api_err,
                "n_jev_ok": agent.n_ok,
                "n_jev_fail": agent.n_fail,
                "n_jev_wait": agent.n_wait,
                "n_jev_skip_one": agent.n_skip_one,
                "n_coin": agent.n_coin,
                "coin_eps": float(cfg.get("coin_eps") or 0.0),
                "jev_argmax": bool(cfg.get("jev_argmax")),
                "invalid": bool(api_err > 0.10),
                "n_depart_calls": ncall,
            }
        )
        dpath = os.path.join(out_dir, "decisions.csv")
        ls = world.label["short"]
        ll = world.label["long"]
        with open(dpath, "w") as fh:
            fh.write("variant,ttl,seed,tick,agent_id,coin_fired,chosen,top7_n_short,top7_n_long\n")
            for tick, aid, route, marks, coin in c.execute(
                "SELECT tick, agent_id, route, marks, coin FROM jev_decision"
            ):
                chosen = ""
                if route in ("short", "long"):
                    chosen = route
                try:
                    labs = json.loads(marks) if marks else []
                except (TypeError, ValueError, json.JSONDecodeError):
                    labs = []
                nshort = sum(1 for x in labs if x == ls)
                nlong = sum(1 for x in labs if x == ll)
                fh.write(
                    "%s,%s,%s,%s,%s,%s,%s,%s,%s\n"
                    % (variant, ttl_val, seed, tick, aid, int(coin or 0), chosen, nshort, nlong)
                )
    metrics_path = os.path.join(out_dir, "metrics.json")
    tmp = metrics_path + ".tmp"
    with open(tmp, "w") as fh:
        json.dump(metrics, fh, indent=2)
    os.replace(tmp, metrics_path)
    conn.close()
    return metrics
