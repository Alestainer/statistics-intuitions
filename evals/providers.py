"""Model access via OpenRouter — one key, one endpoint, every model.

    export OPENROUTER_API_KEY=...

Model ids are OpenRouter's. Verify any you add against
https://openrouter.ai/api/v1/models — that endpoint needs no auth, and
`input_modalities` must include "image" for these tasks.
"""
import base64
import json
import os
import urllib.request

BASE_URL = "https://openrouter.ai/api/v1"
TIMEOUT = 180

# Short name -> OpenRouter model id. All confirmed vision-capable.
MODELS = {
    "gpt":    "openai/gpt-5",
    "claude": "anthropic/claude-sonnet-5",
    "gemini": "google/gemini-2.5-pro",
    "kimi":   "moonshotai/kimi-k3",
    "qwen":   "qwen/qwen3-vl-235b-a22b-instruct",
}


def _b64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def ask(model_id, image_path, question):
    """One image, one question, one reply. Raises on transport errors."""
    payload = {
        "model": model_id,
        "messages": [{"role": "user", "content": [
            {"type": "text", "text": question},
            {"type": "image_url",
             "image_url": {"url": f"data:image/png;base64,{_b64(image_path)}"}},
        ]}],
        "max_tokens": 300,
    }
    req = urllib.request.Request(
        f"{BASE_URL}/chat/completions",
        data=json.dumps(payload).encode(),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}",
            # OpenRouter uses these for attribution on its leaderboards.
            "HTTP-Referer": "https://alestainer.com",
            "X-Title": "Statistics Intuitions",
        })
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        d = json.loads(r.read().decode())
    if "choices" not in d:
        raise RuntimeError(str(d.get("error") or d)[:200])
    return d["choices"][0]["message"]["content"]


def available():
    """Every configured model, if the one key is set."""
    return list(MODELS) if os.environ.get("OPENROUTER_API_KEY") else []
