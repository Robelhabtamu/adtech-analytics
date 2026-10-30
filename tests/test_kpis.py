from adtech_analytics.analytics import campaign_kpis

def test_samsung_example():
    actual = campaign_kpis(100000, 2000, 50, 1000, 5000)
    assert actual == {"ctr_percent": 2.0, "cpm": 10.0, "cpc": 0.5, "cvr_percent": 2.5, "cpa": 20.0, "roas": 5.0}

def test_zero_denominators():
    actual = campaign_kpis(0, 0, 0, 0, 0)
    assert all(value is None for value in actual.values())
