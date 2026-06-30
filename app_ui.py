from __future__ import annotations

import contextlib
import io
import queue
import threading
import tkinter as tk
from tkinter import ttk, messagebox

import cms_session
from bot_context import BotContext
from config import APP_TITLE, WINDOW_SIZE
from runners.customerchecker_runner import run_customer_check
from runners.fcm_runner import run_fcm
from runners.reopencheck_runner import run_reopen_check

class QueueWriter(io.TextIOBase):
    def __init__(self, log_queue: queue.Queue):
        self.log_queue = log_queue

    def write(self, s):
        if s:
            self.log_queue.put(str(s))
        return len(s)

    def flush(self):
        return None

class FcmBotApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(APP_TITLE)
        self.root.geometry(WINDOW_SIZE)
        self.log_queue = queue.Queue()
        self._build_ui()
        self.bring_to_front()
        self.root.after(100, self._drain_log_queue)

    def _build_ui(self):
        outer = ttk.Frame(self.root, padding=12)
        outer.pack(fill="both", expand=True)

        creds = ttk.LabelFrame(outer, text="CMS Login", padding=10)
        creds.pack(fill="x")

        ttk.Label(creds, text="Username").grid(row=0, column=0, sticky="w", padx=(0, 8), pady=4)
        self.username_var = tk.StringVar()
        ttk.Entry(creds, textvariable=self.username_var, width=30).grid(row=0, column=1, sticky="ew", pady=4)

        ttk.Label(creds, text="Password").grid(row=1, column=0, sticky="w", padx=(0, 8), pady=4)
        self.password_var = tk.StringVar()
        ttk.Entry(creds, textvariable=self.password_var, width=30, show="*").grid(row=1, column=1, sticky="ew", pady=4)
        creds.columnconfigure(1, weight=1)

        tools = ttk.LabelFrame(outer, text="Quick tools", padding=10)
        tools.pack(fill="x", pady=(10, 0))
        ttk.Label(tools, text="Claim Number").grid(row=0, column=0, sticky="w", padx=(0, 8), pady=4)
        self.claim_number_var = tk.StringVar()
        ttk.Entry(tools, textvariable=self.claim_number_var, width=20).grid(row=0, column=1, sticky="w", pady=4)

        ttk.Label(tools, text="Customer").grid(row=1, column=0, sticky="w", padx=(0, 8), pady=4)
        self.customer_name_var = tk.StringVar()
        ttk.Entry(tools, textvariable=self.customer_name_var, width=32).grid(row=1, column=1, sticky="ew", pady=4)

        ttk.Label(tools, text="Claim ID").grid(row=2, column=0, sticky="w", padx=(0, 8), pady=4)
        self.claim_id_var = tk.StringVar()
        ttk.Entry(tools, textvariable=self.claim_id_var, width=20).grid(row=2, column=1, sticky="w", pady=4)

        ttk.Label(tools, text="Claimant").grid(row=3, column=0, sticky="w", padx=(0, 8), pady=4)
        self.claimant_name_var = tk.StringVar()
        ttk.Entry(tools, textvariable=self.claimant_name_var, width=32).grid(row=3, column=1, sticky="ew", pady=4)
        tools.columnconfigure(1, weight=1)

        actions = ttk.Frame(outer)
        actions.pack(fill="x", pady=(10, 10))
        self.run_btn = ttk.Button(actions, text="Run Full FCM Flow", command=self.run_full_flow)
        self.run_btn.pack(side="left")
        ttk.Button(actions, text="Run ReOpenCheck", command=self.run_reopen_only).pack(side="left", padx=(8, 0))
        ttk.Button(actions, text="Run CustomerChecker", command=self.run_customer_only).pack(side="left", padx=(8, 0))
        ttk.Button(actions, text="Bring UI to Front", command=self.bring_to_front).pack(side="left", padx=(8, 0))
        ttk.Button(actions, text="Close CMS Browser", command=self.close_browser).pack(side="left", padx=(8, 0))
        ttk.Button(actions, text="Clear Log", command=self.clear_log).pack(side="left", padx=(8, 0))

        note = ttk.LabelFrame(outer, text="What changed", padding=10)
        note.pack(fill="x")
        ttk.Label(
            note,
            text=(
                "This build uses one shared CMS Edge IE-mode session for FCM, ReOpenCheck, and CustomerChecker. "
                "The username and password come from this UI and no longer need to be hardcoded inside those scripts."
            ),
            wraplength=980,
            justify="left",
        ).pack(anchor="w")

        log_frame = ttk.LabelFrame(outer, text="Log", padding=8)
        log_frame.pack(fill="both", expand=True, pady=(10, 0))
        self.log_widget = tk.Text(log_frame, wrap="word")
        scroll = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_widget.yview)
        self.log_widget.configure(yscrollcommand=scroll.set)
        self.log_widget.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

    def bring_to_front(self):
        try:
            self.root.deiconify()
        except Exception:
            pass
        self.root.lift()
        self.root.focus_force()
        self.root.attributes("-topmost", True)
        self.root.after(400, lambda: self.root.attributes("-topmost", False))

    def close_browser(self):
        cms_session.close_shared_driver()
        self.log("[INFO] Shared CMS browser closed.")

    def get_context(self):
        return BotContext(
            cms_username=self.username_var.get().strip(),
            cms_password=self.password_var.get(),
        )

    def show_info(self, title: str, text: str):
        self.bring_to_front()
        messagebox.showinfo(title, text, parent=self.root)

    def clear_log(self):
        self.log_widget.delete("1.0", "end")

    def log(self, message: str):
        self.log_queue.put(message.rstrip("\n") + "\n")

    def _drain_log_queue(self):
        try:
            while True:
                item = self.log_queue.get_nowait()
                self.log_widget.insert("end", item)
                self.log_widget.see("end")
        except queue.Empty:
            pass
        self.root.after(100, self._drain_log_queue)

    def _run_with_redirect(self, target, *args):
        writer = QueueWriter(self.log_queue)
        try:
            with contextlib.redirect_stdout(writer), contextlib.redirect_stderr(writer):
                target(*args)
        except Exception as exc:
            self.log(f"[ERROR] {exc}")
        finally:
            self.root.after(0, lambda: self.run_btn.config(state="normal"))

    def run_full_flow(self):
        context = self.get_context()
        self.run_btn.config(state="disabled")
        threading.Thread(target=self._run_with_redirect, args=(run_fcm, self, context), daemon=True).start()

    def run_reopen_only(self):
        context = self.get_context()
        threading.Thread(
            target=self._run_with_redirect,
            args=(run_reopen_check, self, context, self.claim_number_var.get().strip()),
            daemon=True,
        ).start()

    def run_customer_only(self):
        context = self.get_context()
        threading.Thread(
            target=self._run_with_redirect,
            args=(
                run_customer_check,
                self,
                context,
                self.customer_name_var.get().strip(),
                self.claim_id_var.get().strip(),
                self.claimant_name_var.get().strip(),
            ),
            daemon=True,
        ).start()

    def run(self):
        self.root.mainloop()
