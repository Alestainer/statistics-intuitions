# Statistics Intuitions — reproduction code

Runnable code behind the interactive figures at [alestainer.com](https://alestainer.com).

Each notebook regenerates the exact patterns and numbers shown in its article. Where the evaluation used frozen images, those images and their manifests are included under `data/`.

| # | Article | Notebook | Source |
|---|---|---|---|
| 1 | Which map is random? | [`01-which-map-is-random.ipynb`](notebooks/01-which-map-is-random.ipynb) &nbsp; [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Alestainer/statistics-intuitions/blob/main/notebooks/01-which-map-is-random.ipynb) | Clarke, [*An Application of the Poisson Distribution*](https://garcialab.berkeley.edu/courses/papers/Clarke1946.pdf), J. Inst. Actuaries **72** (1946), p.481 |
| 2 | Simple Stats intuition AI fails on | [`02-which-map-is-random-clumped.ipynb`](notebooks/02-which-map-is-random-clumped.ipynb) &nbsp; [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Alestainer/statistics-intuitions/blob/main/notebooks/02-which-map-is-random-clumped.ipynb) | Local-attraction variant of the Clarke task |
| 3 | Do you know when you know: Testing LLMs for their metacognitive skills | [`03-function-sampling.ipynb`](notebooks/03-function-sampling.ipynb) &nbsp; [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Alestainer/statistics-intuitions/blob/main/notebooks/03-function-sampling.ipynb) | Sequential function identification with an explicit abstention action |
| 4 | Another easy way to break LLMs I found | [`04-support-boundary.ipynb`](notebooks/04-support-boundary.ipynb) &nbsp; [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Alestainer/statistics-intuitions/blob/main/notebooks/04-support-boundary.ipynb) | Function identification from the support boundary of a conditioned uniform distribution |

## Running

Click a Colab badge to run a notebook in the browser.

Locally:

```bash
pip install matplotlib pandas pillow jupyter
jupyter notebook notebooks/
```

The notebooks make no paid API calls automatically. Model reruns require an explicit model selection and API key.

## Licence

Code MIT. Article text and figures are not covered by this licence.
