"""
Builds the analysis and saves every chart as a PNG into images/,
and the cleaned dataset into data/. Also prints the numbers used
in the written report so the report text can be checked against
real output.
"""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="whitegrid")
plt.rcParams["figure.dpi"] = 110
IMG = "images/"

# ---------------------------------------------------------------
# 1. Load
# ---------------------------------------------------------------
cases = pd.read_csv(
    "https://raw.githubusercontent.com/imdevskp/covid-19-india-data/master/complete.csv"
)
vax = pd.read_csv(
    "https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/vaccinations/country_data/India.csv"
)
print("Cases shape:", cases.shape)
print("Vaccination shape:", vax.shape)

# ---------------------------------------------------------------
# 2. Clean
# ---------------------------------------------------------------
cases.columns = [
    "date", "state", "lat", "long", "confirmed",
    "deaths", "cured", "new_cases", "new_deaths", "new_recovered",
]
cases["date"] = pd.to_datetime(cases["date"])
cases["deaths"] = pd.to_numeric(cases["deaths"], errors="coerce").fillna(0).astype(int)
cases["confirmed"] = cases["confirmed"].astype(int)
cases["cured"] = cases["cured"].astype(int)

name_fix = {
    "Telangana***": "Telangana",
    "Telengana": "Telangana",
    "Union Territory of Jammu and Kashmir": "Jammu and Kashmir",
    "Union Territory of Ladakh": "Ladakh",
    "Union Territory of Chandigarh": "Chandigarh",
}
cases["state"] = cases["state"].replace(name_fix)
cases = cases.drop_duplicates(subset=["date", "state"]).sort_values(["state", "date"]).reset_index(drop=True)
cases["active"] = cases["confirmed"] - cases["deaths"] - cases["cured"]
cases["month"] = cases["date"].dt.strftime("%Y-%m")

print("Clean state count:", cases["state"].nunique())
print("Missing values after cleaning:", cases.isna().sum().sum())

cases.to_csv("data/cleaned_covid_india.csv", index=False)

# ---------------------------------------------------------------
# 3. National daily totals (+ 7-day rolling average - NEW vs example)
# ---------------------------------------------------------------
national = cases.groupby("date", as_index=False)[["confirmed", "deaths", "cured"]].sum()
national["recovery_rate"] = (national["cured"] / national["confirmed"] * 100).round(2)
national["death_rate"] = (national["deaths"] / national["confirmed"] * 100).round(2)
national["new_confirmed"] = national["confirmed"].diff().fillna(national["confirmed"])
national["new_confirmed_7d_avg"] = national["new_confirmed"].rolling(7).mean()
national["month"] = national["date"].dt.strftime("%Y-%m")

latest_date = cases["date"].max()
latest_row = national.iloc[-1]
print(f"\nAs of {latest_date.date()}:")
print(f"  Total confirmed : {latest_row['confirmed']:,}")
print(f"  Total recovered : {latest_row['cured']:,}")
print(f"  Total deaths    : {latest_row['deaths']:,}")
print(f"  Recovery rate   : {latest_row['recovery_rate']}%")
print(f"  Death rate      : {latest_row['death_rate']}%")
print(f"  Peak single-day new cases (raw): {int(national['new_confirmed'].max()):,}")

# ---------------------------------------------------------------
# 4. State snapshot
# ---------------------------------------------------------------
latest = cases[cases["date"] == latest_date].copy()
latest["recovery_rate"] = (latest["cured"] / latest["confirmed"] * 100).round(2)
latest["death_rate"] = (latest["deaths"] / latest["confirmed"] * 100).round(2)
latest = latest.sort_values("confirmed", ascending=False).reset_index(drop=True)
top10 = latest.head(10)
top5_states = top10["state"].head(5).tolist()
bottom10 = latest[latest["confirmed"] > 0].nsmallest(10, "confirmed")

print("\nTop 10 states by confirmed cases:")
print(top10[["state", "confirmed", "deaths", "cured", "recovery_rate", "death_rate"]].to_string(index=False))

share_top6 = latest.nlargest(6, "confirmed")["confirmed"].sum() / latest["confirmed"].sum() * 100
print(f"\nTop 6 states share of national cases: {share_top6:.1f}%")
maha_share = latest.loc[latest['state']=='Maharashtra','confirmed'].values[0] / latest['confirmed'].sum() * 100
print(f"Maharashtra alone: {maha_share:.1f}%")

worst_death_state = top10.loc[top10['death_rate'].idxmax()]
best_death_state = top10.loc[top10['death_rate'].idxmin()]
print(f"Highest death rate among top10: {worst_death_state['state']} ({worst_death_state['death_rate']}%)")
print(f"Lowest death rate among top10: {best_death_state['state']} ({best_death_state['death_rate']}%)")

# ---------------------------------------------------------------
# 5. Charts  (12 charts - deliberately varied from the sample report)
# ---------------------------------------------------------------

# Chart 1 - National cumulative trend as a STACKED AREA chart (sample used plain lines)
fig, ax = plt.subplots(figsize=(8, 4.5))
ax.stackplot(
    national["date"],
    national["cured"], national["deaths"], national["active"] if "active" in national else national["confirmed"] - national["cured"] - national["deaths"],
    labels=["Recovered", "Deaths", "Active"],
    colors=["#16a34a", "#dc2626", "#2563eb"], alpha=0.85,
)
ax.set_title("India: Cumulative Case Outcomes Over Time (Stacked)")
ax.set_xlabel("Date"); ax.set_ylabel("People")
ax.legend(loc="upper left")
fig.autofmt_xdate(); plt.tight_layout()
plt.savefig(IMG + "01_cumulative_stacked_area.png"); plt.close()

# Chart 2 - Daily new cases bar + 7-day rolling average line (sample only had the bar)
fig, ax = plt.subplots(figsize=(8, 4.5))
ax.bar(national["date"], national["new_confirmed"], color="#93c5fd", width=1.0, label="Daily new cases")
ax.plot(national["date"], national["new_confirmed_7d_avg"], color="#1d4ed8", lw=2, label="7-day average")
ax.set_title("India: Daily New Confirmed Cases (with 7-day average)")
ax.set_xlabel("Date"); ax.set_ylabel("New cases")
ax.legend()
fig.autofmt_xdate(); plt.tight_layout()
plt.savefig(IMG + "02_daily_new_cases_rolling_avg.png"); plt.close()

# Chart 3 - Top 10 states: GROUPED bar of confirmed vs deaths (sample used a single-metric bar)
fig, ax = plt.subplots(figsize=(9, 5))
x = np.arange(len(top10))
width = 0.4
ax.bar(x - width/2, top10["confirmed"], width, label="Confirmed", color="#2563eb")
ax.bar(x + width/2, top10["deaths"] * 20, width, label="Deaths x20 (scaled to be visible)", color="#dc2626")
ax.set_xticks(x); ax.set_xticklabels(top10["state"], rotation=45, ha="right")
ax.set_title(f"Top 10 States: Confirmed Cases vs Deaths (as of {latest_date.date()})")
ax.set_ylabel("Count")
ax.legend()
plt.tight_layout()
plt.savefig(IMG + "03_top10_confirmed_vs_deaths.png"); plt.close()

# Chart 4 - Death rate ranking for top10 (sample used recovery rate here)
top10_sorted_dr = top10.sort_values("death_rate")
fig, ax = plt.subplots(figsize=(8, 5))
sns.barplot(data=top10_sorted_dr, y="state", x="death_rate", hue="state", palette="Reds", legend=False, ax=ax)
ax.set_title("Death Rate (%) — Top 10 Worst-Hit States")
ax.set_xlabel("Death rate (%)"); ax.set_ylabel("")
plt.tight_layout()
plt.savefig(IMG + "04_death_rate_top10.png"); plt.close()

# Chart 5 - Confirmed-case trend for top 5 states on a LOG scale (sample used linear scale)
fig, ax = plt.subplots(figsize=(8, 4.5))
for s in top5_states:
    sub = cases[cases["state"] == s]
    ax.plot(sub["date"], sub["confirmed"].clip(lower=1), label=s, lw=2)
ax.set_yscale("log")
ax.set_title("Confirmed Cases Over Time — Top 5 States (log scale)")
ax.set_xlabel("Date"); ax.set_ylabel("Confirmed cases (log scale)")
ax.legend(fontsize=8)
fig.autofmt_xdate(); plt.tight_layout()
plt.savefig(IMG + "05_top5_states_log_scale.png"); plt.close()

# Chart 6 - Donut chart (sample used a plain pie chart)
top6 = latest.nlargest(6, "confirmed")[["state", "confirmed"]]
others = latest["confirmed"].sum() - top6["confirmed"].sum()
pie_labels = top6["state"].tolist() + ["Rest of India"]
pie_values = top6["confirmed"].tolist() + [others]
fig, ax = plt.subplots(figsize=(6.5, 6.5))
wedges, texts, autotexts = ax.pie(
    pie_values, labels=pie_labels, autopct="%1.1f%%", startangle=90,
    colors=sns.color_palette("Blues_r", 7), wedgeprops=dict(width=0.4)
)
ax.set_title("Share of Total Confirmed Cases by State (Donut)")
plt.tight_layout()
plt.savefig(IMG + "06_share_donut.png"); plt.close()

# Chart 7 - National DEATH rate trend (sample tracked recovery rate here)
fig, ax = plt.subplots(figsize=(8, 4.5))
ax.plot(national["date"], national["death_rate"], color="#dc2626", lw=2)
ax.set_title("India: National Death Rate Over Time")
ax.set_xlabel("Date"); ax.set_ylabel("Death rate (%)")
fig.autofmt_xdate(); plt.tight_layout()
plt.savefig(IMG + "07_national_death_rate.png"); plt.close()

# Chart 8 - Active cases vs confirmed scatter, colored by state (sample used recovery vs death bubble)
sizeable = latest[latest["confirmed"] >= 1000]
fig, ax = plt.subplots(figsize=(7, 5.5))
sc = sns.scatterplot(data=sizeable, x="confirmed", y="active", hue="recovery_rate",
                      palette="RdYlGn", size="confirmed", sizes=(30, 400), legend=False, ax=ax)
for _, r in sizeable.nlargest(6, "confirmed").iterrows():
    ax.annotate(r["state"], (r["confirmed"], r["active"]), fontsize=7,
                xytext=(3, 3), textcoords="offset points")
ax.set_title("Active Cases vs Confirmed Cases by State\n(color = recovery rate)")
ax.set_xlabel("Confirmed cases"); ax.set_ylabel("Active cases")
plt.tight_layout()
plt.savefig(IMG + "08_active_vs_confirmed_scatter.png"); plt.close()

# Chart 9 - Correlation heatmap (kept, standard for this kind of EDA, slightly different columns)
corr_cols = ["confirmed", "deaths", "cured", "active", "new_confirmed", "recovery_rate", "death_rate"]
corr = national.assign(active=national["confirmed"] - national["cured"] - national["deaths"])[corr_cols].corr()
fig, ax = plt.subplots(figsize=(6.5, 5.5))
sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", center=0, ax=ax)
ax.set_title("Correlation Between National COVID Metrics")
plt.tight_layout()
plt.savefig(IMG + "09_correlation_heatmap.png"); plt.close()

# Chart 10 - Violin plot of daily new cases spread by month (sample used a boxplot)
fig, ax = plt.subplots(figsize=(8, 4.5))
sns.violinplot(data=national, x="month", y="new_confirmed", hue="month", palette="Blues", legend=False, ax=ax)
ax.set_title("Spread of Daily New Cases by Month (Violin Plot)")
ax.set_xlabel("Month"); ax.set_ylabel("Daily new cases")
plt.tight_layout()
plt.savefig(IMG + "10_monthly_spread_violin.png"); plt.close()

# Chart 11 - Vaccination progress as TWO subplots: cumulative + daily new doses (sample had one chart)
vax["date"] = pd.to_datetime(vax["date"])
vax["daily_doses"] = vax["total_vaccinations"].diff()
fig, axes = plt.subplots(2, 1, figsize=(8, 7), sharex=True)
axes[0].plot(vax["date"], vax["total_vaccinations"] / 1e9, label="Total doses (Bn)", color="#7c3aed", lw=2)
axes[0].plot(vax["date"], vax["people_fully_vaccinated"] / 1e9, label="Fully vaccinated (Bn)", color="#0d9488", lw=2)
axes[0].set_ylabel("People / doses (Bn)"); axes[0].legend(); axes[0].set_title("India: COVID-19 Vaccination Progress (2021-2024)")
axes[1].bar(vax["date"], vax["daily_doses"] / 1e6, color="#a78bfa", width=1.0)
axes[1].set_ylabel("Daily doses (Millions)"); axes[1].set_xlabel("Date")
fig.autofmt_xdate(); plt.tight_layout()
plt.savefig(IMG + "11_vaccination_progress_two_panel.png"); plt.close()

# Chart 12 - Least-affected states (kept, but horizontal + value labels)
fig, ax = plt.subplots(figsize=(8, 5))
bars = sns.barplot(data=bottom10, y="state", x="confirmed", hue="state", palette="Oranges", legend=False, ax=ax)
for i, v in enumerate(bottom10["confirmed"]):
    ax.text(v + 20, i, f"{v:,}", va="center", fontsize=8)
ax.set_title(f"10 Least-Affected States/UTs by Confirmed Cases (as of {latest_date.date()})")
ax.set_xlabel("Confirmed cases"); ax.set_ylabel("")
plt.tight_layout()
plt.savefig(IMG + "12_least_affected_states.png"); plt.close()

print("\nAll 12 charts saved to images/")

vax_latest = vax.dropna(subset=["total_vaccinations"]).iloc[-1]
print(f"\nVaccination summary (as of {vax_latest['date'].date()}):")
print(f"  Total doses: {vax_latest['total_vaccinations']:,.0f}")
print(f"  Fully vaccinated: {vax_latest['people_fully_vaccinated']:,.0f}")

print("\nDone.")
