"""Run a scripts/browser/*.js snippet in the logged-in Playwright session and save its result.

The snippet is evaluated with CDP REPL semantics (top-level await, last expression is the
result), the same semantics the snippets were written for (the built-in browser's javascript_tool,
which can no longer open the UW login domain).

Usage:
  python scripts/pw_run.py <snippet.js> <out.json> [--url URL] [--pre "window.LIST_ONLY=true"]

  --url  navigate there first (otherwise runs on the session's current page)
  --pre  JS run before the snippet (e.g. set window.SKIP_DATES)

Exit codes: 0 ok; 3 login expired (nothing written: login expired != no data); 1 other error.

Login lives outside the repo (both files hold bearer cookies): PW_PROFILE (Duo device trust)
and PW_STATE (UW/Canvas *session* cookies, which a browser restart would drop). If the `uw`
session is not open, it is opened headless and PW_STATE is loaded; after a successful run the
state is saved back. When login has expired, the user logs in themselves (never type the
password for them):
  python scripts/pw_run.py --login [source ...]     (default: every source in LOGIN_URLS)
then signs in (and clicks Canvas "Authorize" for Panopto) in the Chrome window tabs, and the
caller runs `python scripts/pw_run.py --save`.
"""
import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

SESSION = "uw"
PW_PROFILE = Path.home() / ".fall-2026" / "pw-profile"
LOGIN_HOSTS = ("idp.u.washington.edu", "login.microsoftonline.com", "/login/oauth2/confirm",
               "piazza.com/account/login")
LOGIN_URLS = {
    "canvas": "https://canvas.uw.edu/courses/1917398",
    "sharepoint": "https://uwnetid.sharepoint.com/sites/og_EEP_524_A_B_-_GPU_Computing/Shared%20Documents/Forms/AllItems.aspx",
    "panopto": "https://uw.hosted.panopto.com/Panopto/Pages/Home.aspx",
    "piazza": "https://piazza.com/class/muomkq9jzdj104",
}
PW_STATE = Path.home() / ".fall-2026" / "uw-state.json"
TMP = Path(__file__).resolve().parent.parent / "state" / "_pw_run.tmp"


def cli(*args):
    exe = shutil.which("playwright-cli")
    if not exe:
        sys.exit("playwright-cli not found: npm install -g @playwright/cli@latest")
    r = subprocess.run([exe, f"-s={SESSION}", *args], capture_output=True, text=True,
                       encoding="utf-8")
    if r.returncode != 0 or "is not open" in r.stdout:
        sys.exit(f"playwright-cli {args[0]} failed (browser not open? see PW_PROFILE in "
                 f"{Path(__file__).name}):\n{r.stdout}{r.stderr}")
    return r.stdout


def is_open():
    return f"- {SESSION}:\n  - status: open" in cli("list").replace("\r", "")


def ensure_open():
    if is_open():
        return
    cli("open", f"--profile={PW_PROFILE}")
    if PW_STATE.exists():
        cli("state-load", str(PW_STATE))


def main():
    if sys.argv[1:2] == ["--login"]:
        urls = [LOGIN_URLS[k] for k in (sys.argv[2:] or LOGIN_URLS)]
        if is_open():
            cli("close")
        cli("open", "--headed", f"--profile={PW_PROFILE}")
        if PW_STATE.exists():
            cli("state-load", str(PW_STATE))
        cli("goto", urls[0])
        for u in urls[1:]:
            cli("tab-new", u)
        print("Chrome window open: the user signs in on each tab, then run: python scripts/pw_run.py --save")
        return
    if sys.argv[1:] == ["--save"]:
        cli("state-save", str(PW_STATE))
        print("saved login state to", PW_STATE)
        return

    ap = argparse.ArgumentParser()
    ap.add_argument("snippet")
    ap.add_argument("out")
    ap.add_argument("--url")
    ap.add_argument("--pre", default="")
    a = ap.parse_args()

    src = a.pre + ";\n" + Path(a.snippet).read_text(encoding="utf-8")
    nav = f"await page.goto({json.dumps(a.url)});" if a.url else ""
    TMP.write_text(f"""async page => {{
  {nav}
  const c = await page.context().newCDPSession(page);
  const r = await c.send('Runtime.evaluate', {{expression: {json.dumps(src)},
    replMode: true, awaitPromise: true, returnByValue: true}});
  return {{href: page.url(), value: r.result.value,
    error: r.exceptionDetails && (r.exceptionDetails.exception || {{}}).value
      || r.exceptionDetails && r.exceptionDetails.text}};
}}""", encoding="utf-8")
    ensure_open()
    try:
        res = json.loads(cli("run-code", "--raw", f"--filename={TMP}"))
    finally:
        TMP.unlink(missing_ok=True)

    err = res.get("error")
    if any(h in res["href"] for h in LOGIN_HOSTS) or (isinstance(err, str) and "LOGIN_EXPIRED" in err):
        print(f"LOGIN_EXPIRED: {res['href'].split('?')[0]}  (nothing written)")
        sys.exit(3)
    if err:
        print(f"snippet error: {err}")
        sys.exit(1)
    cli("state-save", str(PW_STATE))  # keep refreshed session cookies for the next restart
    Path(a.out).write_text(json.dumps(res["value"], ensure_ascii=False), encoding="utf-8")
    v = res["value"]
    print("saved", a.out, "keys:", list(v) if isinstance(v, dict) else type(v).__name__)


if __name__ == "__main__":
    main()
