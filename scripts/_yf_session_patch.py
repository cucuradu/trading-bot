"""Workaround for yfinance's curl_cffi backend failing TLS through the
cloud-sandbox egress proxy (curl error 35: OPENSSL_internal invalid library).
Plain `requests` negotiates fine through the same proxy, so force yfinance's
HTTP layer to always build plain-requests sessions instead of curl_cffi
ones — patching at the `_http.new_session()` source covers every call path
(yf.Ticker, the singleton YfData session, and yf.download's per-call
new_session()). Safe outside the sandbox too — only changes the HTTP
client, not the data.
"""
import requests as _requests_backend
import yfinance._http as _yf_http

_yf_http._backend = _requests_backend
_yf_http.requests = _requests_backend
_yf_http.HAS_CURL_CFFI = False
