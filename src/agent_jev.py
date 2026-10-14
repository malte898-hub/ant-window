"""Jev forager. 00g default: sample P. 00j: argmax(P) then host coin. Never print the key."""
from __future__ import annotations
import json
import random
from jev_client import jev_choice


class JevAgent:
    def __init__(self, rng, argmax=False, coin_eps=0.0, cell_seed=0):
        self.rng = rng
        self.argmax_mode = bool(argmax)
        self.coin_eps = float(coin_eps or 0.0)
        self.cell_seed = int(cell_seed or 0)
        self.n_ok = 0
        self.n_fail = 0
        self.n_wait = 0
        self.n_skip_one = 0
        self.n_coin = 0
        self.models = []
        self.decisions = []

    def note(self, route_label, n_ticks):
        text = "returned from %s after %s ticks" % (route_label, n_ticks)
        return text, "template"

    def _coin_rng(self, agent_id, tick):
        s = (self.cell_seed * 1000003 + int(agent_id) * 9176 + int(tick) * 13) & 0xFFFFFFFF
        return random.Random(s)

    def choose(self, open_routes, trail, label_map, agent_id=0, tick=0):
        if len(open_routes) == 1:
            self.n_skip_one += 1
            rec = {
                "ok": True,
                "skipped_one_route": True,
                "coin_fired": 0,
                "route": open_routes[0],
                "marks": [],
                "weights": [],
                "probabilities": None,
                "choice": open_routes[0],
                "model": None,
            }
            self.decisions.append(rec)
            return open_routes[0], rec

        if self.coin_eps > 0:
            cr = self._coin_rng(agent_id, tick)
            if cr.random() < self.coin_eps:
                route = cr.choice(list(open_routes))
                self.n_coin += 1
                rec = {
                    "ok": True,
                    "skipped_one_route": False,
                    "coin_fired": 1,
                    "route": route,
                    "marks": [label_map[e["route"]] for e in trail.read_set()],
                    "weights": [float(e["weight"]) for e in trail.read_set()],
                    "probabilities": None,
                    "sampled": label_map[route],
                    "model": "coin",
                    "error": None,
                }
                self.decisions.append(rec)
                return route, rec

        read = trail.read_set()
        marks = [label_map[e["route"]] for e in read]
        weights = [float(e["weight"]) for e in read]
        labs = [label_map[r] for r in open_routes]
        order = list(labs)
        self.rng.shuffle(order)
        criteria = {}
        for lab in order:
            criteria[lab] = "route %s" % lab
        state = json.dumps({"marks_strongest_first": marks})
        r = jev_choice(state, "Which route should this ant take next?", criteria, retries=2)
        rec = {
            "ok": bool(r.get("ok")),
            "skipped_one_route": False,
            "coin_fired": 0,
            "marks": marks,
            "weights": weights,
            "order": order,
            "probabilities": r.get("probabilities"),
            "choice_argmax": r.get("choice"),
            "model": r.get("model"),
            "error": r.get("error"),
            "confidence": r.get("confidence"),
        }
        probs = r.get("probabilities") or {}
        if not r.get("ok") or not probs:
            self.n_fail += 1
            self.n_wait += 1
            rec["route"] = None
            self.decisions.append(rec)
            return None, rec

        if self.argmax_mode:
            chosen_lab = max(probs, key=lambda k: float(probs.get(k) or 0.0))
        else:
            mass = []
            for lab in order:
                try:
                    mass.append(float(probs.get(lab) or 0.0))
                except (TypeError, ValueError):
                    mass.append(0.0)
            s = sum(mass)
            if s <= 0:
                self.n_fail += 1
                self.n_wait += 1
                rec["route"] = None
                rec["error"] = "zero_mass"
                self.decisions.append(rec)
                return None, rec
            u = self.rng.random() * s
            acc = 0.0
            chosen_lab = order[-1]
            for lab, w in zip(order, mass):
                acc += w
                if u <= acc:
                    chosen_lab = lab
                    break

        route = None
        for rname, lab in label_map.items():
            if lab == chosen_lab:
                route = rname
                break
        if route is None:
            self.n_fail += 1
            self.n_wait += 1
            rec["route"] = None
            rec["error"] = "unmapped_label"
            self.decisions.append(rec)
            return None, rec
        self.n_ok += 1
        if r.get("model"):
            self.models.append(r["model"])
        rec["route"] = route
        rec["sampled"] = chosen_lab
        rec["p_sampled"] = float(probs.get(chosen_lab) or 0.0)
        self.decisions.append(rec)
        return route, rec
