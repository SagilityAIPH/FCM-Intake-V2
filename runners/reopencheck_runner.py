from __future__ import annotations

import cms_session
import ReOpenCheck_shared

def run_reopen_check(ui, context, claim_number: str):
    cms_session.set_credentials(context.cms_username, context.cms_password)
    result = ReOpenCheck_shared.MainReopenCheck(claim_number)
    ui.log("ReOpenCheck finished.")
    ui.log(str(result))
    return result
