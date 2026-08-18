# LLM intuition evals

Every article in **Statistics Intuitions** poses a question to the reader. This runs the same
question past frontier models, with the same images.

## Why not just measure accuracy

A model that answers `RIGHT` every time scores ~50% on a balanced set. That is indistinguishable
from a coin flip, and both are indistinguishable from a model that reads the image well. So every
trial is paired with its **left-right mirror**, which has the opposite correct answer:

| behaviour | accuracy | follows pattern | position-locked |
|---|---|---|---|
| always answers one side | 0.50 | 0% | 100% |
| reads the image correctly | 1.00 | 100% | 0% |
| **reads it and shares the human bias** | **0.00** | **100%** | 0% |

The last row is the interesting one. A model that reliably picks the *wrong* square is not failing
to see — it is seeing, and making the human mistake. Accuracy alone hides that completely.

An early informal run of one model answered `RIGHT` on all five images while describing the correct
rule in its reasoning. That is what prompted the mirror control.

## Running

```bash
export OPENAI_API_KEY=...        # or ANTHROPIC_API_KEY, GEMINI_API_KEY,
                                 # MOONSHOT_API_KEY (Kimi), DASHSCOPE_API_KEY (Qwen)
python evals/run.py --task which-map-is-random --models available --n 20
python evals/report.py --task which-map-is-random
```

`--models available` runs whichever providers have a key set. Stimuli are regenerated from a fixed
seed, so every model sees byte-identical images. Results are written per model to
`results/<task>/<model>.json`, including each raw reply.

## Adding a task

Drop a module in `tasks/` exposing a `TASK` with `slug`, `question`, and `build(out_dir, n, seed)`
returning `Trial`s. Pair each trial with a control that isolates the shortcut you are worried
about — mirroring for left/right questions, relabelling for A/B ones.

## Adding a provider

One function in `providers.py` plus a `REGISTRY` entry. OpenAI, Kimi and Qwen share the
chat/completions shape, so they reuse one adapter.

Keys are read from the environment and never written to disk. Raw replies are stored; do not put
anything in a prompt you would not publish.
