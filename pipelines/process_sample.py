"""Small local example: aggregate daily campaign rows and calculate KPIs."""
from pathlib import Path
import pandas as pd
from adtech_analytics.analytics import campaign_kpis


def main():
    df = pd.read_csv(Path(__file__).resolve().parents[1] / "data/sample/campaigns.csv")
    totals = df.groupby("campaign", as_index=False)[["impressions", "clicks", "conversions", "spend", "revenue"]].sum()
    metrics = totals.apply(lambda r: pd.Series(campaign_kpis(r.impressions, r.clicks, r.conversions, r.spend, r.revenue)), axis=1)
    output = pd.concat([totals, metrics], axis=1)
    path = Path(__file__).resolve().parents[1] / "data" / "processed" / "campaign_summary.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(path, index=False)
    print(output.to_string(index=False))
    print(f"Saved {path}")

if __name__ == "__main__":
    main()
