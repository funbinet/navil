"""Built-in plugin exports."""

from navil.scanner.plugins.auth_bypass import AuthBypassPlugin
from navil.scanner.plugins.cors import CorsPlugin
from navil.scanner.plugins.csrf import CsrfPlugin
from navil.scanner.plugins.headers import HeadersPlugin
from navil.scanner.plugins.idor import IdorPlugin
from navil.scanner.plugins.info_disclosure import InfoDisclosurePlugin
from navil.scanner.plugins.lfi import LfiPlugin
from navil.scanner.plugins.open_redirect import OpenRedirectPlugin
from navil.scanner.plugins.rce import RcePlugin
from navil.scanner.plugins.sqli import SqliPlugin
from navil.scanner.plugins.ssrf import SsrfPlugin
from navil.scanner.plugins.xss import XssPlugin

DEFAULT_PLUGINS = [
    XssPlugin(),
    SqliPlugin(),
    SsrfPlugin(),
    IdorPlugin(),
    CsrfPlugin(),
    HeadersPlugin(),
    CorsPlugin(),
    OpenRedirectPlugin(),
    LfiPlugin(),
    RcePlugin(),
    AuthBypassPlugin(),
    InfoDisclosurePlugin(),
]

__all__ = ["DEFAULT_PLUGINS"]
