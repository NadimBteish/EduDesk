from http import cookies
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse
import html
import mimetypes
import os
import secrets


ROOT = Path(__file__).resolve().parent
PORT = int(os.environ.get("PORT", "5174"))
SESSIONS = {}

SCHOOL_DOMAINS = (
    ".edu",
    ".ac.uk",
    ".sch.uk",
    ".k12.",
    "school",
    "academy",
    "college",
    "university",
    "trust",
)


LOGIN_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>EduDesk AI - Sign in</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Hanken+Grotesk:wght@400;500;600;700;800&family=Newsreader:ital,opsz@1,18..72&display=swap" rel="stylesheet">
<style>
  :root{--primary:#2B5AD4;--accent:#E8845A;--ink:#15203A;--soft:#56606E;--bg:#F7F5F1;--line:rgba(21,32,58,.12)}
  *{box-sizing:border-box}
  body{margin:0;min-height:100vh;font-family:'Hanken Grotesk',system-ui,-apple-system,sans-serif;color:var(--ink);background:var(--bg)}
  .shell{min-height:100vh;display:grid;grid-template-columns:1.05fr .95fr}
  .story{position:relative;overflow:hidden;background:#15203A;color:#fff;padding:44px clamp(28px,5vw,72px);display:flex;flex-direction:column;justify-content:space-between}
  .story:before{content:"";position:absolute;inset:auto -20% -35% auto;width:620px;height:620px;border-radius:50%;background:rgba(43,90,212,.32);filter:blur(6px)}
  .brand{position:relative;display:flex;align-items:center;gap:12px;font-weight:800;font-size:20px}
  .mark{width:38px;height:38px;border-radius:10px;background:var(--primary);display:grid;place-items:center}
  .mark span{width:15px;height:15px;border:3px solid #fff;border-radius:5px}
  .hero{position:relative;max-width:620px;margin:70px 0}
  .eyebrow{display:inline-flex;align-items:center;gap:9px;border:1px solid rgba(255,255,255,.16);border-radius:999px;padding:7px 13px;color:#CFD8EA;font-size:13px;font-weight:700;margin-bottom:24px}
  .eyebrow:before{content:"";width:8px;height:8px;border-radius:999px;background:#2E8B57;box-shadow:0 0 0 5px rgba(46,139,87,.16)}
  h1{font-size:clamp(42px,5vw,68px);line-height:1.02;letter-spacing:-.03em;margin:0 0 22px;font-weight:800;text-wrap:balance}
  .mission{font-size:clamp(17px,1.7vw,21px);line-height:1.55;color:#CFD8EA;max-width:560px;margin:0}
  .proof{position:relative;display:grid;grid-template-columns:repeat(3,1fr);gap:14px}
  .proof div{background:rgba(255,255,255,.07);border:1px solid rgba(255,255,255,.1);border-radius:16px;padding:17px}
  .proof b{display:block;font-size:26px;letter-spacing:-.03em;margin-bottom:4px}
  .proof span{font-size:13px;color:#B9C5D8;line-height:1.35}
  .panel{padding:34px clamp(22px,4vw,64px);display:grid;place-items:center}
  .card{width:min(100%,470px);background:#fff;border:1px solid var(--line);border-radius:24px;padding:34px;box-shadow:0 28px 70px -48px rgba(21,32,58,.45)}
  .card h2{font-size:30px;line-height:1.1;letter-spacing:-.025em;margin:0 0 10px}
  .sub{margin:0 0 28px;color:var(--soft);font-size:15.5px;line-height:1.55}
  label{display:block;font-size:13.5px;font-weight:700;margin-bottom:8px;color:#1B2230}
  input{width:100%;height:52px;border:1px solid rgba(21,32,58,.18);border-radius:14px;padding:0 15px;font:600 15px 'Hanken Grotesk',system-ui;color:#1B2230;outline:none;background:#FBFAF8}
  input:focus{border-color:var(--primary);box-shadow:0 0 0 4px rgba(43,90,212,.11);background:#fff}
  .hint{display:flex;gap:9px;align-items:flex-start;margin:12px 0 22px;color:#697384;font-size:13.5px;line-height:1.45}
  .hint svg{flex:none;margin-top:2px}
  .error{background:#FFF1ED;border:1px solid rgba(201,82,46,.22);color:#A4432E;border-radius:12px;padding:11px 13px;font-size:13.5px;font-weight:600;margin-bottom:16px}
  button{width:100%;height:52px;border:none;border-radius:14px;background:var(--primary);color:#fff;font:700 15.5px 'Hanken Grotesk',system-ui;cursor:pointer;box-shadow:0 14px 28px -16px var(--primary)}
  button:hover{filter:brightness(1.04)}
  .demo{margin-top:18px;border-top:1px solid rgba(21,32,58,.08);padding-top:17px}
  .demo p{font-size:13px;color:#8A93A0;margin:0 0 10px}
  .demo button{height:38px;background:#F2F5FC;color:#2B5AD4;box-shadow:none;border:1px solid rgba(43,90,212,.14);font-size:13.5px}
  .small{margin-top:22px;font-size:12.5px;color:#8A93A0;line-height:1.5}
  .small a{color:var(--primary);font-weight:700;text-decoration:none}
  @media (max-width:900px){.shell{grid-template-columns:1fr}.story{min-height:44vh}.proof{grid-template-columns:1fr 1fr 1fr}.hero{margin:54px 0}.panel{padding:24px}.card{padding:26px}}
  @media (max-width:560px){.proof{grid-template-columns:1fr}.story{padding:28px 22px}.card{border-radius:18px}}
</style>
</head>
<body>
<main class="shell">
  <section class="story">
    <div class="brand"><span class="mark"><span></span></span>EduDesk AI</div>
    <div class="hero">
      <div class="eyebrow">Secure school access</div>
      <h1>Classroom support, ready before the lesson slips.</h1>
      <p class="mission">Make every classroom run seamlessly, so educators can focus on what matters most - their students.</p>
    </div>
    <div class="proof">
      <div><b>24s</b><span>average demo resolution for everyday issues</span></div>
      <div><b>71%</b><span>resolved instantly without waiting for IT</span></div>
      <div><b>3.2h</b><span>teacher time recovered this week</span></div>
    </div>
  </section>
  <section class="panel">
    <form class="card" method="post" action="/login">
      <h2>Sign in with your school email</h2>
      <p class="sub">Use an institution email to open the EduDesk AI teacher dashboard. This demo checks the email format only.</p>
      __ERROR__
      <label for="email">School email</label>
      <input id="email" name="email" type="email" placeholder="sarah.carter@oakfield.edu" value="__EMAIL__" autocomplete="email" required autofocus>
      <div class="hint">
        <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="#2E8B57" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3 5 6v5c0 4.4 3 7.6 7 9 4-1.4 7-4.6 7-9V6l-7-3z"/></svg>
        <span>For the presentation, any realistic school, college, or university email will open the demo.</span>
      </div>
      <button type="submit">Continue to dashboard</button>
      <div class="demo">
        <p>Need a sample for the pitch?</p>
        <button type="button" onclick="document.getElementById('email').value='sarah.carter@oakfield.edu'">Use demo teacher account</button>
      </div>
      <p class="small">Looking for the marketing site? <a href="/edudesk-ai.html">View EduDesk AI</a></p>
    </form>
  </section>
</main>
</body>
</html>"""


def is_school_email(email):
    value = email.strip().lower()
    if "@" not in value or value.startswith("@") or value.endswith("@"):
        return False
    domain = value.rsplit("@", 1)[1]
    return "." in domain and any(marker in domain for marker in SCHOOL_DOMAINS)


def session_from(headers):
    raw = headers.get("Cookie", "")
    jar = cookies.SimpleCookie(raw)
    token = jar.get("edudesk_session")
    if not token:
        return None
    return SESSIONS.get(token.value)


def login_page(email="", error=""):
    error_html = ""
    if error:
        error_html = f'<div class="error">{html.escape(error)}</div>'
    return LOGIN_PAGE.replace("__ERROR__", error_html).replace("__EMAIL__", html.escape(email))


class EduDeskHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print("%s - %s" % (self.address_string(), fmt % args))

    def send_html(self, body, status=200, headers=None):
        data = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        if headers:
            for key, value in headers.items():
                self.send_header(key, value)
        self.end_headers()
        self.wfile.write(data)

    def redirect(self, location, headers=None):
        self.send_response(303)
        self.send_header("Location", location)
        if headers:
            for key, value in headers.items():
                self.send_header(key, value)
        self.end_headers()

    def serve_file(self, name):
        target = (ROOT / name).resolve()
        if ROOT not in target.parents and target != ROOT:
            self.send_error(404)
            return
        if not target.exists() or not target.is_file():
            self.send_error(404)
            return
        data = target.read_bytes()
        content_type = mimetypes.guess_type(str(target))[0] or "application/octet-stream"
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        path = urlparse(self.path).path
        if path in ("/", "/login"):
            if session_from(self.headers):
                self.redirect("/dashboard.html")
                return
            self.send_html(login_page())
            return
        if path == "/logout":
            header = "edudesk_session=; Path=/; Max-Age=0; SameSite=Lax"
            self.redirect("/", {"Set-Cookie": header})
            return
        if path in ("/dashboard", "/dashboard.html"):
            if not session_from(self.headers):
                self.redirect("/")
                return
            self.serve_file("dashboard.html")
            return
        if path in ("/landing", "/edudesk-ai.html"):
            self.serve_file("edudesk-ai.html")
            return
        if path == "/EduDesk%20AI.dc.html":
            self.serve_file("EduDesk AI.dc.html")
            return
        clean = path.lstrip("/")
        if clean in {"support.js", ".thumbnail"} or clean.startswith("dist/"):
            self.serve_file(clean)
            return
        self.send_error(404)

    def do_POST(self):
        path = urlparse(self.path).path
        if path != "/login":
            self.send_error(404)
            return
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length).decode("utf-8")
        email = parse_qs(body).get("email", [""])[0].strip()
        if not is_school_email(email):
            self.send_html(
                login_page(email, "Please use a school, college, or university email address."),
                status=400,
            )
            return
        token = secrets.token_urlsafe(32)
        SESSIONS[token] = {"email": email}
        header = f"edudesk_session={token}; Path=/; HttpOnly; SameSite=Lax"
        self.redirect("/dashboard.html", {"Set-Cookie": header})


if __name__ == "__main__":
    try:
        server = ThreadingHTTPServer(("localhost", PORT), EduDeskHandler)
        print(f"EduDesk AI running at http://localhost:{PORT}/")
        print("Press Ctrl+C to stop.")
        server.serve_forever()
    except Exception as exc:
        (ROOT / "edudesk-app-startup-error.log").write_text(str(exc), encoding="utf-8")
        raise
