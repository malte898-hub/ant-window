"""Decaying shared trail (in-memory). v1.3."""
import math


class Trail:
    def __init__(self, ttl, weight_drop=0.05, top_k=7):
        self.ttl = ttl  # None => inf
        self.weight_drop = weight_drop
        self.top_k = top_k
        self.entries = []  # dicts
        self._next_id = 1

    def decay(self):
        if self.ttl is None:
            return
        factor = math.exp(-1.0 / float(self.ttl))
        kept = []
        for e in self.entries:
            e["weight"] *= factor
            if e["weight"] >= self.weight_drop:
                kept.append(e)
        self.entries = kept

    def total_weight(self, route):
        return sum(e["weight"] for e in self.entries if e["route"] == route)

    def read_set(self, k=None):
        k = self.top_k if k is None else k
        ranked = sorted(self.entries, key=lambda e: (-e["weight"], -e["created_tick"]))
        if k != "all":
            ranked = ranked[: int(k)]
        return ranked

    def deposit(self, route, text, tick, author, trip_ticks, source):
        e = {
            "id": self._next_id,
            "route": route,
            "text": text,
            "weight": 1.0,
            "created_tick": tick,
            "last_reinforced_tick": tick,
            "author": author,
            "trip_ticks": trip_ticks,
            "source": source,
        }
        self._next_id += 1
        self.entries.append(e)
        return e

    def reinforce(self, entry_ids, route, tick):
        """+1.0 split across read-set entries on the route taken. Returns reinforced ids."""
        targets = [e for e in self.entries if e["id"] in entry_ids and e["route"] == route]
        if not targets:
            return []
        share = 1.0 / len(targets)
        ids = []
        for e in targets:
            e["weight"] += share
            e["last_reinforced_tick"] = tick
            ids.append(e["id"])
        return ids

    def snapshot(self):
        return [dict(e) for e in self.entries]
