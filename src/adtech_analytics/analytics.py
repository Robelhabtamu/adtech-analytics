"""KPI calculations on aggregate campaign counts."""

def safe_ratio(numerator: float, denominator: float):
    return numerator / denominator if denominator else None


def campaign_kpis(impressions: int, clicks: int, conversions: int, spend: float, revenue: float):
    return {
        "ctr_percent": safe_ratio(100 * clicks, impressions),
        "cpm": safe_ratio(1000 * spend, impressions),
        "cpc": safe_ratio(spend, clicks),
        "cvr_percent": safe_ratio(100 * conversions, clicks),
        "cpa": safe_ratio(spend, conversions),
        "roas": safe_ratio(revenue, spend),
    }
