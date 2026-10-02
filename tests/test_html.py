import pandas as pd

from dataguard.html_report import render_html
from dataguard.scanner import scan_dataframe


def test_html_report():
    r=scan_dataframe(pd.DataFrame({"id":[1,2],"email":["a@example.com","b@example.com"]}))
    html=render_html(r)
    assert "DataGuard AI" in html and "Quality" in html and "<table>" in html
