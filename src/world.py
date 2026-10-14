"""Bridge world, tick clock, return scheduling. v1.3."""
import random


class Forager:
    def __init__(self, fid):
        self.id = fid
        self.idle = True
        self.return_tick = None
        self.route = None
        self.read_ids = []
        self.depart_tick = None


class World:
    def __init__(self, n_agents, n_ticks, L_short, L_long, T_open, seed, variant):
        self.n_agents = n_agents
        self.n_ticks = n_ticks
        self.L = {"short": L_short, "long": L_long}
        self.T_open = T_open
        self.variant = variant
        self.rng = random.Random(seed)
        self.foragers = [Forager(i) for i in range(n_agents)]
        # public labels shuffled per seed
        names = ["route_A", "route_B"]
        self.rng.shuffle(names)
        self.label = {"short": names[0], "long": names[1]}
        self.internal = {names[0]: "short", names[1]: "long"}

    def open_routes(self, t):
        if self.variant == "A":
            return ["short", "long"]
        if t >= self.T_open:
            return ["short", "long"]
        return ["long"]

    def round_trip(self, route):
        return 2 * self.L[route]
