"""Deneubourg stochastic forager. v1.3."""


class AntAgent:
    def __init__(self, rng, k=20, n=2):
        self.rng = rng
        self.k = k
        self.n = n

    def choose(self, open_routes, trail):
        if len(open_routes) == 1:
            return open_routes[0]
        weights = []
        for r in open_routes:
            tau = trail.total_weight(r)
            weights.append((self.k + tau) ** self.n)
        total = sum(weights)
        u = self.rng.random() * total
        acc = 0.0
        for r, w in zip(open_routes, weights):
            acc += w
            if u <= acc:
                return r
        return open_routes[-1]

    def note(self, route_label, n_ticks):
        text = "returned from %s after %s ticks" % (route_label, n_ticks)
        return text, "template"
