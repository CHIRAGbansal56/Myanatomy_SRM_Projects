# Exploratory Data Analysis on India's COVID-19 Data

A mini project exploring state-wise trends, recovery/death rates, and vaccination
progress during India's COVID-19 pandemic, built with **Pandas, NumPy, Matplotlib,
and Seaborn**.

## 📊 What this project does

1. **Loads** two public datasets directly from the web (no manual download needed):
   - Daily state-wise case data (confirmed / deaths / recovered), 30 Jan – 6 Aug 2020, from [imdevskp/covid-19-india-data](https://github.com/imdevskp/covid-19-india-data)
   - India's national vaccination totals (Jan 2021 onward) from [Our World in Data](https://github.com/owid/covid-19-data)
2. **Inspects** the raw data for problems (wrong data types, inconsistent naming)
3. **Cleans** it (fixes the `Death` column's data type, merges duplicate state-name spellings)
4. **Explores** it with `groupby` and `pivot_table`
5. **Visualises** it with 12 charts (line, bar, donut, violin, heatmap, scatter, stacked area, etc.)
6. **Summarises** the findings in writing

See [`REPORT.md`](REPORT.md) for the full write-up with all charts and findings, or open the
notebook directly to see the code + outputs together.

## 📁 Project structure

```
covid19_india_eda/
├── covid19_india_eda.ipynb   # Main notebook — code + charts + explanations
├── build_analysis.py          # Same analysis as a plain .py script (generates images/)
├── REPORT.md                  # Written report with all 12 charts and findings
├── README.md                  # This file
├── requirements.txt           # Python dependencies
├── images/                    # Chart PNGs (used in REPORT.md)
└── data/
    └── cleaned_covid_india.csv  # Cleaned dataset, ready for reuse
```

## 🛠 How to run it yourself

1. Clone this repo:
   ```bash
   git clone <your-repo-url>
   cd covid19_india_eda
   ```
2. Create a virtual environment (optional but recommended) and install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Open the notebook in VS Code or Jupyter and run all cells:
   ```bash
   jupyter notebook covid19_india_eda.ipynb
   ```
   Both datasets are fetched live from GitHub/OWID URLs, so you just need an internet
   connection — no files to download by hand.

## 🔑 Key findings (short version)

- India's first wave (through Aug 2020) was still accelerating when this dataset ends —
  daily new cases hadn't peaked yet.
- The outbreak was heavily concentrated: **Maharashtra** alone made up ~24% of all
  national cases; the **top 6 states** held about two-thirds of the total case load.
- Recovery and death rates varied a lot by state — **Delhi** had the highest recovery
  rate (~90%), while **Gujarat** had the highest death rate (~3.8%) among the worst-hit
  states.
- By mid-2024, India's vaccination drive had delivered **2.2+ billion doses** and fully
  vaccinated **950+ million people**.

Full details, charts, and caveats are in [`REPORT.md`](REPORT.md).

## 📚 Data sources & credits

- Case data: [imdevskp/covid-19-india-data](https://github.com/imdevskp/covid-19-india-data) (sourced from MoHFW / covid19india.org)
- Vaccination data: [Our World in Data](https://github.com/owid/covid-19-data)

## ⚠️ Caveats

This is state-bulletin-sourced data and inherits whatever reporting inconsistencies
existed at the time. Recovery/death rates are simple ratios of cumulative totals on a
given date, not adjusted for reporting lag, so they should be read as directional
trends rather than precise clinical outcome rates.
