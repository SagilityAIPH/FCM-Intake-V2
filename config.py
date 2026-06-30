from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
LEGACY_DIR = BASE_DIR / "legacy"

FCM_SCRIPT = LEGACY_DIR / "legacy_fcm.py"
REOPENCHECK_SCRIPT = LEGACY_DIR / "legacy_reopencheck.py"
CUSTOMERCHECKER_SCRIPT = LEGACY_DIR / "legacy_customerchecker.py"
CEM_SCRIPT = LEGACY_DIR / "legacy_cem.py"
GOOGLESEARCH_SCRIPT = LEGACY_DIR / "legacy_googlesearch.py"
PROVIDER_RESULT_SCRIPT = LEGACY_DIR / "legacy_providerresultchecker.py"
UNITY_SCRIPT = LEGACY_DIR / "legacy_unity.py"

APP_TITLE = "FCM Intake Bot"
WINDOW_SIZE = "1040x760"
