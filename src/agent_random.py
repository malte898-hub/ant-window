"""Uniform random forager. v1.3."""


class RandomAgent:
    def __init__(self, rng):
        self.rng = rng

    def choose(self, open_routes, trail):
        return self.rng.choice(open_routes)

    def note(self, route_label, n_ticks):
        text = "returned from %s after %s ticks" % (route_label, n_ticks)
        return text, "template"
