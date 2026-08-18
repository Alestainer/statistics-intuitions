# Statistics Intuitions — reproduction code

Runnable code behind the interactive figures at [alestainer.com](https://alestainer.com).

Each notebook regenerates the **exact** patterns and numbers shown in its article, from the seed
printed under the figure. Where a figure runs in the browser, the notebook ports the same
pseudo-random generator rather than using Python's `random`, so the reproduction is bit-for-bit
rather than merely statistically similar. Each notebook asserts that.

| # | Article | Notebook | Source |
|---|---|---|---|
| 1 | Which map is random? | [`01-which-map-is-random.ipynb`](notebooks/01-which-map-is-random.ipynb) | Clarke, *An Application of the Poisson Distribution*, J. Inst. Actuaries **72** (1946), p.481 — [PDF](https://garcialab.berkeley.edu/courses/papers/Clarke1946.pdf) |

## Running

```bash
pip install matplotlib jupyter
jupyter notebook notebooks/
```

`matplotlib` is only needed for the plots; the statistics are standard library.

## Licence

Code MIT. Article text and figures are not covered by this licence.
