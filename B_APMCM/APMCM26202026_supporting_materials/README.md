# APMCM26202026 Supporting Materials

This package contains supporting files related to the submitted paper. Official problem statements and original contest data are NOT included.

## Structure

- `results/`
  - `paper.pdf`: final compiled paper PDF.
  - `paper.tex`: LaTeX source file.
  - `paper_markdown.md`: Markdown backup of the paper.

- `code/`
  - `q2_surrogate_models.py`: surrogate model comparison for Problem 2.
  - `loo_cv.py`: leave-one-out cross validation and grid coverage analysis.
  - `pareto_and_sensitivity.py`: Pareto front, weight sensitivity and perturbation analysis.
  - `generate_figures_v3.py`: main figure generation script.
  - `generate_mechanism_summary.py`: mechanism summary figure generation.
  - `regenerate_fig2.py`: regenerated weight sensitivity figure.
  - `regenerate_fig3.py`: regenerated Monte Carlo perturbation figure.
  - `generate_figures.py`, `generate_figures_v2.py`: earlier figure generation versions.
  - `fix_formulas.py`: auxiliary formula formatting script.

- `figures/`
  - `mechanism_summary.png`: mechanism influence diagram.
  - `pareto_frontier.png`: Pareto front views.
  - `weight_sensitivity.png`: weight sensitivity heatmap.
  - `perturbation_dist.png`: Monte Carlo perturbation distributions.

## Reproducibility

The Python scripts require common scientific packages such as `numpy`, `pandas`, `matplotlib`, `scikit-learn`, and `openpyxl`.

To reproduce the calculations, place the official Attachment 2 file in this directory with the original filename:

```text
附件 2：不同结构参数下无量纲的热阻、压降和温度非均匀性结果数据.xlsx
```

Then run:

```bash
python3 code/loo_cv.py
python3 code/q2_surrogate_models.py
python3 code/pareto_and_sensitivity.py
python3 code/generate_figures_v3.py
python3 code/generate_mechanism_summary.py
python3 code/regenerate_fig2.py
python3 code/regenerate_fig3.py
```

`generate_figures_v3.py`, `regenerate_fig2.py`, `regenerate_fig3.py`, and `generate_mechanism_summary.py` regenerate the images in `figures/`.
