# LeNinja — Discord EVs Generator

```
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   ██╗     ███████╗███╗   ██╗██╗███╗   ██╗     ██╗ █████╗     ║
║   ██║     ██╔════╝████╗  ██║██║████╗  ██║     ██║██╔══██╗    ║
║   ██║     █████╗  ██╔██╗ ██║██║██╔██╗ ██║     ██║███████║    ║
║   ██║     ██╔══╝  ██║╚██╗██║██║██║╚██╗██║██   ██║██╔══██║    ║
║   ███████╗███████╗██║ ╚████║██║██║ ╚████║╚█████╔╝██║  ██║    ║
║   ╚══════╝╚══════╝╚═╝  ╚═══╝╚═╝╚═╝  ╚═══╝ ╚════╝ ╚═╝  ╚═╝    ║
║                                                               ║
║          Discord EVs Generator · AI CAPTCHA v1.0              ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
```

An educational browser-automation project that walks a real Chromium
window through Discord's registration flow while producing legible,
diagnostic-first logs so every failure names its own cause.

> **Educational use only.** This project exists so people can learn how
> browser automation, CDP hooks, and modern anti-bot systems interact.
> Use it against services you own or on accounts you're authorized to
> create. Respect the ToS of any service you point it at, and don't use
> it to spam, scam, farm, or harass.

---

## Table of contents

- [What's in the box](#whats-in-the-box)
- [Quick start](#quick-start)
- [How it works](#how-it-works)
- [Configuration reference](#configuration-reference)
- [Mail providers](#mail-providers)
- [CAPTCHA solver chain](#captcha-solver-chain)
- [Proxy pool](#proxy-pool)
- [Fingerprints](#fingerprints)
- [Concurrent workers](#concurrent-workers)
- [Persistent logs and run summary](#persistent-logs-and-run-summary)
- [Troubleshooting](#troubleshooting)
- [Project layout](#project-layout)
- [License](#license)

---

## What's in the box

- **Multi-provider mail integration** — Cybertemp, Hotmail007, Zeus-X,
  Afham, DuckMail, CrowMail behind one interface.
- **Pluggable CAPTCHA solver chain** — browser extension first, then
  optional Groq and Claude vision-model fallbacks for text CAPTCHAs.
- **Proxy pool** — parallel startup health check, round-robin rotation,
  automatic retirement of proxies after two consecutive failures.
- **Concurrent workers** — run N account attempts in parallel; each
  worker owns its own browser, proxy, and fingerprint.
- **Real-time Discord response detector** — a CDP hook watches
  `/api/v9/auth/register` responses and names the exact rejection
  reason (captcha token invalid, rate limit, sitekey mismatch, ...).
- **25-fingerprint default pool** — realistic Chrome fingerprints so
  every account uses a distinct one out of the box.
- **Humanized typing** — 40–120 ms per keystroke with occasional
  "think" pauses; 200–500 ms between fields.
- **Persistent logs** — every console line mirrors to a rotating
  `logs/leninja.log` (5 MB × 10 files).
- **End-of-run summary** — attempts, valid/locked/invalid, per-provider
  and per-proxy success ratios, top-N failure reasons, solver stats.
- **Broad browser detection** — Brave, Chrome, Chromium, or Edge on
  Windows / macOS / Linux (including `PLAYWRIGHT_BROWSERS_PATH`).
- **Hard timeouts** — per-attempt (240 s) and browser-launch (45 s)
  caps so a stall never wedges the whole run.

---

## Quick start

```bash
# 1. Install
pip install -r requirements.txt

# 2. Configure
edit config/config.yaml            # set API keys, workers, proxy toggle
edit config/nopecha.txt            # one Nopecha key per line
edit input/proxies.txt             # optional: one proxy per line

# 3. Run
python main.py                     # interactive prompts
python main.py 10                  # generate 10 accounts
python main.py 25 3                # generate 25 accounts with 3 workers
```

**First run** downloads the LeNinja/Nopecha CRX extension into
`extension/nopecha_ext/` automatically. You'll need a Chromium-family
browser installed — the tool auto-detects Brave, Chrome, Chromium, or
Edge (see [Configuration reference](#configuration-reference) for
overriding the pick).

---

## How it works

Startup:

1. **Config loaded and validated.** Missing yaml, non-int `vpn_delay`,
   etc. abort with a specific error before anything else happens.
2. **Browser detected.** First installed Chromium-family binary wins;
   log line names which one.
3. **Proxy pool health-checked.** Each proxy pinged against
   `api.ipify.org` in parallel; dead ones dropped. `proxies: 4/5 alive`.
4. **Nopecha keys audited.** Every key in `config/nopecha.txt` pinged
   against the Nopecha status API; balance/plan/expiry logged per key.
   Zero-live keys triggers an explicit `hCaptcha will never solve`
   error before the first attempt runs.
5. **Extension key injected** into `manifest.json`, `settings.json`,
   and the extension's compiled JS bundles.
6. **Captcha chain built** — extension always first, Groq and Claude
   join only when their key is set AND their SDK is installed.

Per account:

1. **Fingerprint chosen** — one-time-use from `input/fp.txt`, otherwise
   round-robin from the 25-line default pool.
2. **Proxy claimed** from the pool via round-robin over alive set.
3. **Chromium launched** with extension, fingerprint args, and proxy.
   Wrapped in a 45 s timeout with one retry.
4. **CDP register-watcher attached** — listens to
   `/api/v9/auth/register` responses so any Discord rejection reason
   surfaces immediately.
5. **Mailbox created** via the chosen provider.
6. **Form filled** with humanized typing (per-key jitter + inter-field
   pauses).
7. **CAPTCHA handled** — solver chain kicks in when a challenge
   appears; extension solves invisibly first, then AI vision fallbacks
   for text CAPTCHAs.
8. **Email verified** — inbox polled for a Discord verify link, which
   is opened in the same tab.
9. **Token extracted** by an injected JS snippet that reads Discord's
   webpack store, then validated via `/users/@me`.
10. **Result recorded** in `RunMetrics` and reported to `ProxyPool`
    (success clears the proxy's failure counter; failure demotes it).

End of run:

```
═══════════════════════════════════════════════════════════════
                     RUN SUMMARY
═══════════════════════════════════════════════════════════════
  attempts   : 6
  valid      : 5
  locked     : 0
  invalid    : 1
  elapsed    : 121.3s (avg per attempt: 42.7s)
  per provider :
    Hotmail      5/6
  per proxy    :
    198.44.24.9:1080      3/3
    172.16.10.5:8080      2/2
    45.61.180.14:8080     0/1
  top failures :
      1x  rate-limited (bad proxy reputation)
  captcha      : extension: 4/5 | claude: 1/1
═══════════════════════════════════════════════════════════════
```

---

## Configuration reference

Everything lives in `config/config.yaml`. Keys marked *optional* fall
back to sensible defaults.

| Key                          | Default | Description |
|------------------------------|---------|-------------|
| `vpn`                        | `false` | Enable Mullvad IP rotation between attempts. Disabled when `workers > 1`. |
| `vpn_delay`                  | `120`   | Cooldown seconds between serial attempts. |
| `workers`                    | `1`     | Parallel account attempts. Also overridable via `python main.py <target> <workers>`. |
| `attempt_timeout`            | `240`   | Hard cap per attempt (seconds). Stalled browsers get killed. |
| `browser`                    | `""`    | Prefer `brave` / `chrome` / `chromium` / `edge`; empty = auto. |
| `captcha_extension_wait`     | `60`    | How long the extension solver waits before falling through. |
| `groq_key`                   | `""`    | Optional Groq API key for AI fallback. |
| `groq_model`                 | `""`    | Override the built-in Groq vision model. |
| `anthropic_key`              | `""`    | Optional Anthropic API key for Claude vision fallback. |
| `anthropic_model`            | `""`    | Override the built-in Claude model. |
| `cybertemp_key`              | `""`    | Cybertemp mail API key. |
| `hotmail007_key`             | `""`    | Hotmail007 broker client key. |
| `zeusx_key`                  | `""`    | Zeus-X broker API key. |
| `afham_mail_api9_key`        | `""`    | Afham mail API key. |
| `duckmail_key`               | `""`    | DuckMail bearer token (optional). |
| `crowmail_key`               | `""`    | CrowMail bearer token (optional). |
| `proxy.enabled`              | `false` | Read proxies from the file below. |
| `proxy.file`                 | `input/proxies.txt` | One proxy per line. |

Nopecha extension keys go in `config/nopecha.txt` (one per line, `#`
lines ignored). Fingerprints in `input/fp.txt` (JSON per line;
one-time-use). Empty lines and `#` comments are skipped.

---

## Mail providers

Choose one at run time with the interactive prompt (`C/H/Z/A/D/R`).

| Letter | Provider      | Backend                                        | Notes |
|--------|---------------|------------------------------------------------|-------|
| `C`    | Cybertemp     | `api.cybertemp.xyz`                            | Filters known-blacklisted domains. |
| `H`    | Hotmail007    | `gapi.hotmail007.com` → Microsoft OAuth        | Uses `MSGraphMailbox` base class. |
| `Z`    | Zeus-X        | `api.zeus-x.ru` → Microsoft OAuth              | Same shared OAuth flow. |
| `A`    | Afham         | `api.afhamxmailz.com`                          | Discord-safe domain filter. |
| `D`    | DuckMail      | `api.duckmail.sbs` (Hydra API)                 | `HydraMailProvider` base. |
| `R`    | CrowMail      | `api.crowmail.sbs` (Hydra API)                 | Same Hydra base. |

Every provider surfaces its own errors: missing key, network error,
HTTP status, application-level `code`/`msg`, empty stock, or malformed
account line. No more silent `mail failed`.

---

## CAPTCHA solver chain

Order of solvers is fixed: extension → Groq → Claude. Each is skipped
if its key isn't set (or its SDK isn't installed, with a specific
warning). Metrics track tries and wins per solver:

```
captcha solver stats -- extension: 3/5 | claude: 1/2
```

The AI fallbacks screenshot the visible challenge element, ask the
vision model to read the CAPTCHA text, and type the answer into the
CAPTCHA input. This works for text CAPTCHAs; hCaptcha's image-tile
challenge still relies on the extension.

If the extension appears to solve the challenge but Discord rejects
the resulting token, the register-watcher will log exactly why:

```
discord captcha rejection: discord rejected the captcha token
  (solver returned bad answer or token expired)
```

---

## Proxy pool

Add proxies to `input/proxies.txt` (one per line). Supported formats:

```
1.2.3.4:8080                              # host:port
user:pass@1.2.3.4:8080                    # authenticated
1.2.3.4:8080:user:pass                    # legacy broker format
http://user:pass@1.2.3.4:8080             # full URL
```

On startup every proxy is pinged in parallel against
`https://api.ipify.org` (5 s timeout, 20-way concurrent). Alive count
is logged: `proxies: 4/5 alive`. During the run, a proxy is retired
after two consecutive failures with a masked-address warning:

```
proxy retired after 2 failures: 45.61.180.14:8080
```

---

## Fingerprints

Two sources, checked in order:

1. **`input/fp.txt`** — user-supplied, one JSON dict per line, consumed
   after each account (one-time-use).
2. **`data/fingerprints_default.jsonl`** — 25 realistic Chrome
   fingerprints shipped with the repo (Win 10/11, macOS 14/15, Linux;
   Chrome 135–139; 8 different window sizes). Round-robin, never
   consumed.

Each fingerprint drives launch args (`--user-agent`, `--lang`,
`--window-size`) and a per-page JS override for
`navigator.userAgent/platform/languages/vendor/webdriver`.

---

## Concurrent workers

Set `workers: 3` in the config or pass it as the second CLI arg:

```bash
python main.py 30 3
```

Three workers claim from a shared attempt counter, each with its own
browser + proxy + fingerprint. Log lines are prefixed with `[w1]`,
`[w2]`, `[w3]`. Mullvad VPN rotation is disabled automatically when
`workers > 1` (single tunnel — can't rotate per worker).

**Trade-off:** N workers use N extension-key credits per attempt window
and N browser processes. Enable only when the proxy pool has that many
alive proxies and the Nopecha balance can afford it.

---

## Persistent logs and run summary

- Every `log_event` call mirrors to `logs/leninja.log` (rotating: 5 MB
  × 10 files). ANSI colors are stripped from the file version.
- End-of-run summary prints to both console (colorized) and log (plain).
- `logs/` is gitignored.

Failure reasons come from real diagnostic hooks (register-response
detector, provider errors, browser timeouts), so the top-N failures
line in the summary is actionable, not "unknown".

---

## Troubleshooting

The tool tries hard to name its own problems. Common ones:

| You see | Meaning |
|---------|---------|
| `all N nopecha keys are dead/exhausted` | Check balance at https://nopecha.com/manage. |
| `discord captcha rejection: invalid-input-response` | The extension solved it but Discord rejected the token. Usually a Nopecha key going bad or a proxy with poor reputation. |
| `discord rate-limited (429, retry after Xs)` | Cloudflare/Discord blocked the IP. Change proxy pool. |
| `proxies: 0/5 alive` | Your proxies are dead; check them independently against `https://api.ipify.org`. |
| `no Chromium-family browser found` | Install Brave, Chrome, Chromium, or Edge. |
| `attempt timed out after 240s` | Something wedged; per-attempt hard cap fired. Bump `attempt_timeout` if your proxy is slow. |
| `discord_info endpoint unreachable ... stale hardcoded build` | The build-metadata endpoint is down. If accounts start failing with "outdated client", bump the fallback constants in `main.py`. |
| `form field 'password' failed: ...` | Discord changed a form selector; the field name and exception are in the log. |

Everything is also in `logs/leninja.log` — grep it before asking for
help.

---

## Project layout

```
LeNinja-Discord-EVs-Gen/
├── main.py                     # Everything is in here
├── requirements.txt
├── config/
│   ├── config.yaml             # Runtime config (see reference above)
│   └── nopecha.txt             # Nopecha extension keys, one per line
├── input/
│   ├── fp.txt                  # Optional user fingerprints (one-time)
│   └── proxies.txt             # Optional proxies
├── data/
│   └── fingerprints_default.jsonl   # 25 fallback Chrome fingerprints
├── extension/
│   └── nopecha_ext/            # Auto-downloaded on first run
├── output/
│   ├── accounts.txt            # email:password:token for valid accts
│   ├── tokens.txt              # tokens only
│   └── locked.txt              # locked-account records
└── logs/
    └── leninja.log             # Rotating persistent log (gitignored)
```

---

## License

Educational purposes only. Use responsibly and in accordance with the
Terms of Service of any service you interact with. The maintainers do
not condone spam, harassment, ban-evasion, mass abuse, or any use that
violates a third party's ToS or applicable law.
