"""Jev HTTP client. Bearer token from environment API_KEY only. Never print the key."""
from __future__ import annotations
import json, os, time, urllib.error, urllib.request

API = "https://api.typesafe.ai/v1/systemone"


def load_key():
    k = os.environ.get("API_KEY")
    if k:
        return k.strip()
    raise RuntimeError("API_KEY missing from environment")


def jev_choice(state, instructions, criteria, timeout=60, retries=1):
    key = load_key()
    body = {
        "model": "jev-latest",
        "state": state,
        "questions": {
            "route": {
                "type": "choice",
                "instructions": instructions,
                "criteria": criteria,
            }
        },
    }
    last = None
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(
                API,
                data=json.dumps(body).encode(),
                headers={
                    "Content-Type": "application/json",
                    "Authorization": "Bearer " + key,
                },
            )
            t0 = time.time()
            raw = urllib.request.urlopen(req, timeout=timeout).read()
            dt = time.time() - t0
            data = json.loads(raw)
            ans = ((data.get("answers") or {}).get("route") or {})
            probs = ans.get("probabilities") or {}
            return {
                "ok": True,
                "model": data.get("model"),
                "choice": ans.get("choice"),
                "probabilities": probs,
                "confidence": ans.get("confidence"),
                "dt": dt,
                "usage": data.get("usage") or {},
            }
        except urllib.error.HTTPError as e:
            last = e
            ra = e.headers.get("Retry-After") if e.headers else None
            wait = float(ra) if ra else (0.8 * (attempt + 1))
            if e.code in (429, 529):
                time.sleep(min(wait, 20))
            else:
                time.sleep(0.4 * (attempt + 1))
        except Exception as e:
            last = e
            time.sleep(0.4 * (attempt + 1))
    err = type(last).__name__ if last is not None else "error"
    code = getattr(last, "code", None)
    return {"ok": False, "error": err, "http": code, "dt": None}
