from __future__ import annotations

import sys

import cms_session
import CustomerCheckerV2_shared
import ReOpenCheck_shared
from config import FCM_SCRIPT
from module_loader import load_module_from_path

def run_fcm(ui, context):
    cms_session.set_credentials(context.cms_username, context.cms_password)
    cms_session.init_shared_cms_session()

    sys.modules["ReOpenCheck"] = ReOpenCheck_shared
    sys.modules["CustomerCheckerV2"] = CustomerCheckerV2_shared

    module = load_module_from_path("legacy_fcm_shared_runtime", FCM_SCRIPT)

    def ui_notify(title: str, text: str):
        ui.log(f"[{title}] {text}")
        try:
            ui.show_info(title, text)
        except Exception:
            pass

    module.notify = ui_notify
    ui.log("Starting full FCM workflow with shared CMS session...")
    module.main()
    ui.log("Full FCM workflow finished.")
