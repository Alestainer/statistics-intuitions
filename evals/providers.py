"""Model adapters. Each takes an image path plus a question and returns a raw
string answer. Adding a provider means adding one function and one env var.

Keys are read from the environment only. Nothing is written to disk.
"""
import base64
import json
import os
import urllib.request

TIMEOUT = 120


def _b64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def _post(url, payload, headers):
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", **headers})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        return json.loads(r.read().decode())


def _openai_compatible(model, image_path, question, *, base_url, api_key):
    """Works for OpenAI, Moonshot (Kimi) and Alibaba (Qwen) — all expose the
    same chat/completions shape."""
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": [
            {"type": "text", "text": question},
            {"type": "image_url",
             "image_url": {"url": f"data:image/png;base64,{_b64(image_path)}"}},
        ]}],
        "max_tokens": 300,
    }
    d = _post(f"{base_url}/chat/completions", payload,
              {"Authorization": f"Bearer {api_key}"})
    return d["choices"][0]["message"]["content"]


def openai(model, image_path, question):
    return _openai_compatible(model, image_path, question,
                              base_url="https://api.openai.com/v1",
                              api_key=os.environ["OPENAI_API_KEY"])


def kimi(model, image_path, question):
    return _openai_compatible(model, image_path, question,
                              base_url="https://api.moonshot.ai/v1",
                              api_key=os.environ["MOONSHOT_API_KEY"])


def qwen(model, image_path, question):
    return _openai_compatible(
        model, image_path, question,
        base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
        api_key=os.environ["DASHSCOPE_API_KEY"])


def anthropic(model, image_path, question):
    payload = {
        "model": model, "max_tokens": 300,
        "messages": [{"role": "user", "content": [
            {"type": "text", "text": question},
            {"type": "image", "source": {"type": "base64",
                                         "media_type": "image/png",
                                         "data": _b64(image_path)}},
        ]}],
    }
    d = _post("https://api.anthropic.com/v1/messages", payload,
              {"x-api-key": os.environ["ANTHROPIC_API_KEY"],
               "anthropic-version": "2023-06-01"})
    return "".join(b.get("text", "") for b in d["content"])


def gemini(model, image_path, question):
    key = os.environ["GEMINI_API_KEY"]
    payload = {"contents": [{"parts": [
        {"text": question},
        {"inline_data": {"mime_type": "image/png", "data": _b64(image_path)}},
    ]}], "generationConfig": {"maxOutputTokens": 300}}
    d = _post(
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}",
        payload, {})
    return "".join(p.get("text", "")
                   for p in d["candidates"][0]["content"]["parts"])


# name -> (adapter, default model id, env var it needs)
REGISTRY = {
    "gpt":    (openai,    "gpt-5",                  "OPENAI_API_KEY"),
    "claude": (anthropic, "claude-sonnet-5",        "ANTHROPIC_API_KEY"),
    "gemini": (gemini,    "gemini-2.5-pro",         "GEMINI_API_KEY"),
    "kimi":   (kimi,      "moonshot-v1-32k-vision-preview", "MOONSHOT_API_KEY"),
    "qwen":   (qwen,      "qwen-vl-max",            "DASHSCOPE_API_KEY"),
}


def available():
    return [n for n, (_, _, env) in REGISTRY.items() if os.environ.get(env)]
