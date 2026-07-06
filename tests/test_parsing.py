import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from audit_collector.models import Report, slugify
from audit_collector.scrapers.github_repo import _date_from_name, _project_from_name
from audit_collector import catalog


def test_slugify():
    assert slugify("Uniswap V4 (Final) Report!") == "uniswap-v4-final-report"


def test_date_from_name():
    assert _date_from_name("reviews/2023-05-uniswap.pdf") == "2023-05"
    assert _date_from_name("Harbor Review July 2018.pdf") == "2018-07"
    assert _date_from_name("audit_2021.12.01_final.pdf") == "2021-12-01"
    assert _date_from_name("SomeProject_2020.pdf") == "2020"
    assert _date_from_name("no-date-here.pdf") is None


def test_project_from_name():
    assert _project_from_name("reviews/2023-05-uniswap-securityreview.pdf") == "uniswap"
    assert _project_from_name("Harbor Smart Contract. Review July 2018.pdf") == "Harbor Smart Contract"


def test_merge_preserves_download_state():
    old = Report(source="s", project="P", title="T", report_url="https://x/1.pdf",
                 local_path="data/reports/s/t.pdf", sha256="abc")
    fresh = Report(source="s", project="P2", title="T", report_url="https://x/1.pdf")
    merged = catalog.merge([old], [fresh])
    assert len(merged) == 1
    assert merged[0].project == "P2"
    assert merged[0].local_path == "data/reports/s/t.pdf"
    assert merged[0].sha256 == "abc"
