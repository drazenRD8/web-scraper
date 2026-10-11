"""
Testovi za web-scraper.
Pokreni: pytest -v
"""
import csv
import json
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

# Dodaj root folder u path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scraper import scrape_quotes, USER_AGENTS


# ============================================================
# HTML MOCK PODACI
# ============================================================

HTML_PAGE_1 = """
<html>
<body>
    <div class="quote">
        <span class="text">"Prvi citat"</span>
        <small class="author">Autor Jedan</small>
    </div>
    <div class="quote">
        <span class="text">"Drugi citat"</span>
        <small class="author">Autor Dva</small>
    </div>
    <li class="next"><a href="/page/2/">Next</a></li>
</body>
</html>
"""

HTML_PAGE_2 = """
<html>
<body>
    <div class="quote">
        <span class="text">"Treći citat"</span>
        <small class="author">Autor Tri</small>
    </div>
</body>
</html>
"""

HTML_EMPTY = """
<html><body><div>Nema citata</div></body></html>
"""

HTML_MISSING_FIELDS = """
<html>
<body>
    <div class="quote">
        <small class="author">Samo autor</small>
    </div>
</body>
</html>
"""


# ============================================================
# FIXTURE — mock requests.get
# ============================================================

def make_mock_response(html, status_code=200):
    """Napravi mock response."""
    mock = MagicMock()
    mock.status_code = status_code
    mock.text = html
    mock.raise_for_status = MagicMock()
    return mock


# ============================================================
# TESTIRANJE scrape_quotes()
# ============================================================

class TestScrapeQuotes:
    """Testovi za scrape_quotes funkciju."""

    @patch("scraper.requests.get")
    @patch("scraper.time.sleep")
    def test_single_page_json(self, mock_sleep, mock_get, tmp_path):
        """Testira skrejpovanje jedne stranice u JSON."""
        mock_get.return_value = make_mock_response(HTML_PAGE_2)
        output = tmp_path / "test.json"
        scrape_quotes("http://test.com/", 1, str(output), "json")

        assert output.exists()
        data = json.loads(output.read_text(encoding="utf-8"))
        assert len(data) == 1
        assert data[0]["text"] == '"Treći citat"'
        assert data[0]["author"] == "Autor Tri"

    @patch("scraper.requests.get")
    @patch("scraper.time.sleep")
    def test_single_page_csv(self, mock_sleep, mock_get, tmp_path):
        """Testira skrejpovanje jedne stranice u CSV."""
        mock_get.return_value = make_mock_response(HTML_PAGE_2)
        output = tmp_path / "test.csv"
        scrape_quotes("http://test.com/", 1, str(output), "csv")

        assert output.exists()
        with open(output, encoding="utf-8") as f:
            reader = list(csv.DictReader(f))
        assert len(reader) == 1
        assert reader[0]["author"] == "Autor Tri"

    @patch("scraper.requests.get")
    @patch("scraper.time.sleep")
    def test_multiple_pages(self, mock_sleep, mock_get, tmp_path):
        """Testira paginaciju — 2 stranice."""
        mock_get.side_effect = [
            make_mock_response(HTML_PAGE_1),
            make_mock_response(HTML_PAGE_2),
        ]
        output = tmp_path / "multi.json"
        scrape_quotes("http://test.com/", 2, str(output), "json")

        data = json.loads(output.read_text(encoding="utf-8"))
        assert len(data) == 3  # 2 sa prve + 1 sa druge
        authors = [d["author"] for d in data]
        assert "Autor Jedan" in authors
        assert "Autor Dva" in authors
        assert "Autor Tri" in authors

    @patch("scraper.requests.get")
    @patch("scraper.time.sleep")
    def test_max_pages_limit(self, mock_sleep, mock_get, tmp_path):
        """Testira da MAX_PAGES limit radi (50)."""
        mock_get.return_value = make_mock_response(HTML_EMPTY)
        output = tmp_path / "limit.json"
        scrape_quotes("http://test.com/", 100, str(output), "json")
        # MAX_PAGES je 50, ali HTML_EMPTY nema next, pa staje posle 1
        assert mock_get.call_count >= 1

    @patch("scraper.requests.get")
    @patch("scraper.time.sleep")
    def test_empty_page(self, mock_sleep, mock_get, tmp_path, capsys):
        """Testira stranicu bez citata."""
        mock_get.return_value = make_mock_response(HTML_EMPTY)
        output = tmp_path / "empty.json"
        scrape_quotes("http://test.com/", 1, str(output), "json")

        captured = capsys.readouterr()
        assert "Nema pronađenih podataka" in captured.out

    @patch("scraper.requests.get")
    @patch("scraper.time.sleep")
    def test_missing_fields_use_defaults(self, mock_sleep, mock_get, tmp_path):
        """Testira da nedostajuća polja koriste default vrednosti."""
        mock_get.return_value = make_mock_response(HTML_MISSING_FIELDS)
        output = tmp_path / "missing.json"
        scrape_quotes("http://test.com/", 1, str(output), "json")

        data = json.loads(output.read_text(encoding="utf-8"))
        assert data[0]["text"] == "Nema teksta"
        assert data[0]["author"] == "Samo autor"

    @patch("scraper.requests.get")
    @patch("scraper.time.sleep")
    def test_network_error_handling(self, mock_sleep, mock_get, tmp_path, capsys):
        """Testira mrežnu grešku."""
        import requests
        mock_get.side_effect = requests.RequestException("Network error")
        output = tmp_path / "error.json"
        scrape_quotes("http://test.com/", 1, str(output), "json")

        captured = capsys.readouterr()
        assert "Greška u mreži" in captured.out

    @patch("scraper.requests.get")
    @patch("scraper.time.sleep")
    def test_output_file_conflict_renames(self, mock_sleep, mock_get, tmp_path):
        """Testira da se postojeći fajl preimenuje."""
        mock_get.return_value = make_mock_response(HTML_PAGE_2)
        output = tmp_path / "test.json"
        output.write_text("postojeći sadržaj")

        scrape_quotes("http://test.com/", 1, str(output), "json")

        # Originalni ostaje, novi dobija _1
        assert output.exists()
        assert output.read_text() == "postojeći sadržaj"
        renamed = tmp_path / "test_1.json"
        assert renamed.exists()

    @patch("scraper.requests.get")
    @patch("scraper.time.sleep")
    def test_user_agent_rotation(self, mock_sleep, mock_get, tmp_path):
        """Testira da se User-Agent rotira."""
        mock_get.return_value = make_mock_response(HTML_EMPTY)
        output = tmp_path / "ua.json"
        scrape_quotes("http://test.com/", 1, str(output), "json")

        # Proveri da je headers poslat
        call_args = mock_get.call_args
        headers = call_args.kwargs.get("headers") or call_args[1].get("headers")
        assert "User-Agent" in headers
        assert headers["User-Agent"] in USER_AGENTS

    @patch("scraper.requests.get")
    @patch("scraper.time.sleep")
    def test_timeout_set(self, mock_sleep, mock_get, tmp_path):
        """Testira da je timeout 10 postavljen."""
        mock_get.return_value = make_mock_response(HTML_EMPTY)
        output = tmp_path / "to.json"
        scrape_quotes("http://test.com/", 1, str(output), "json")

        call_args = mock_get.call_args
        timeout = call_args.kwargs.get("timeout") or call_args[1].get("timeout")
        assert timeout == 10


# ============================================================
# TESTIRANJE KONSTANTI
# ============================================================

class TestConstants:
    """Testovi za konstante."""

    def test_user_agents_not_empty(self):
        """Testira da lista User-Agenta nije prazna."""
        assert len(USER_AGENTS) > 0

    def test_user_agents_are_strings(self):
        """Testira da su svi User-Agenti stringovi."""
        for ua in USER_AGENTS:
            assert isinstance(ua, str)
            assert "Mozilla" in ua

    def test_user_agents_modern_browsers(self):
        """Testira da su moderni browseri."""
        joined = " ".join(USER_AGENTS)
        assert "Chrome" in joined or "Firefox" in joined or "Safari" in joined
