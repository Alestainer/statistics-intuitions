#!/usr/bin/env python3
"""Score the eval results, including the position-bias control.

    python evals/report.py --task which-map-is-random

Accuracy alone is misleading: a model that always answers RIGHT scores
whatever fraction of trials happen to be RIGHT. The mirror pairs settle it.
Each trial has a left-right mirrored twin with the opposite correct answer, so:

  consistent  - answered the same PATTERN both times (flipped side): reading the image
  positional  - answered the same SIDE both times: reading position, not pattern

A model at chance on accuracy but 100% positional is not guessing, it is
ignoring the image.
"""
import argparse, glob, json, os

HERE = os.path.dirname(os.path.abspath(__file__))


def score(data):
    rows = data["trials"]
    by_id = {r["trial_id"]: r for r in rows}
    answered = [r for r in rows if r["choice"]]
    correct = sum(r["choice"] == r["truth"] for r in answered)
    left = sum(r["choice"] == "LEFT" for r in answered)

    pairs = positional = consistent = 0
    for r in rows:
        if not r["mirror_of"]:
            continue
        base = by_id.get(r["mirror_of"])
        if not base or not base["choice"] or not r["choice"]:
            continue
        pairs += 1
        if base["choice"] == r["choice"]:
            positional += 1        # same side chosen despite the flip
        else:
            consistent += 1        # followed the pattern across the flip
    return {
        "model": data["model"], "model_id": data.get("model_id", ""),
        "n": len(rows), "answered": len(answered),
        "accuracy": correct / len(answered) if answered else 0.0,
        "left_rate": left / len(answered) if answered else 0.0,
        "pairs": pairs,
        "pattern_consistent": consistent / pairs if pairs else 0.0,
        "position_locked": positional / pairs if pairs else 0.0,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", required=True)
    args = ap.parse_args()
    files = sorted(glob.glob(os.path.join(HERE, "results", args.task, "*.json")))
    if not files:
        raise SystemExit(f"no results for {args.task}")
    rows = [score(json.load(open(f))) for f in files]

    print(f"\n{args.task}   (chance accuracy = 0.50)\n")
    hdr = f"{'model':10s} {'n':>3s} {'acc':>6s} {'LEFT%':>7s} {'follows pattern':>16s} {'position-locked':>16s}"
    print(hdr); print("-" * len(hdr))
    for r in rows:
        print(f"{r['model']:10s} {r['n']:3d} {r['accuracy']:6.2f} {r['left_rate']*100:6.0f}% "
              f"{r['pattern_consistent']*100:15.0f}% {r['position_locked']*100:15.0f}%")
    print("\nfollows pattern: answer flipped with the mirrored image (reading the dots)")
    print("position-locked: answer stayed on the same side (ignoring the dots)")


if __name__ == "__main__":
    main()
