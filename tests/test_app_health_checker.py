import sys, pathlib
from unittest import mock
import requests
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))
from app_health_checker import check

def resp(code):
    r = mock.Mock(status_code=code); r.elapsed.total_seconds.return_value = 0.05; return r

@mock.patch("app_health_checker.requests.get", return_value=resp(200))
def test_200_is_up(_): assert check("http://x", retries=1)[0] == "UP"

@mock.patch("app_health_checker.requests.get", return_value=resp(301))
def test_3xx_is_up(_): assert check("http://x", retries=1)[0] == "UP"

@mock.patch("app_health_checker.requests.get", return_value=resp(404))
def test_404_is_down_without_retry(g):
    assert check("http://x", retries=3, backoff=0)[0] == "DOWN"; assert g.call_count == 1

@mock.patch("app_health_checker.requests.get", return_value=resp(503))
def test_5xx_retries_then_down(g):
    assert check("http://x", retries=3, backoff=0) == ("DOWN", "HTTP 503"); assert g.call_count == 3

@mock.patch("app_health_checker.requests.get", side_effect=[requests.exceptions.ConnectionError(), resp(200)])
def test_recovers_after_transient_failure(_): assert check("http://x", retries=2, backoff=0)[0] == "UP"

@mock.patch("app_health_checker.requests.get", side_effect=requests.exceptions.Timeout())
def test_timeout_is_down(_): assert "timeout" in check("http://x", retries=1, backoff=0)[1]
