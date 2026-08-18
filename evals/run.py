#!/usr/bin/env python3
"""Run one intuition task against one or more models.

    python evals/run.py --task which-map-is-random --models gpt,claude --n 20

Needs the matching API key in the environment (see providers.REGISTRY).
Results land in evals/results/<task>/<model>.json and are safe to re-run:
each run is a fresh file, and the stimuli are regenerated from a fixed seed
so every model sees exactly the same images.
"""
import argparse
import importlib
import json
import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import providers  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)


def load_dotenv():
    """Read KEY=value lines from a .env at the repo root, if there is one.

    Environment variables already set win, so an export always overrides the
    file. The file is gitignored; never commit it.
    """
    path = os.path.join(REPO, ".env")
    if not os.path.exists(path):
        return
    for line in open(path):
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip("'\""))


load_dotenv()

INSTRUCTIONS = (
    "\n\nAnswer with exactly one word on the first line: LEFT or RIGHT. "
    "Then one short sentence saying what made you choose it."
)


def load_task(slug):
    mod = importlib.import_module(f"tasks.{slug.replace('-', '_')}")
    return mod.TASK


def parse_choice(raw, options):
    head = (raw or "").strip().upper()
    for opt in options:
        if re.search(rf"\b{opt}\b", head.split("\n")[0]):
            return opt
    for opt in options:            # fall back to anywhere in the reply
        if re.search(rf"\b{opt}\b", head):
            return opt
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", required=True)
    ap.add_argument("--models", required=True, help="comma separated, or 'available'")
    ap.add_argument("--n", type=int, default=20, help="trials, half of them mirrors")
    ap.add_argument("--seed", type=int, default=7)
    args = ap.parse_args()

    task = load_task(args.task)
    stim_dir = os.path.join(HERE, "stimuli", task.slug)
    trials = task.build(stim_dir, n=args.n, seed=args.seed)
    print(f"{len(trials)} trials in {stim_dir}")

    if not os.environ.get("OPENROUTER_API_KEY"):
        sys.exit("Set OPENROUTER_API_KEY (see evals/README.md)")
    names = providers.available() if args.models == "available" else args.models.split(",")

    out_dir = os.path.join(HERE, "results", task.slug)
    os.makedirs(out_dir, exist_ok=True)
    prompt = task.question + INSTRUCTIONS

    for name in names:
        model_id = providers.MODELS.get(name, name)   # unknown name = raw model id
        path = os.path.join(out_dir, f"{name}.json")

        # Resume: keep any trial already answered without an error, so an
        # interrupted or partial run is never paid for twice.
        done, cost = {}, 0.0
        if os.path.exists(path):
            prev = json.load(open(path))
            cost = prev.get("cost_usd", 0.0)
            done = {r["trial_id"]: r for r in prev["trials"]
                    if r.get("choice") and not r.get("error")}
            if done:
                print(f"  {name}: resuming, {len(done)} trials already recorded")

        rows = []
        for t in trials:
            if t.trial_id in done:
                rows.append(done[t.trial_id])
                continue
            try:
                raw, usage = providers.ask(model_id, t.image_path, prompt)
                err = None
                cost += usage.get("cost", 0.0) or 0.0
            except Exception as e:                      # keep going on failures
                raw, usage, err = "", {}, f"{type(e).__name__}: {e}"[:200]
            choice = parse_choice(raw, t.options)
            rows.append({"trial_id": t.trial_id, "mirror_of": t.mirror_of,
                         "truth": t.answer, "choice": choice,
                         "raw": (raw or "")[:600], "error": err,
                         "tokens": {k: usage.get(k) for k in
                                    ("prompt_tokens", "completion_tokens")}})
            # Write after every trial: some models take minutes per call.
            json.dump({"model": name, "model_id": model_id, "task": task.slug,
                       "n": len(rows), "seed": args.seed, "cost_usd": round(cost, 4),
                       "ran_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                       "trials": rows}, open(path, "w"), indent=1)
            print(f"  {name} {t.trial_id}: {choice or '?'} (truth {t.answer})"
                  f"{' [' + err + ']' if err else ''}")
            time.sleep(0.3)
        print(f"wrote {path}  (${cost:.3f})")


if __name__ == "__main__":
    main()
