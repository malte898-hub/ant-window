"""LLM forager. Two calls per trip. v1.4 smoke."""
import json
import re
import urllib.request

JSON_OBJ = re.compile(r"\{.*\}", re.DOTALL)


def _extract_json(text):
    if not text:
        return None
    m = JSON_OBJ.search(text)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except ValueError:
        return None


class LLMAgent:
    def __init__(self, rng, base_url, model, depart_prompt, return_prompt, timeout=30):
        self.rng = rng
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.depart_prompt = depart_prompt
        self.return_prompt = return_prompt
        self.timeout = timeout
        self.parse_fail_depart = 0
        self.parse_fail_return = 0
        self.n_depart = 0
        self.n_return = 0
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.n_first_listed = 0
        self.backend = "openai"
        self.ollama_model = None

    def complete_ollama(self, user_text):
        from model_select import ollama_chat
        r = ollama_chat(self.ollama_model, user_text, temperature=0.7, num_predict=40, think=False)
        content = r.get("content") or ""
        pt = int(r.get("prompt_eval_count") or 0)
        ct = int(r.get("eval_count") or 0)
        self.prompt_tokens += pt
        self.completion_tokens += ct
        return content, pt, ct

    def complete(self, user_text):
        if self.backend == "ollama":
            return self.complete_ollama(user_text)
        url = self.base_url + "/chat/completions"
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": user_text}],
            "max_tokens": 40,
            "temperature": 0.7,
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json", "Authorization": "Bearer not-needed"},
        )
        raw = urllib.request.urlopen(req, timeout=self.timeout).read()
        data = json.loads(raw)
        msg = data["choices"][0]["message"]
        content = msg.get("content") or ""
        usage = data.get("usage") or {}
        pt = int(usage.get("prompt_tokens") or 0)
        ct = int(usage.get("completion_tokens") or 0)
        self.prompt_tokens += pt
        self.completion_tokens += ct
        print("llm_ok pt=%s ct=%s chars=%s" % (pt, ct, len(content)), flush=True)
        return content, pt, ct

    def choose(self, open_routes, trail, labels, open_labels):
        self.n_depart += 1
        read = trail.read_set()
        lines = []
        for e in read:
            lab = labels[e["route"]]
            if getattr(self, "show_weights", False):
                lines.append("- %s (w=%.3f): %s" % (lab, e.get("weight", 0.0), e["text"]))
            else:
                lines.append("- %s: %s" % (lab, e["text"]))
        trail_txt = "\n".join(lines) if lines else "(none)"
        shuffled = list(open_labels)
        self.rng.shuffle(shuffled)
        first = shuffled[0] if shuffled else None
        prompt = (
            self.depart_prompt.replace("{routes_shuffled}", ", ".join(shuffled))
            .replace("{routes}", ", ".join(shuffled))
            .replace("{trail}", trail_txt)
        )
        content, pt, ct = self.complete(prompt)
        obj = _extract_json(content)
        if obj is None or "route" not in obj:
            content, pt, ct = self.complete(prompt)
            obj = _extract_json(content)
        label_to_internal = {labels[r]: r for r in open_routes}
        if obj and obj.get("route") in label_to_internal:
            if obj.get("route") == first:
                self.n_first_listed += 1
            return label_to_internal[obj["route"]], pt, ct, 0
        self.parse_fail_depart += 1
        return self.rng.choice(open_routes), pt, ct, 1

    def note(self, route_label, n_ticks):
        self.n_return += 1
        prompt = self.return_prompt.replace("{route}", route_label).replace("{N}", str(n_ticks))
        content, pt, ct = self.complete(prompt)
        obj = _extract_json(content)
        if obj is None or "note" not in obj:
            content, pt, ct = self.complete(prompt)
            obj = _extract_json(content)
        if obj and obj.get("note"):
            text = str(obj["note"]).strip()
            words = text.split()
            if len(words) > 20:
                text = " ".join(words[:20])
            if not hasattr(self, "notes_llm"):
                self.notes_llm = []
            self.notes_llm.append(text)
            return text, "llm", pt, ct, 0
        self.parse_fail_return += 1
        text = "returned from %s after %s ticks" % (route_label, n_ticks)
        return text, "template", pt, ct, 1
