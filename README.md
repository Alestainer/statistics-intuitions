# Statistics Intuitions — reproduction code

Runnable code behind the interactive figures at [alestainer.com](https://alestainer.com).

Each notebook regenerates the **exact** patterns and numbers shown in its article, from the seed
printed under the figure. Where a figure runs in the browser, the notebook ports the same
pseudo-random generator rather than using Python's `random`, so the reproduction is bit-for-bit
rather than merely statistically similar. Each notebook asserts that.

| # | Article | Notebook | Source |
|---|---|---|---|
| 1 | Which map is random? | [`01-which-map-is-random.ipynb`](notebooks/01-which-map-is-random.ipynb) &nbsp; [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Alestainer/statistics-intuitions/blob/main/notebooks/01-which-map-is-random.ipynb) | Clarke, [*An Application of the Poisson Distribution*](https://garcialab.berkeley.edu/courses/papers/Clarke1946.pdf), J. Inst. Actuaries **72** (1946), p.481 |
| 2 | Can you beat the AI models on this task? | [`02-which-map-is-random-clumped.ipynb`](notebooks/02-which-map-is-random-clumped.ipynb) &nbsp; [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Alestainer/statistics-intuitions/blob/main/notebooks/02-which-map-is-random-clumped.ipynb) | Local-attraction variant of the Clarke task |

## Running

Click the Colab badge — it opens in the browser with nothing to install.

Locally:

```bash
pip install matplotlib jupyter
jupyter notebook notebooks/
```

`matplotlib` is only needed for the plots; the statistics are standard library. The clumping
notebook defaults to making no paid API calls; model reruns require an explicit model selection.

## Licence

Code MIT. Article text and figures are not covered by this licence.
