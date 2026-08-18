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
        rows = []
        for t in trials:
            try:
                raw = providers.ask(model_id, t.image_path, prompt)
                err = None
            except Exception as e:                      # keep going on failures
                raw, err = "", f"{type(e).__name__}: {e}"[:200]
            choice = parse_choice(raw, t.options)
            rows.append({"trial_id": t.trial_id, "mirror_of": t.mirror_of,
                         "truth": t.answer, "choice": choice,
                         "raw": (raw or "").strip()[:400], "error": err})
            print(f"  {name} {t.trial_id}: {choice or '?'} (truth {t.answer})")
            time.sleep(0.5)
        path = os.path.join(out_dir, f"{name}.json")
        json.dump({"model": name, "model_id": model_id, "task": task.slug,
                   "n": len(rows), "seed": args.seed,
                   "ran_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                   "trials": rows}, open(path, "w"), indent=1)
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
