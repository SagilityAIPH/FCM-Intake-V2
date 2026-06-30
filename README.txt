Run:
python main.py

What this build changes:
- The UI collects CMS username and password.
- cms_session.py owns one shared Edge IE-mode CMS browser.
- FCM, ReOpenCheck, and CustomerChecker reuse that same session.
- The hardcoded CMS login inside ReOpenCheck and CustomerChecker is bypassed by shared wrappers.
- The legacy FCM engine is loaded with sys.modules redirects so its imports use the shared-session wrappers.

Included:
- main.py
- app_ui.py
- cms_session.py
- ReOpenCheck_shared.py
- CustomerCheckerV2_shared.py
- legacy folder with your latest engines
- runners folder

Notes:
- This focuses on CMS session sharing and UI credentials.
- Unity, CEM, GoogleSearch, and ProviderResultChecker are still included as legacy files.
- The legacy FCM copy also has the broken recursive safe_click fixed in this bundle.


Edge automation update:
- cms_session.py now auto-detects msedge.exe.
- legacy_unity.py now auto-detects the Edge browser and uses webdriver-manager for EdgeDriver when available.
- To enable EdgeDriver auto-download, install: pip install webdriver-manager


Recovery patch:
- CustomerChecker CMS menu navigation now refreshes and retries when CMS throws the JavaScript null/undefined property error.

Where to place support files when you move this to your machine:
- Put IEDriverServer.exe in the SAME folder as main.py and cms_session.py, or keep your original static path.
- Put these Excel files inside the legacy folder, beside legacy_fcm.py:
  - Liberty Mutual Claims Office Matrix_08-29-19.xlsx
  - Liberty Mutual Medical Dedicated Supervisor Mapping 04-07-2025.xlsx

Why:
- legacy_fcm.py resolves its Excel paths from its own file location, so the Excel files should sit in the legacy folder.
- cms_session.py now looks for IEDriverServer.exe locally first, then falls back to your original hardcoded path.


CustomTkinter UI:
- Use main_v2.py to launch the styled UI.
- app_ui_v2.py is the CustomTkinter app shell.
- fcm_ctk_theme.json contains your visual theme.

Requirements:
- pip install customtkinter


Fix 1:
- cms_session.py now correctly imports find_msedge_path from edge_auto.py.
- Added local IEDriverServer discovery again.
