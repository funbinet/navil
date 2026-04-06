"""Global constants for Navil."""

from pathlib import Path

APP_NAME = "Navil"
DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 8080
DEFAULT_REQUEST_TIMEOUT_SECONDS = 10.0
DEFAULT_SCAN_CONCURRENCY = 10
DEFAULT_MAX_DEPTH = 3
DEFAULT_RATE_LIMIT_RPS = 2.0
DEFAULT_MAX_REQUESTS = 2500

DATA_DIR = Path(".data")
DB_PATH = DATA_DIR / "navil.db"
REPORTS_DIR = Path("reports")
LOGS_DIR = Path("logs")
MODEL_DIR = Path("models")
PAYLOAD_DIR = Path(__file__).parent / "mutator" / "payloads"

SECURITY_HEADERS = {
    "content-security-policy",
    "x-frame-options",
    "x-content-type-options",
    "strict-transport-security",
    "referrer-policy",
    "permissions-policy",
}

THIRD_PARTY_INTEGRATIONS = ("burp", "nuclei", "metasploit")
