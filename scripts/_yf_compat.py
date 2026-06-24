"""Patches yfinance to use a plain requests.Session instead of its default
curl_cffi session. In this sandbox, curl_cffi's bundled BoringSSL fails the
TLS handshake against the egress proxy's re-terminated certificate
("OPENSSL_internal:invalid library (0)") while plain `requests` works fine
against the same hosts. Import and call patch() before any yfinance call.
"""
import requests
from yfinance.data import YfData

_session = None


def get_session() -> requests.Session:
    """Returns the shared plain-requests session, creating it if needed.

    yf.download() takes its own `session=` kwarg and ignores the YfData
    singleton patched by patch() — pass this explicitly to yf.download().
    """
    global _session
    if _session is None:
        _session = requests.Session()
        _session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
            )
        })
    return _session


def patch() -> None:
    """Seeds yfinance's YfData singleton so plain yf.Ticker(...) calls
    (without an explicit session=) use plain requests instead of curl_cffi.
    """
    YfData(session=get_session())
