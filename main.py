import os
import sys
import subprocess
import shutil
import traceback
import random
import string
import re
import asyncio
import httpx
import tls_client
import time
import yaml
import warnings
import logging
import json
import base64
import email
import codecs
import datetime
from datetime import datetime
from dataclasses import dataclass, field
import threading
from threading import Thread
from pathlib import Path
from typing import Optional, Dict

from colorama import Fore, Style, init
from pystyle import Colors, Colorate, Center
import zipfile
import io
from pathlib import Path
from PIL import Image
import base64
from curl_cffi import requests

init(autoreset=True)


def is_domain_blacklisted(domain):
    if not domain:
        return False
    domain = domain.lower()
    blacklist_suffixes = [".store", ".ng"]
    blacklist_domains = ["cybertemp.xyz", "altmails.icu"]
    if domain in blacklist_domains:
        return True
    for suffix in blacklist_suffixes:
        if domain.endswith(suffix):
            return True
    return False
warnings.filterwarnings("ignore")
logging.getLogger().setLevel(logging.CRITICAL)


def log_event(level, message):
    ts = datetime.now().strftime("%H:%M:%S")
    labels = {
        "SUCCESS": Fore.LIGHTGREEN_EX + "COP" + Style.RESET_ALL,
        "ERROR":   Fore.RED    + "ERR" + Style.RESET_ALL,
        "INFO":    Fore.CYAN   + "INF" + Style.RESET_ALL,
        "WARNING": Fore.YELLOW + "WAR" + Style.RESET_ALL,
        "INPUT":   Fore.MAGENTA + "INP" + Style.RESET_ALL,
    }
    label = labels.get(level.upper(), level.upper())
    print(f"{Fore.LIGHTBLACK_EX}{ts}{Style.RESET_ALL}  {label}  {Fore.WHITE}{message}{Style.RESET_ALL}")


def log_token(token_masked):
    ts = datetime.now().strftime("%H:%M:%S")
    label = Fore.LIGHTGREEN_EX + "COP" + Style.RESET_ALL
    prefix = Fore.WHITE + "token: " + Style.RESET_ALL
    token_part = Fore.LIGHTBLACK_EX + token_masked + Style.RESET_ALL
    print(f"{Fore.LIGHTBLACK_EX}{ts}{Style.RESET_ALL}  {label}  {prefix}{token_part}")


def prompt_user(query):
    now = datetime.now().strftime("%H:%M:%S")
    formatted = f"{Fore.LIGHTBLACK_EX}{now}{Style.RESET_ALL}  {Fore.MAGENTA}INP{Style.RESET_ALL}  {Fore.WHITE}{query}{Style.RESET_ALL}"
    return input(formatted)


def install_requirements():
    if os.path.exists("requirements.txt"):
        choice = prompt_user("Do you want to install requirements? (y/n): ").strip().lower()
        if choice == 'y':
            log_event("INFO", "installing requirements, please wait...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
                log_event("SUCCESS", "requirements installed successfully!")
            except subprocess.CalledProcessError:
                log_event("ERROR", "failed to install requirements. please install them manually.")
        else:
            log_event("WARNING", "skipping requirements installation.")


install_requirements()


try:
    if sys.stdout and sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except AttributeError:
            sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    import asyncio
    import truedriver as uc
except Exception as e:
    with open("startup_error.txt", "w", encoding="utf-8") as f:
        f.write(f"IMPORT ERROR: {str(e)}\n\n")
        f.write(traceback.format_exc())
    log_event("ERROR", "fatal error during startup")
    log_event("ERROR", f"{str(e)}")
    log_event("INFO", "detailed log saved to 'startup_error.txt'")
    prompt_user("press enter to exit")
    sys.exit(1)


@dataclass
class UTILS_DISCORD:
    x_super_properties: dict = field(default_factory=dict)
    discord_user_agent: str = ""
    browser_user_agent: str = ""

    def __init__(self):
        self._scrape_info()
        Thread(target=self._scrape_info_loop, daemon=True).start()

    def _scrape_info(self):
        try:
            session = tls_client.Session(
                client_identifier="chrome_131",
                random_tls_extension_order=True
            )
            response = session.get("https://discord.eintim.dev/discord_info")
            if response.status_code == 200:
                details = response.json()
                self.discord_user_agent = details["desktop"]["user-agent"]
                self.browser_user_agent = details["browser"]["user-agent"]
                self.x_super_properties = details["desktop"]["decoded-x-super-properties"]
            else:
                self._set_fallback_values()
        except:
            self._set_fallback_values()

    def _set_fallback_values(self):
        self.discord_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) discord/1.0.9220 Chrome/128.0.6613.186 Electron/32.2.7 Safari/537.36"
        self.browser_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36"
        self.x_super_properties = {
            "os": "Windows",
            "browser": "Discord Client",
            "release_channel": "stable",
            "client_version": "1.0.9220",
            "os_version": "10.0.26100",
            "os_arch": "x64",
            "app_arch": "x64",
            "system_locale": "en-US",
            "has_client_mods": False,
            "browser_user_agent": self.discord_user_agent,
            "browser_version": "32.2.7",
            "os_sdk_version": "26100",
            "client_build_number": 485097,
            "native_build_number": 73818,
            "client_event_source": None
        }

    def _scrape_info_loop(self):
        while True:
            time.sleep(300)
            try:
                self._scrape_info()
            except:
                pass


def get_path(relative_path):
    if getattr(sys, 'frozen', False) or '__compiled__' in globals():
        base_path = os.path.dirname(os.path.abspath(sys.executable))
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


_UTILS_DISCORD = UTILS_DISCORD()
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False


LENINJA_EXT_ID = "dknlfmjaanfblgfdfebhijalfmhmjjjo"
LENINJA_EXT_DIR = Path(get_path("extension/nopecha_ext"))
LENINJA_KEYS_FILE = Path(get_path("config/nopecha.txt"))
FP_FILE = Path(get_path("input/fp.txt"))
_fp_lock = threading.Lock()
LENINJA_KEY_INDEX = 0


def load_leninja_keys() -> list:
    if not LENINJA_KEYS_FILE.exists():
        LENINJA_KEYS_FILE.parent.mkdir(parents=True, exist_ok=True)
        LENINJA_KEYS_FILE.write_text("")
        return []
    keys = []
    for line in LENINJA_KEYS_FILE.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith('#'):
            keys.append(line)
    return keys


def get_current_leninja_key() -> Optional[str]:
    keys = load_leninja_keys()
    if not keys:
        return None
    global LENINJA_KEY_INDEX
    return keys[LENINJA_KEY_INDEX % len(keys)]


def inject_leninja_key(api_key: str):
    if not api_key or not LENINJA_EXT_DIR.exists():
        return False
    ok = False

    # 1. Inject into manifest.json
    manifest_path = LENINJA_EXT_DIR / "manifest.json"
    try:
        if manifest_path.exists():
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)

            all_keys = load_leninja_keys()

            if 'nopecha' not in manifest:
                manifest['nopecha'] = {}
            manifest['nopecha']['key'] = api_key

            if all_keys:
                manifest['nopecha']['keys'] = all_keys

            with open(manifest_path, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent='	')
            ok = True
    except Exception as e:
        pass

    # 2. Inject into settings.json
    settings_path = LENINJA_EXT_DIR / "settings.json"
    try:
        settings = {}
        if settings_path.exists():
            with open(settings_path, 'r') as f:
                settings = json.load(f)
        settings['key'] = api_key
        with open(settings_path, 'w') as f:
            json.dump(settings, f)
        ok = True
    except:
        pass

    # 3. Patch JavaScript bundles
    replacement = f'key:me(ge(),{json.dumps(api_key)})'
    pattern = re.compile(r'key:me\(ge\(\),\"[^\"]*\"\)')
    try:
        for bundle_path in LENINJA_EXT_DIR.rglob("*.js"):
            try:
                bundle = bundle_path.read_text(encoding="utf-8", errors="ignore")
                new_bundle, count = pattern.subn(replacement, bundle, count=1)
                if count:
                    bundle_path.write_text(new_bundle, encoding="utf-8")
                    ok = True
            except:
                continue
    except:
        pass
    return ok
def download_leninja_ext() -> Optional[Path]:
    if LENINJA_EXT_DIR.exists() and (LENINJA_EXT_DIR / "manifest.json").exists():
        return LENINJA_EXT_DIR
    log_event("INFO", "downloading leninja extension (first run)...")
    crx_url = f"https://clients2.google.com/service/update2/crx?response=redirect&prodversion=120.0.0.0&acceptformat=crx2,crx3&x=id%3D{LENINJA_EXT_ID}%26uc"
    try:
        with httpx.Client(follow_redirects=True) as client:
            r = client.get(crx_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=60)
            if r.status_code != 200:
                log_event("ERROR", f"leninja download failed: HTTP {r.status_code}")
                return None
            data = r.content
        if data[:4] == b"Cr24":
            version = int.from_bytes(data[4:8], "little")
            zip_start = (12 + int.from_bytes(data[8:12], "little")) if version == 3 else (16 + int.from_bytes(data[8:12], "little") + int.from_bytes(data[12:16], "little"))
        else:
            zip_start = 0
        LENINJA_EXT_DIR.mkdir(exist_ok=True, parents=True)
        with zipfile.ZipFile(io.BytesIO(data[zip_start:])) as z:
            z.extractall(LENINJA_EXT_DIR)
        if (LENINJA_EXT_DIR / "manifest.json").exists():
            log_event("SUCCESS", "leninja extension installed")
            return LENINJA_EXT_DIR
        log_event("ERROR", "leninja extract failed: manifest.json missing")
        return None
    except Exception as e:
        log_event("ERROR", f"leninja download failed: {str(e)[:100]}")
        return None


async def setup_leninja(log_func=None):
    _l = log_func or log_event
    ext_path = download_leninja_ext()
    if not ext_path:
        _l("ERROR", "Failed to download LeNinja extension")
        return None
    current_key = get_current_leninja_key()
    if current_key:
        if inject_leninja_key(current_key):
            _l("SUCCESS", "leninja key injected")
        else:
            _l("WARNING", "leninja key could not be injected (check extension files)")
    else:
        _l("WARNING", "no leninja key in config/nopecha.txt - captcha solving will be limited")
    return ext_path


def get_brave_path() -> Optional[str]:
    paths = [
        r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
        r"C:\Program Files (x86)\BraveSoftware\Brave-Browser\Application\brave.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\BraveSoftware\Brave-Browser\Application\brave.exe"),
    ]
    for p in paths:
        if os.path.exists(p):
            return p
    return None


class GroqCaptchaSolver:
    def __init__(self, api_key: str):
        if not GROQ_AVAILABLE:
            raise ImportError("Groq not installed")
        self.client = Groq(api_key=api_key)
        self.model = "llama-3.2-90b-vision-preview"

    def solve_text_captcha(self, image_base64: str) -> Optional[str]:
        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_base64}"}},
                            {"type": "text", "text": "Extract ONLY the text from this CAPTCHA."}
                        ]
                    }
                ],
                temperature=0.1,
                max_tokens=100
            )
            return resp.choices[0].message.content.strip().replace('"', '').replace('.', '')
        except Exception as e:
            log_event("WARNING", f"groq captcha solve failed: {str(e)[:150]}")
            return None


JS_UTILS = '''
(() => {
    if (window.utils) return; 
    window.utils = {
        setInput: (s, v) => { const el = document.querySelector(s); if(el){ el.value=v; el.dispatchEvent(new Event('input',{bubbles:true})); el.dispatchEvent(new Event('change',{bubbles:true})); }},
        clickAllCheckboxes: () => { 
            const cbs = document.querySelectorAll('input[type="checkbox"]'); 
            let c=0; cbs.forEach(cb => { if(!cb.checked){ cb.click(); cb.checked=true; cb.dispatchEvent(new Event('change',{bubbles:true})); c++; }});
            return {clicked:c, total:cbs.length};
        },
        clickElement: (s) => { const el = document.querySelector(s); if(el) el.click(); }
    };
})();
'''


try:
    loop = asyncio.get_event_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)


loop.set_exception_handler(lambda loop, context: None)


async def animated_cooldown(total_seconds):
    import sys
    bar_width = 30
    start = time.time()
    while True:
        elapsed = time.time() - start
        remaining = max(0, total_seconds - elapsed)
        if total_seconds > 0:
            progress = min(elapsed / total_seconds, 1.0)
        else:
            progress = 1.0
        filled = round(bar_width * progress)
        bar_filled = Fore.LIGHTCYAN_EX + chr(9608) * filled + Style.RESET_ALL
        bar_empty = Fore.LIGHTBLACK_EX + chr(9617) * (bar_width - filled) + Style.RESET_ALL
        spin_chars = ['|', '/', '-', '\\']
        spin = Fore.LIGHTMAGENTA_EX + spin_chars[int(elapsed * 4) % len(spin_chars)] + Style.RESET_ALL
        label = Fore.LIGHTYELLOW_EX + 'Cooldown' + Style.RESET_ALL
        timer = Fore.LIGHTWHITE_EX + f'{remaining:.0f}s' + Style.RESET_ALL
        line = f'\r {spin} {label} [{bar_filled}{bar_empty}] {timer} remaining   '
        sys.stdout.write(line)
        sys.stdout.flush()
        if remaining <= 0:
            break
        await asyncio.sleep(0.15)
    done_line = f'\r {Fore.LIGHTGREEN_EX}+{Style.RESET_ALL} {Fore.LIGHTWHITE_EX}Cooldown complete{Style.RESET_ALL}' + ' ' * 40
    sys.stdout.write(done_line + '\n')
    sys.stdout.flush()


def print_stats_bar(valid, locked, invalid):
    total = valid + locked + invalid
    print(f"\r {Fore.LIGHTGREEN_EX}Valid: {valid} {Fore.LIGHTBLACK_EX}| {Fore.LIGHTYELLOW_EX}Locked: {locked} {Fore.LIGHTBLACK_EX}| {Fore.LIGHTRED_EX}Invalid: {invalid} {Fore.LIGHTBLACK_EX}| {Fore.LIGHTCYAN_EX}Total: {total}{Style.RESET_ALL}")


def set_console_title(title="LeNinja - Discord EVs Generator"):
    if os.name == 'nt':
        os.system(f"title {title}")
    else:
        try:
            stream = sys.__stdout__ or sys.stdout
            stream.write(f"\33]0;{title}\a")
            stream.flush()
        except Exception:
            pass


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def cleanup_resources():
    try:
        import gc
        gc.collect()
        try:
            import truedriver as uc
            uc.stop_all()
        except:
            pass
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            return
        tasks = [t for t in asyncio.all_tasks(loop) if not t.done()]
        for t in tasks:
            try: t.cancel()
            except: pass
        gc.collect()
    except:
        pass


async def shutdown_engine():
    try:
        import gc
        gc.collect()
        try:
            import truedriver as uc
            uc.stop_all()
        except:
            pass
        await asyncio.sleep(0.3)
        try:
            loop = asyncio.get_running_loop()
            tasks = [t for t in asyncio.all_tasks(loop) if not t.done()]
            for t in tasks:
                try: t.cancel()
                except: pass
        except RuntimeError:
            pass
        gc.collect()
    except:
        pass


def animate_text(text, speed=0.03):
    lines = text.split('\n')
    for line in lines:
        print(line)
        time.sleep(speed)


def apply_gradient(lines, color_start=(255, 0, 255), color_end=(0, 255, 255)):
    total = len(lines)
    result = []
    for i, line in enumerate(lines):
        r = color_start[0] + (color_end[0] - color_start[0]) * i // max(1, total - 1)
        g = color_start[1] + (color_end[1] - color_start[1]) * i // max(1, total - 1)
        b = color_start[2] + (color_end[2] - color_start[2]) * i // max(1, total - 1)
        result.append(f'\033[38;2;{r};{g};{b}m{line}\033[0m')
    return result


def show_interface():
    ascii_art = """
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
    """

    gradient_lines = apply_gradient(
        ascii_art.split('\n'),
        color_start=(138, 43, 226),    # Purple
        color_end=(0, 255, 255)         # Cyan
    )

    for line in gradient_lines:
        print(line)

    print()
    print(f"{Fore.LIGHTMAGENTA_EX}═══════════════════════════════════════════════════════════════{Style.RESET_ALL}")
    print(f"{Fore.LIGHTCYAN_EX}        Advanced Discord Account Generator & Solver{Style.RESET_ALL}")
    print(f"{Fore.LIGHTMAGENTA_EX}═══════════════════════════════════════════════════════════════{Style.RESET_ALL}")
    print()


async def fetch_discord_token(email: str, password: str, proxy_config: Dict = None) -> str:
    url = "https://discord.com/api/v9/auth/login"
    payload = {
        "login": email,
        "password": password,
        "undelete": False,
        "gift_code_sku_id": None,
        "login_source": None
    }
    
    headers = get_headers()
    
    session = tls_client.Session(
        client_identifier="chrome_131",
        random_tls_extension_order=True
    )
    
    if proxy_config:
        session.proxies = proxy_config

    try:
        response = session.post(
            url,
            headers=headers,
            json=payload,
            timeout_seconds=30
        )
        if response.status_code == 200:
            return response.json().get("token")
        else:
            log_event("ERROR", f"login failed: {response.status_code} - {response.text}")
    except Exception as e:
        log_event("ERROR", f"fetch token error: {str(e)}")
    return None


def get_headers():
    return {
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "content-type": "application/json",
        "origin": "https://discord.com",
        "priority": "u=1, i",
        "referer": "https://discord.com/channels/@me",
        "sec-ch-ua": '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
        "x-discord-timezone": "Asia/Calcutta",
        "x-super-properties": "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiQ2hyb21lIiwiZGV2aWNlIjoiIiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiaGFzX2NsaWVudF9tb2RzIjpmYWxzZSwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzEzNC4wLjAuMCBTYWZhcmkvNTM3LjM2IiwiYnJvd3Nlcl92ZXJzaW9uIjoiMTM0LjAuMC4wIiwib3NfdmVyc2lvbiI6IjEwIiwicmVmZXJyZXIiOiIiLCJyZWZlcnJpbmdfZG9tYWluIjoiIiwicmVmZXJyZXJfY3VycmVudCI6IiIsInJlZmVycmluZ19kb21haW5fY3VycmVudCI6IiIsInJlbGVhc2VfY2hhbm5lbCI6InN0YWJsZSIsImNsaWVudF9idWlsZF9udW1iZXIiOjM4NDg4NywiY2xpZW50X2V2ZW50X3NvdXJjZSI6bnVsbH0="
    }


def create_random_string(length=10):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


def make_handle():
    adjectives = [
        "dark", "cool", "epic", "mega", "ultra", "pro", "elite", "alpha",
        "sigma", "shadow", "void", "ghost", "neon", "cyber", "pixel", "frost",
        "lunar", "solar", "nova", "zen", "sky", "storm", "river", "mountain",
        "silent", "hidden", "lost", "mythic", "iron", "golden", "vivid"
    ]
    nouns = [
        "gamer", "warrior", "ninja", "king", "lord", "knight", "beast",
        "titan", "scout", "pilot", "vortex", "blade", "seeker", "walker",
        "hunter", "reaper", "phantom", "spirit", "dragon", "wolf", "raven"
    ]
    connectors = ["", "_", "."]
    name_parts = [random.choice(adjectives), random.choice(nouns)]
    if random.random() > 0.7:
        name_parts.insert(1, random.choice(adjectives))
    sep = random.choice(connectors)
    name = sep.join(name_parts)
    suffix = str(random.randint(1000, 999999))
    if random.random() > 0.5:
        name += random.choice(connectors) + suffix
    else:
        name += suffix
    return name[:32].lower()


def load_proxies(config: dict) -> list:
    proxy_enabled = config.get("proxy", {}).get("enabled", False)
    if not proxy_enabled:
        return []
    proxy_file = config.get("proxy", {}).get("file", "input/proxies.txt")
    proxy_path = Path(get_path(proxy_file))
    if not proxy_path.exists():
        return []
    try:
        with open(proxy_path, 'r', encoding='utf-8') as f:
            proxies = [line.strip() for line in f if line.strip()]
        if proxies:
            return proxies
        else:
            return []
    except Exception as e:
        return []


def get_random_proxy(proxies: list) -> str:
    if not proxies:
        return None
    return random.choice(proxies)


MULLVADEXE = None

MULLVADCOUNTRIES = [
    "us", "ca", "gb", "au", "de", "fr", "nl", "se", "no", "dk",
    "fi", "at", "be", "ie", "jp", "sg", "nz", "za"
]

MULLVADLAST_COUNTRY = None
MULLVADUSED_COUNTRIES = []


def findmullvad_cli():
    in_path = shutil.which("mullvad")
    if in_path:
        return in_path
    root = r"C:\Program Files\Mullvad VPN"
    candidates = [
        os.path.join(root, "mullvad.exe"),
        os.path.join(root, "resources", "bin", "mullvad.exe"),
        os.path.join(root, "resources", "mullvad.exe"),
        os.path.join(root, "bin", "mullvad.exe"),
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\Mullvad VPN\mullvad.exe"),
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\Mullvad VPN\resources\bin\mullvad.exe"),
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    return None


MULLVADEXE = findmullvad_cli()


def runmullvad(args, timeout=30):
    si = None
    cf = 0
    if os.name == "nt":
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        si.wShowWindow = 0
        cf = 0x08000000
    exe = MULLVADEXE or "mullvad"
    try:
        proc = subprocess.run(
            [exe, *args],
            capture_output=True,
            text=True,
            timeout=timeout,
            startupinfo=si,
            creationflags=cf if cf else 0
        )
        return proc.returncode, (proc.stdout or "").strip(), (proc.stderr or "").strip()
    except Exception as e:
        return -1, "", str(e)


def mullvadstatus():
    rc, out, _ = runmullvad(["status"], timeout=15)
    return rc, out


def mullvadis_connected(status_text):
    if not status_text:
        return False
    lower = status_text.lower()
    first_line = lower.splitlines()[0] if lower.splitlines() else lower
    return ("tunnel status: connected" in lower
            or (first_line.strip().startswith("connected") and "disconnected" not in first_line)
            or re.search(r"^\s*connected\b", lower, re.M))


def mullvadcountry_from_status(text):
    if not text:
        return None
    m = re.search(r"Relay\s+-\s+([A-Za-z]{2})", text)
    if m:
        return m.group(1).lower()
    m = re.search(r"Visible location:\s*([A-Za-z ]+),\s*([A-Za-z ]+)", text)
    if m:
        country_name = m.group(2).strip().lower()
        map_ = {
            "sweden": "se", "united states": "us", "usa": "us",
            "germany": "de", "netherlands": "nl", "france": "fr", "united kingdom": "gb",
            "england": "gb", "uk": "gb", "canada": "ca", "japan": "jp", "singapore": "sg",
            "australia": "au", "norway": "no", "denmark": "dk", "finland": "fi", "spain": "es",
            "italy": "it", "switzerland": "ch", "austria": "at", "belgium": "be", "ireland": "ie",
            "portugal": "pt", "poland": "pl", "czech republic": "cz", "romania": "ro",
            "new zealand": "nz", "brazil": "br", "india": "in", "south africa": "za",
            "hong kong": "hk", "turkey": "tr"
        }
        return map_.get(country_name)
    return None


def get_public_ip():
    urls = [
        "https://api.ipify.org?format=json",
        "https://ipinfo.io/json",
        "https://ifconfig.co/json",
        "https://am.i.mullvad.net/json"
    ]
    for url in urls:
        try:
            session = tls_client.Session(client_identifier="chrome_131", random_tls_extension_order=True)
            r = session.get(url, timeout_seconds=3)
            if r.status_code == 200:
                data = r.json()
                ip = data.get("ip")
                if ip and re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", ip):
                    return ip
        except:
            continue
    return None


def redact_ip(ip):
    if not ip:
        return "?.?.?.?"
    parts = ip.split(".")
    if len(parts) != 4:
        return ip
    parts[2] = "*"
    parts[3] = "*"
    return ".".join(parts)


def mullvadrandom_country():
    global MULLVADLAST_COUNTRY, MULLVADUSED_COUNTRIES
    avoid_count = min(8, max(0, len(MULLVADCOUNTRIES) - 1))
    avoid_set = set(MULLVADUSED_COUNTRIES[-avoid_count:]) if avoid_count else set()
    pool = [c for c in MULLVADCOUNTRIES if c not in avoid_set]
    if not pool:
        pool = MULLVADCOUNTRIES[:]
        MULLVADUSED_COUNTRIES = []
    pick = random.choice(pool)
    MULLVADLAST_COUNTRY = pick
    MULLVADUSED_COUNTRIES.append(pick)
    if len(MULLVADUSED_COUNTRIES) > 20:
        MULLVADUSED_COUNTRIES = MULLVADUSED_COUNTRIES[-12:]
    return pick


async def mullvad_ensure_connected():
    if not MULLVADEXE:
        log_event("ERROR", "mullvad cli not in path and not found in program files")
        return False
    rc, status = mullvadstatus()
    baseline_ip = get_public_ip()
    log_event("INFO", f"baseline ip: {redact_ip(baseline_ip)}")
    runmullvad(["lockdown-mode", "set", "on"], timeout=20)
    if mullvadis_connected(status):
        c = mullvadcountry_from_status(status)
        log_event("SUCCESS", f"mullvad already connected {redact_ip(baseline_ip)}" + (f" ({c})" if c else ""))
        return True
    log_event("INFO", "connecting mullvad vpn")
    rc, out, err = runmullvad(["connect"], timeout=45)
    last_shown_ip = None
    for i in range(1, 501):
        await asyncio.sleep(0.2)
        rc2, s = mullvadstatus()
        if i % 10 == 0 or not last_shown_ip:
            current_ip = get_public_ip()
            if current_ip != last_shown_ip:
                last_shown_ip = current_ip
        if mullvadis_connected(s):
            connected_count = 1
            for _verify in range(4):
                await asyncio.sleep(0.4)
                _rc, _s = mullvadstatus()
                if mullvadis_connected(_s):
                    connected_count += 1
            if connected_count >= 3:
                ip = last_shown_ip or get_public_ip()
                c = mullvadcountry_from_status(s)
                log_event("SUCCESS", f"mullvad connected {redact_ip(ip)}" + (f" ({c})" if c else ""))
                return True
    runmullvad(["lockdown-mode", "set", "off"], timeout=20)
    final_ip = get_public_ip()
    log_event("ERROR", f"mullvad failed to connect [{rc}]: {err or out} (final ip: {redact_ip(final_ip)})")
    return False


async def mullvad_cycle(old_ip=None, max_attempts=5):
    global MULLVADLAST_COUNTRY
    if not MULLVADEXE or not os.path.exists(MULLVADEXE):
        log_event("WARNING", "mullvad cli not found, falling back to 10s sleep")
        await asyncio.sleep(10)
        return None
    previous = old_ip or get_public_ip()
    last_ip = previous
    for attempt in range(1, max_attempts + 1):
        country = mullvadrandom_country()
        log_event("INFO", f"switching to {country} ({attempt}/{max_attempts})")
        rc, out, err = runmullvad(["relay", "set", "location", country])
        if rc != 0:
            runmullvad(["relay", "set", "location"])
        rc, out, err = runmullvad(["connect"])
        log_event("INFO", "connecting mullvad vpn")
        deadline = time.time() + 25
        new_ip = None
        last_shown = None
        poll_i = 0
        while time.time() < deadline:
            poll_i += 1
            await asyncio.sleep(0.3)
            new_ip = get_public_ip()
            if new_ip and new_ip != last_shown:
                last_shown = new_ip
            if new_ip and new_ip != last_ip:
                break
        if mullvadis_connected(mullvadstatus()[1]):
            if new_ip and new_ip != last_ip and new_ip != previous:
                log_event("SUCCESS", f"connected to {redact_ip(new_ip)} ({country})")
                return new_ip
            elif new_ip and new_ip != previous:
                log_event("SUCCESS", f"connected to {redact_ip(new_ip)} ({country})")
                return new_ip
        last_ip = new_ip or last_ip
        if attempt < max_attempts:
            log_event("WARNING", "ip unchanged, retrying with new country")
    final_ip = get_public_ip()
    log_event("ERROR", f"mullvad failed to change ip after {max_attempts} attempts (last seen: {redact_ip(final_ip)})")
    return last_ip if last_ip != previous else previous


async def rotate_mullvad_ip():
    if not MULLVADEXE:
        log_event("ERROR", "mullvad cli not found")
        return False
    current_ip = get_public_ip()
    new_ip = await mullvad_cycle(old_ip=current_ip, max_attempts=5)
    return new_ip is not None and new_ip != current_ip


_DISCORD_VERIFY_PATTERNS = [
    r'https?://(?:www\.)?discord\.com/verify\?token=[a-zA-Z0-9\-\._~%]+',
    r'https?://click\.discord\.com/ls/click\?upn=[a-zA-Z0-9\-\._~%]+',
]


def extract_discord_verify_link(content, min_length=50):
    if not content:
        return None
    text = str(content).replace("&amp;", "&").replace("&quot;", '"').replace("&#39;", "'")
    found = []
    for pattern in _DISCORD_VERIFY_PATTERNS:
        for url in re.findall(pattern, text, re.IGNORECASE):
            url = url.replace("\\/", "/").split("\n")[0].strip()
            url = re.sub(r"[.,;>]$", "", url)
            if len(url) > min_length:
                found.append(url)
    if not found:
        return None
    verify = [u for u in found if "discord.com/verify" in u]
    (verify or found).sort(key=len, reverse=True)
    return (verify or found)[0]


class MSGraphMailbox:
    """Base for brokers that hand back Microsoft refresh_tokens.

    Subclasses provide `create_inbox`; the OAuth token refresh and the
    Graph inbox scan are identical across every Microsoft-backed broker.
    """
    ms_client_id = "9e5f94bc-e8a4-4e73-b8be-63364c29d753"
    label = "mailbox"

    def __init__(self):
        self.email = None
        self.password = None
        self.refresh_token = None
        self.uuid = None

    async def get_access_token(self, r_token=None, c_id=None):
        token = (r_token or self.refresh_token or "").rstrip("$").strip()
        cid = (c_id or self.uuid or self.ms_client_id or "").strip()
        if not token:
            log_event("ERROR", f"{self.label}: missing refresh_token")
            return None
        data = {
            "client_id": cid,
            "refresh_token": token,
            "grant_type": "refresh_token",
            "scope": "https://graph.microsoft.com/.default",
        }
        try:
            async with httpx.AsyncClient() as client:
                r = await client.post(
                    "https://login.microsoftonline.com/common/oauth2/v2.0/token",
                    data=data, timeout=30,
                )
            if r.status_code == 200:
                return r.json().get("access_token")
            try:
                err = r.json()
                msg = err.get("error_description") or err.get("error") or r.text[:200]
            except Exception:
                msg = r.text[:200]
            log_event("ERROR", f"{self.label}: microsoft oauth {r.status_code}: {msg}")
        except Exception as e:
            log_event("ERROR", f"{self.label}: oauth request failed: {str(e)[:150]}")
        return None

    async def get_verification_url(self):
        if not self.refresh_token:
            return None
        access = await self.get_access_token()
        if not access:
            return None
        try:
            async with httpx.AsyncClient() as client:
                r = await client.get(
                    "https://graph.microsoft.com/v1.0/me/messages",
                    headers={"Authorization": f"Bearer {access}"},
                    params={"$top": 10, "$orderby": "receivedDateTime desc", "$select": "subject,body,from"},
                    timeout=15,
                )
            if r.status_code != 200:
                log_event("WARNING", f"{self.label}: graph {r.status_code}: {r.text[:150]}")
                return None
            for msg in r.json().get("value", []):
                subj = msg.get("subject", "").lower()
                from_data = msg.get("from", {}).get("emailAddress", {})
                frm_addr = from_data.get("address", "").lower()
                frm_name = from_data.get("name", "").lower()
                if not (("discord" in frm_addr or "discord" in frm_name)
                        and ("verify" in subj or "confirm" in subj or "verification" in subj)):
                    continue
                body = msg.get("body", {}).get("content", "") or ""
                link = extract_discord_verify_link(body)
                if link:
                    return link
                for tracked in re.findall(r'https://click\.discord\.com/ls/click\?[^\s"\'><]+', body):
                    try:
                        async with httpx.AsyncClient() as check_client:
                            res = await check_client.get(tracked, follow_redirects=False, timeout=10)
                            if "discord.com/verify" in res.headers.get("Location", ""):
                                return tracked
                    except Exception:
                        continue
        except Exception as e:
            log_event("WARNING", f"{self.label}: graph request failed: {str(e)[:150]}")
        return None


class HydraMailProvider:
    """Base for API-Platform 'Hydra' style mail brokers (DuckMail, CrowMail)."""
    api_base = ""
    label = "mailbox"

    def __init__(self, api_key=None, never_expire=False):
        self.email = None
        self.password = None
        self.api_key = api_key
        self.auth_token = None
        self.account_id = None
        self.never_expire = never_expire

    def _headers(self, content_type=False):
        h = {}
        if content_type:
            h["Content-Type"] = "application/json"
        if self.api_key:
            h["Authorization"] = f"Bearer {self.api_key}"
        return h

    def get_domains(self):
        try:
            response = requests.get(f"{self.api_base}/domains", headers=self._headers(), timeout=15, impersonate="chrome124")
        except Exception as e:
            log_event("ERROR", f"{self.label}: domains request failed: {str(e)[:150]}")
            return None
        if response.status_code != 200:
            log_event("ERROR", f"{self.label}: domains HTTP {response.status_code}: {response.text[:150]}")
            return None
        try:
            members = response.json().get("hydra:member", []) or []
        except Exception:
            log_event("ERROR", f"{self.label}: non-json domains response")
            return None
        valid = [item.get("domain") for item in members
                 if item.get("domain") and item.get("isVerified")
                 and not is_domain_blacklisted(item.get("domain"))]
        return valid or None

    async def create_inbox(self, session=None):
        domains = self.get_domains()
        if not domains:
            log_event("ERROR", f"{self.label}: no verified domains available")
            return None
        domain = random.choice(domains)
        user = "".join(random.choices(string.ascii_lowercase + string.digits, k=random.randint(10, 16)))
        self.email = f"{user}@{domain}"
        self.password = create_random_string(12)

        payload = {
            "address": self.email,
            "password": self.password,
            "expiresIn": 0 if self.never_expire else 86400,
        }
        try:
            create_resp = requests.post(
                f"{self.api_base}/accounts",
                headers=self._headers(content_type=True),
                json=payload, timeout=15, impersonate="chrome124",
            )
        except Exception as e:
            log_event("ERROR", f"{self.label}: account create failed: {str(e)[:150]}")
            return None
        if create_resp.status_code not in (200, 201):
            log_event("ERROR", f"{self.label}: account create HTTP {create_resp.status_code}: {create_resp.text[:200]}")
            return None

        try:
            token_resp = requests.post(
                f"{self.api_base}/token",
                headers={"Content-Type": "application/json"},
                json={"address": self.email, "password": self.password},
                timeout=15, impersonate="chrome124",
            )
        except Exception as e:
            log_event("ERROR", f"{self.label}: token request failed: {str(e)[:150]}")
            return None
        if token_resp.status_code == 200:
            td = token_resp.json()
            self.auth_token = td.get("token")
            self.account_id = td.get("id")
        else:
            log_event("WARNING", f"{self.label}: token HTTP {token_resp.status_code}: {token_resp.text[:150]}")
        return self.email

    async def get_verification_url(self):
        if not self.auth_token:
            return None
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        try:
            for _ in range(3):
                response = requests.get(f"{self.api_base}/messages", headers=headers, timeout=15, impersonate="chrome124")
                if response.status_code == 200:
                    messages = response.json().get("hydra:member", []) or []
                    if isinstance(messages, list):
                        for mail in messages:
                            subject = str(mail.get("subject", "") or "").lower()
                            from_data = mail.get("from", {}) or {}
                            from_address = str(from_data.get("address", "") or "").lower()
                            from_name = str(from_data.get("name", "") or "").lower()
                            is_discord = "discord" in from_address or "discord" in from_name
                            has_verify = "verify" in subject or "confirm" in subject or "verification" in subject
                            if not (is_discord or has_verify):
                                continue
                            msg_id = mail.get("id")
                            if not msg_id:
                                continue
                            detail_resp = requests.get(f"{self.api_base}/messages/{msg_id}", headers=headers, timeout=15, impersonate="chrome124")
                            if detail_resp.status_code != 200:
                                continue
                            msg_detail = detail_resp.json()
                            parts = [str(msg_detail.get("text", "") or "")]
                            for html_body in (msg_detail.get("html", []) or []):
                                parts.append(str(html_body or ""))
                            link = extract_discord_verify_link("\n".join(parts))
                            if link:
                                return link
                await asyncio.sleep(1)
        except Exception as e:
            log_event("WARNING", f"{self.label}: verify scan failed: {str(e)[:150]}")
        return None


class MailboxClient:
    def __init__(self, api_token):
        self.email = None
        self.api_base = "https://api.cybertemp.xyz"
        self.token = (api_token or "").strip()
        self.domain = None
        self.password = None

    async def get_domain(self):
        try:
            async with httpx.AsyncClient() as session:
                response = await session.get(
                    f"{self.api_base}/getDomains",
                    headers={"X-API-KEY": self.token},
                    params={"type": "discord", "limit": 20},
                    timeout=15,
                )
            if response.status_code != 200:
                log_event("WARNING", f"cybertemp: getDomains {response.status_code}: {response.text[:150]}")
                return "cybertemp.xyz"
            data = response.json() or []
            excluded = {"altmails.icu"}
            filtered = [d for d in data if not d.endswith(".store") and not d.endswith(".ng") and d not in excluded]
            if filtered:
                return random.choice(filtered)
            usable = [d for d in data if d not in excluded]
            return random.choice(usable) if usable else "cybertemp.xyz"
        except Exception as e:
            log_event("WARNING", f"cybertemp: getDomains failed: {str(e)[:150]}")
            return "cybertemp.xyz"

    async def create_inbox(self):
        if not self.token:
            log_event("ERROR", "cybertemp: no api key set (config/config.yaml -> cybertemp_key)")
            return None
        self.domain = await self.get_domain()
        user = "".join(random.choices(string.ascii_lowercase + string.digits, k=random.randint(14, 18)))
        self.email = f"{user}@{self.domain}"
        self.password = create_random_string(12)
        return self.email

    async def get_verification_url(self):
        if not self.email:
            return None
        try:
            async with httpx.AsyncClient() as session:
                response = await session.get(
                    f"{self.api_base}/getMail",
                    headers={"X-API-KEY": self.token},
                    params={"email": self.email, "limit": 5},
                    timeout=15,
                )
            if response.status_code != 200:
                log_event("WARNING", f"cybertemp: getMail {response.status_code}: {response.text[:150]}")
                return None
            emails = response.json()
            if not isinstance(emails, list):
                return None
            for mail in emails:
                subj = str(mail.get("subject", "") or "").lower()
                if "verify" not in subj and "discord" not in subj:
                    continue
                content = mail.get("html", "") or mail.get("text", "")
                link = extract_discord_verify_link(content)
                if link:
                    return link
        except Exception as e:
            log_event("WARNING", f"cybertemp: getMail failed: {str(e)[:150]}")
        return None

def _parse_broker_credential(raw, default_client_id):
    """Parse an 'email:password:refresh_token[:client_id]' record from a broker.

    Splits at most 3 times so that a password containing ':' is not corrupted,
    strips whitespace/BOM, and falls back to `default_client_id` when the
    broker omits the client id.
    """
    if raw is None:
        return None
    text = (raw if isinstance(raw, str) else str(raw)).strip().lstrip("﻿")
    parts = text.split(":", 3)
    if len(parts) < 3:
        return None
    email = parts[0].strip()
    password = parts[1].strip()
    refresh_token = parts[2].strip()
    client_id = parts[3].strip() if len(parts) >= 4 and parts[3].strip() else default_client_id
    return email, password, refresh_token, client_id


class Hotmail007Provider(MSGraphMailbox):
    label = "hotmail007"

    def __init__(self, client_key, mail_type="hotmail"):
        super().__init__()
        self.client_key = (client_key or "").strip()
        self.mail_type = mail_type
        self.base_api = "https://gapi.hotmail007.com/api"

    async def create_inbox(self):
        if not self.client_key:
            log_event("ERROR", "hotmail007: no api key set (config/config.yaml -> hotmail007_key)")
            return None
        url = f"{self.base_api}/mail/getMail?clientKey={self.client_key}&mailType={self.mail_type}&quantity=1"
        try:
            async with httpx.AsyncClient() as client:
                r = await client.get(url, timeout=30)
        except Exception as e:
            log_event("ERROR", f"hotmail007: network error: {str(e)[:150]}")
            return None
        if r.status_code != 200:
            log_event("ERROR", f"hotmail007: HTTP {r.status_code}: {r.text[:200]}")
            return None
        try:
            data = r.json()
        except Exception:
            log_event("ERROR", f"hotmail007: non-json response: {r.text[:200]}")
            return None
        if data.get("code") != 0 or not data.get("success"):
            msg = data.get("msg") or data.get("message") or data.get("error") or str(data)[:200]
            log_event("ERROR", f"hotmail007: api error (code={data.get('code')}): {msg}")
            return None
        accounts = data.get("data") or []
        if not accounts:
            log_event("ERROR", "hotmail007: api returned empty account list (check balance / stock)")
            return None
        parsed = _parse_broker_credential(accounts[0], self.ms_client_id)
        if not parsed:
            log_event("ERROR", f"hotmail007: unexpected account format: {str(accounts[0])[:80]}")
            return None
        self.email, self.password, self.refresh_token, self.uuid = parsed
        return self.email


class ZeusXProvider(MSGraphMailbox):
    label = "zeus-x"

    def __init__(self, api_key, account_code="HOTMAIL"):
        super().__init__()
        self.api_key = (api_key or "").strip()
        self.account_code = account_code
        self.base_api = "https://api.zeus-x.ru"

    async def create_inbox(self):
        if not self.api_key:
            log_event("ERROR", "zeus-x: no api key set (config/config.yaml -> zeusx_key)")
            return None
        url = f"{self.base_api}/purchase?apikey={self.api_key}&accountcode={self.account_code}&quantity=1"
        try:
            async with httpx.AsyncClient() as client:
                r = await client.get(url, timeout=30)
        except Exception as e:
            log_event("ERROR", f"zeus-x: network error: {str(e)[:150]}")
            return None
        if r.status_code != 200:
            log_event("ERROR", f"zeus-x: HTTP {r.status_code}: {r.text[:200]}")
            return None
        try:
            data = r.json()
        except Exception:
            log_event("ERROR", f"zeus-x: non-json response: {r.text[:200]}")
            return None
        if isinstance(data, list):
            accounts = data
        else:
            accounts = data.get("data") or []
        if not accounts:
            log_event("ERROR", "zeus-x: api returned empty account list (check balance / stock)")
            return None
        parsed = _parse_broker_credential(accounts[0], self.ms_client_id)
        if not parsed:
            log_event("ERROR", f"zeus-x: unexpected account format: {str(accounts[0])[:80]}")
            return None
        self.email, self.password, self.refresh_token, self.uuid = parsed
        return self.email


class DuckMailProvider(HydraMailProvider):
    label = "duckmail"
    api_base = "https://api.duckmail.sbs"


class CrowMailProvider(HydraMailProvider):
    label = "crowmail"
    api_base = "https://api.crowmail.sbs"


class AfhamMailProvider:
    label = "afham"

    def __init__(self, api_key="axm_moOcVCBUD6r1FbIeThT0wEmEofjuaDnJdMiQj7OymTU"):
        self.api_key = (api_key or "").strip()
        self.api_base = "https://api.afhamxmailz.com"
        self.email = None
        self.inbox_id = None
        self.password = None

    def _headers(self):
        return {"X-API-Key": self.api_key, "Content-Type": "application/json"}

    async def get_discord_domain(self):
        try:
            async with httpx.AsyncClient() as session:
                response = await session.get(
                    f"{self.api_base}/domains",
                    headers=self._headers(),
                    params={"type": "discord"},
                    timeout=15,
                )
        except Exception as e:
            log_event("ERROR", f"afham: domains request failed: {str(e)[:150]}")
            return None
        if response.status_code != 200:
            log_event("ERROR", f"afham: domains HTTP {response.status_code}: {response.text[:150]}")
            return None
        try:
            data = response.json()
        except Exception:
            log_event("ERROR", "afham: non-json domains response")
            return None
        if not isinstance(data, list):
            log_event("ERROR", "afham: unexpected domains response shape")
            return None
        valid = [
            d["domain"] for d in data
            if isinstance(d, dict)
            and d.get("status") == "active"
            and not d.get("domain", "").endswith(".store")
            and not d.get("domain", "").endswith(".ng")
        ]
        if not valid:
            log_event("ERROR", "afham: no active discord-safe domains available")
            return None
        return random.choice(valid)

    async def create_inbox(self):
        domain = await self.get_discord_domain()
        if not domain:
            return None
        user = "".join(random.choices(string.ascii_lowercase + string.digits, k=random.randint(10, 16)))
        self.password = create_random_string(12)
        payload = {"username": user, "domain": domain, "password": self.password}
        try:
            async with httpx.AsyncClient() as session:
                response = await session.post(
                    f"{self.api_base}/inbox/generate",
                    headers=self._headers(),
                    json=payload,
                    params={"type": "discord"},
                    timeout=15,
                )
        except Exception as e:
            log_event("ERROR", f"afham: inbox create failed: {str(e)[:150]}")
            return None
        if response.status_code not in (200, 201):
            log_event("ERROR", f"afham: inbox create HTTP {response.status_code}: {response.text[:200]}")
            return None
        data = response.json()
        self.email = data.get("address")
        self.inbox_id = data.get("id")
        return self.email

    async def get_verification_url(self):
        if not self.email:
            return None
        try:
            async with httpx.AsyncClient() as session:
                response = await session.get(
                    f"{self.api_base}/emails/{self.email}/wait",
                    headers=self._headers(),
                    params={"timeout": 30},
                    timeout=40,
                )
                emails = []
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list):
                        emails = data
                if not emails:
                    response = await session.get(
                        f"{self.api_base}/emails/{self.email}",
                        headers=self._headers(),
                        params={"per_page": 20, "unread_only": False},
                        timeout=15,
                    )
                    if response.status_code == 200:
                        data = response.json()
                        emails = data.get("emails", []) if isinstance(data, dict) else data

                for mail in emails or []:
                    subject = str(mail.get("subject", "") or "").lower()
                    from_address = str(mail.get("from_address", "") or "").lower()
                    from_name = str(mail.get("from_name", "") or "").lower()
                    is_discord = "discord" in from_address or "discord" in from_name
                    has_verify = "verify" in subject or "confirm" in subject or "verification" in subject
                    if not (is_discord or has_verify):
                        continue
                    msg_id = mail.get("id")
                    if not msg_id:
                        continue
                    detail_resp = await session.get(
                        f"{self.api_base}/emails/message/{msg_id}",
                        headers=self._headers(), timeout=15,
                    )
                    if detail_resp.status_code != 200:
                        continue
                    msg = detail_resp.json()
                    body = str(msg.get("body_text", "") or "") + "\n" + str(msg.get("body_html", "") or "")
                    link = extract_discord_verify_link(body)
                    if link:
                        return link
        except Exception as e:
            log_event("WARNING", f"afham: verify scan failed: {str(e)[:150]}")
        return None


def check_environment():
    if get_brave_path():
        return True
    return False


class BrowserContext:
    def __init__(self):
        self.driver = None

    async def start(self, url, extension_path=None, proxy=None, fingerprint=None):
        brave_path = get_brave_path()
        if not brave_path:
            log_event("ERROR", "brave browser not found")
            return None

        args = ["--lang=en-US"]
        if fingerprint:
            args.extend(build_fingerprint_args(fingerprint))
        if extension_path:
            args.append(f"--load-extension={extension_path}")
            args.append(f"--disable-extensions-except={extension_path}")

        try:
            self.driver = await uc.start(
                browser_executable_path=brave_path,
                browser_args=args,
                proxy=proxy
            )
            tab = await self.driver.get(url)
            await tab.wait_for_ready_state('complete', timeout=30000)
            try:
                await tab.evaluate(JS_UTILS)
            except:
                pass
            return tab
        except Exception as e:
            log_event("ERROR", f"browser start failed: {str(e)}")
            return None

    async def stop(self):
        if self.driver:
            try:
                await self.driver.stop()
            except:
                pass
            finally:
                self.driver = None


class AccountCreator:
    def __init__(self, api_key, mailbox_class, extension_path=None, proxy=None, custom_display_name=None, fingerprint=None):
        self.extension_path = extension_path
        self.proxy = proxy
        self.custom_display_name = custom_display_name
        self.fingerprint = fingerprint
        self.mailbox = mailbox_class(api_key)
        self.browser = BrowserContext()
        self.password = None
        self.email = None
        self.token = None
        self.session = tls_client.Session(
            client_identifier="chrome_131",
            random_tls_extension_order=True
        )
        if proxy:
            self.session.proxies = {"http": proxy, "https": proxy}

    def save_account_locally(self, status, token=""):
        output_dir = Path(get_path("output"))
        output_dir.mkdir(exist_ok=True)
        if status == "valid" and token:
            acc_path = output_dir / "accounts.txt"
            tok_path = output_dir / "tokens.txt"
            with open(acc_path, "a", encoding="utf-8") as f:
                f.write(f"{self.email}:{self.password}:{token}\n")
            with open(tok_path, "a", encoding="utf-8") as f:
                f.write(f"{token}\n")
        elif status == "locked" and token:
            locked_path = output_dir / "locked.txt"
            with open(locked_path, "a", encoding="utf-8") as f:
                f.write(f"{self.email}:{self.password}:{token}\n")

    async def report_status(self, status, token=""):
        self.save_account_locally(status, token)

    async def run(self):
        start_time = time.time()
        try:
            addr = await self.mailbox.create_inbox()
            if not addr:
                log_event("ERROR", "mail failed")
                return None
            self.email = addr
            log_event("SUCCESS", f"mail pulled: {addr}")

            page = await self.browser.start("https://discord.com/register", extension_path=self.extension_path, proxy=self.proxy, fingerprint=self.fingerprint)
            if not page:
                log_event("ERROR", "browser failed")
                return None

            if self.fingerprint:
                try:
                    import truedriver.cdp.page as cdp_page
                    fp_script = build_fingerprint_script(self.fingerprint)
                    if fp_script:
                        await page.send(cdp_page.enable())
                        await page.send(cdp_page.add_script_to_evaluate_on_new_document(source=fp_script))
                        log_event("INFO", f"fingerprint: {get_fingerprint_label(self.fingerprint)}")
                except Exception as _fp_e:
                    log_event("WARNING", f"fingerprint inject failed: {_fp_e}")

            try:
                first_names = ["James", "Mary", "Robert", "Patricia", "John", "Jennifer", "Michael", "Linda", "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica", "Thomas", "Sarah", "Charles", "Karen"]
                last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]
                display_name = self.custom_display_name or f"{random.choice(first_names)} {random.choice(last_names)}"
                user_name = make_handle()
                secret = self.mailbox.password or create_random_string(14)
                self.password = secret

                success = await self.fill_registration_form(page, addr, display_name, user_name, secret)
                if not success:
                    log_event("ERROR", "form failed")
                    return None, 0

                await self.handle_challenges(page)

                result = await self.verify_email()
                if result:
                    end_time = time.time()
                    return result, end_time - start_time
                else:
                    log_event("ERROR", "verify failed")
                    return None, 0
            except Exception as e:
                log_event("ERROR", f"error: {str(e)}")
                return None, 0
            finally:
                await self.browser.stop()
        except Exception as e:
            log_event("ERROR", f"fatal: {str(e)}")
            return None, 0

    async def human_type(self, element, text: str):
        for char in text:
            await element.send_keys(char)
            await asyncio.sleep(random.uniform(0.005, 0.02))

    async def clear_and_type(self, page, selector: str, value: str, timeout: int = 45):
        try:
            element = None
            for _ in range(5):
                try:
                    element = await page.select(selector, timeout=timeout//5)
                    if element: break
                except:
                    await asyncio.sleep(2)
            if not element:
                raise Exception(f"Element not found: {selector}")
            selector_js = json.dumps(selector)
            await page.evaluate(
                f'''() => {{
                    const el = document.querySelector({selector_js});
                    if (!el) return;
                    el.focus();
                    el.value = "";
                    el.dispatchEvent(new Event("input", {{ bubbles: true }}));
                    el.dispatchEvent(new Event("change", {{ bubbles: true }}));
                }}'''
            )
            await asyncio.sleep(random.uniform(0.01, 0.04))
            await self.human_type(element, value)
        except Exception as e:
            raise e

    async def detect_registration_issue(self, page) -> Optional[dict]: 
        try: 
            result = await page.evaluate('''() => { 
                const text = (document.body?.innerText || "").toLowerCase(); 
                const emailInvalid = text.includes("email is invalid") || 
                                    text.includes("invalid email") || 
                                    text.includes("email is not valid") || 
                                    !!document.querySelector('input[name="email"][aria-invalid="true"]'); 
                const usernameTaken = text.includes("username is already taken") || 
                                     text.includes("username already taken") || 
                                     text.includes("username is unavailable") || 
                                     text.includes("username taken") || 
                                     !!document.querySelector('input[name="username"][aria-invalid="true"]'); 
                if (emailInvalid || usernameTaken) { 
                    return { email_invalid: emailInvalid, username_taken: usernameTaken }; 
                } 
                return null; 
            }''') 
            if isinstance(result, dict): 
                return result 
        except: 
            pass
        return None 

    async def fill_registration_form(self, page, email: str, display_name: str, username: str, password: str) -> bool:
        try:
            try:
                await self.clear_and_type(page, 'input[name="email"]', email, timeout=45)
                await asyncio.sleep(random.uniform(0.05, 0.15))
            except Exception as e:
                return False
            try:
                await self.clear_and_type(page, 'input[name="global_name"]', display_name, timeout=20)
                await asyncio.sleep(random.uniform(0.05, 0.15))
            except Exception as e:
                return False
            try:
                await self.clear_and_type(page, 'input[name="username"]', username, timeout=20)
                await asyncio.sleep(random.uniform(0.05, 0.15))
            except Exception as e:
                return False
            try:
                await self.clear_and_type(page, 'input[name="password"]', password, timeout=20)
                await asyncio.sleep(random.uniform(0.05, 0.15))
            except Exception as e:
                return False
            await asyncio.sleep(0.1)
            await self.fill_date_of_birth(page)
            await asyncio.sleep(0.05)
            try:
                await page.evaluate(JS_UTILS)
                await asyncio.sleep(0.05)
                await page.evaluate('window.utils.clickAllCheckboxes()')
                await asyncio.sleep(0.05)
            except Exception as e:
                pass
            clicked = False
            await asyncio.sleep(0.1)
            try:
                buttons = await page.select_all('button')
                for button in buttons:
                    try:
                        text = (await button.get_text() or "").strip()
                        if not text: text = (button.text or "").strip()
                        if text and any(keyword in text for keyword in ['Continue', 'Create', 'Submit', 'Register']):
                            await button.click()
                            clicked = True
                            break
                    except: continue
            except: pass
            if not clicked:
                try:
                    submit = await page.select('[type="submit"]', timeout=0)
                    if submit:
                        await submit.click()
                        clicked = True
                except: pass
            if not clicked:
                try:
                    clicked_eval = await page.evaluate('''() => { 
                        const buttons = document.querySelectorAll('button'); 
                        for (const btn of buttons) { 
                            const text = btn.textContent || ''; 
                            if (text.includes('Continue') || text.includes('Create') || text.includes('Submit')) { 
                                btn.click(); 
                                return true; 
                            } 
                        } 
                        return false; 
                    }''')
                    if clicked_eval: clicked = True
                except Exception as e: pass
            if not clicked: return False
            return True
        except Exception as e: 
            return False

    async def fill_date_of_birth(self, page):
        import truedriver.cdp.input_ as cdp_input
        try:
            month_el = await page.select('[aria-label*="Month"], [aria-label*="Mês"]', timeout=5)
            await month_el.click()
            await asyncio.sleep(0.05)
            month_scrolls = random.randint(1, 11)
            for _ in range(month_scrolls):
                await page.send(cdp_input.dispatch_key_event(type_="keyDown", key="ArrowDown", windows_virtual_key_code=40, native_virtual_key_code=40))
                await page.send(cdp_input.dispatch_key_event(type_="keyUp", key="ArrowDown", windows_virtual_key_code=40, native_virtual_key_code=40))
                await asyncio.sleep(0.005)
            await asyncio.sleep(0.05)
            await page.send(cdp_input.dispatch_key_event(type_="keyDown", key="Enter", windows_virtual_key_code=13, native_virtual_key_code=13))
            await page.send(cdp_input.dispatch_key_event(type_="keyUp", key="Enter", windows_virtual_key_code=13, native_virtual_key_code=13))
            await asyncio.sleep(0.05)
            day_el = await page.select('[aria-label*="Day"], [aria-label*="Dia"]', timeout=5)
            await day_el.click()
            await asyncio.sleep(0.05)
            day_scrolls = random.randint(1, 28)
            for _ in range(day_scrolls):
                await page.send(cdp_input.dispatch_key_event(type_="keyDown", key="ArrowDown", windows_virtual_key_code=40, native_virtual_key_code=40))
                await page.send(cdp_input.dispatch_key_event(type_="keyUp", key="ArrowDown", windows_virtual_key_code=40, native_virtual_key_code=40))
                await asyncio.sleep(0.005)
            await asyncio.sleep(0.05)
            await page.send(cdp_input.dispatch_key_event(type_="keyDown", key="Enter", windows_virtual_key_code=13, native_virtual_key_code=13))
            await page.send(cdp_input.dispatch_key_event(type_="keyUp", key="Enter", windows_virtual_key_code=13, native_virtual_key_code=13))
            await asyncio.sleep(0.05)
            year_el = await page.select('[aria-label*="Year"], [aria-label*="Ano"]', timeout=5)
            await year_el.click()
            await asyncio.sleep(0.05)
            year_scrolls = random.randint(25, 35)
            for _ in range(year_scrolls):
                await page.send(cdp_input.dispatch_key_event(type_="keyDown", key="ArrowDown", windows_virtual_key_code=40, native_virtual_key_code=40))
                await page.send(cdp_input.dispatch_key_event(type_="keyUp", key="ArrowDown", windows_virtual_key_code=40, native_virtual_key_code=40))
                await asyncio.sleep(0.005)
            await asyncio.sleep(0.05)
            await page.send(cdp_input.dispatch_key_event(type_="keyDown", key="Enter", windows_virtual_key_code=13, native_virtual_key_code=13))
            await page.send(cdp_input.dispatch_key_event(type_="keyUp", key="Enter", windows_virtual_key_code=13, native_virtual_key_code=13))
        except Exception as e:
            pass

    async def handle_challenges(self, page):
        try:
            is_active = False
            for i in range(120):
                queries = ['iframe[src*="captcha"]', 'div[class*="captcha"]', '.h-captcha', '.g-recaptcha', '[data-sitekey]']
                detected = False
                for q in queries:
                    try:
                        el = await page.query_selector(q)
                        if el and await el.is_visible():
                            detected = True
                            break
                    except:
                        continue
                
                if detected and not is_active:
                    log_event("INFO", "mail pulled")
                    log_event("WARNING", "captcha appeared")
                    is_active = True
                
                if not detected:
                    if is_active:
                        log_event("INFO", "solving captcha")
                        log_event("SUCCESS", "captcha solved")
                        return True
                    elif i >= 10:
                        return True
                
                await asyncio.sleep(0.5)
        except Exception as e:
            pass
        return True

    async def get_generated_token(self, page):
        script = """
        (function() {
            try {
                const chunks = window.webpackChunkdiscord_app;
                let store;
                chunks.push([['__extra_extract__'], {}, (e) => { store = Object.values(e.c); }]);
                const mod = store.find(m => m?.exports?.default?.getToken !== undefined);
                const auth = mod.exports.default.getToken();
                if (auth) return auth;
            } catch (e) {}
            try {
                const node = document.createElement('iframe');
                document.body.appendChild(node);
                const auth = node.contentWindow.localStorage.token;
                document.body.removeChild(node);
                if (auth) return auth.replace(/\"/g, "");
            } catch (e) {}
            return null;
        })();
        """
        try:
            return await page.evaluate(script)
        except:
            return None

    async def wait_for_auth(self, page, timeout=180):
        start_time = time.time()
        attempts = 0
        while time.time() - start_time < timeout:
            try:
                attempts += 1
                token = await self.get_generated_token(page)
                if token and len(str(token)) > 30:
                    log_event("INFO", f"Token found, validating...")
                    valid, _ = self.validate_token(token)
                    if valid:
                        log_event("SUCCESS", "Token validated successfully")
                        return token
                    else:
                        log_event("WARNING", "Token invalid, retrying...")

                # Progress update every 30 seconds
                if attempts % 6 == 0:
                    elapsed = int(time.time() - start_time)
                    log_event("INFO", f"Waiting for token... ({elapsed}s / {timeout}s)")

            except Exception as e:
                log_event("WARNING", f"Token check error: {str(e)}")
            await asyncio.sleep(5)
        log_event("ERROR", f"Token wait timeout ({timeout}s)")
        return None

    def validate_token(self, token):
        if not isinstance(token, str) or not token:
            return None, None
        
        endpoint = "https://discord.com/api/v9/users/@me"
        headers = get_headers()
        headers["Authorization"] = token
        try:
            resp = self.session.get(endpoint, headers=headers)
            if resp.status_code == 200:
                info = resp.json()
                return info.get("verified", False), info.get("email", "")
            return None, None
        except:
            return None, None

    def is_flagged(self, token):
        if not isinstance(token, str) or not token:
            return None
        
        endpoint = "https://discordapp.com/api/v9/users/@me/library"
        headers = get_headers()
        headers["Authorization"] = token
        try:
            resp = self.session.get(endpoint, headers=headers)
            return resp.status_code
        except:
            return None

    async def verify_email(self):
        url = None
        log_event("INFO", "Waiting for verification email...")
        for attempt in range(300):
            try:
                url = await self.mailbox.get_verification_url()
                if url:
                    break
            except Exception as e:
                if attempt % 30 == 0 and attempt > 0:
                    log_event("WARNING", f"Still waiting for email ({attempt}s)")
            await asyncio.sleep(1)

        if not url:
            log_event("ERROR", "Mail timeout (300s)")
            return None

        try:
            if not self.browser.driver:
                log_event("ERROR", "Browser not available")
                return None

            log_event("INFO", "Opening verification link...")
            tab = await asyncio.wait_for(
                self.browser.driver.get(url, new_tab=True),
                timeout=30
            )

            log_event("INFO", "Extracting authentication token...")
            challenge_task = asyncio.create_task(self.handle_challenges(tab))
            token = await self.wait_for_auth(tab, timeout=180)

            try:
                challenge_task.cancel()
                await asyncio.sleep(0.1)
            except:
                pass

            if not token:
                log_event("ERROR", "Token extraction failed")
                return None

            log_event("INFO", "Verifying token...")

            flag_status = self.is_flagged(token)
            if flag_status == 403:
                mask = f"{token[:24]}{'*' * 12}"
                ts = datetime.now().strftime("%H:%M:%S")
                print(f"{Fore.LIGHTBLACK_EX}{ts}{Style.RESET_ALL}  {Fore.YELLOW}WAR{Style.RESET_ALL}  {Fore.WHITE}Locked: {Style.RESET_ALL}{Fore.LIGHTBLACK_EX}{mask}{Style.RESET_ALL}")
                with open("output/locked.txt", "a", encoding="utf-8") as f:
                    f.write(f"{self.email}:{self.password}:{token}\n")
                return "LOCKED"

            log_event("SUCCESS", "Verified successfully")
            log_token(f"{token[:24]}{'*' * 12}")
            self.save_data(token)
            return token
        except asyncio.TimeoutError:
            log_event("ERROR", "Verification page timeout")
            return None
        except Exception as e:
            log_event("ERROR", f"Verify error: {str(e)}")
            return None

    def save_data(self, token):
        try:
            os.makedirs("output", exist_ok=True)
            with open("output/tokens.txt", "a", encoding="utf-8") as f:
                f.write(token + "\n")
            with open("output/accounts.txt", "a", encoding="utf-8") as f:
                f.write(f"{self.email}:{self.password}:{token}\n")
            self.token = token
        except:
            pass



def _load_fp_lines() -> list:
    if not FP_FILE.exists():
        return []
    lines = []
    for line in FP_FILE.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if line and not line.startswith('#'):
            lines.append(line)
    return lines


def parse_fingerprint_line(raw_line: str) -> dict:
    import re as _re
    raw_line = raw_line.strip()
    if _re.match(r'^\d+\.[A-Za-z0-9_-]+$', raw_line):
        return {'fingerprint': raw_line}
    try:
        obj = json.loads(raw_line)
        if isinstance(obj, dict):
            return obj
    except Exception:
        pass
    return {'user_agent': raw_line}


def peek_next_fingerprint() -> tuple:
    with _fp_lock:
        lines = _load_fp_lines()
        if not lines:
            return None, None
        raw_line = lines[0]
        return parse_fingerprint_line(raw_line), raw_line


def consume_fingerprint_line(raw_line: str) -> bool:
    with _fp_lock:
        lines = _load_fp_lines()
        if raw_line not in lines:
            return False
        FP_FILE.write_text(chr(10).join(lines) + (chr(10) if lines else ""), encoding="utf-8")
        return True


def build_fingerprint_args(fp: dict) -> list:
    args = []
    user_agent = fp.get('user_agent')
    if user_agent:
        args.append(f'--user-agent={user_agent}')
    language = fp.get('language') or fp.get('accept_language')
    if language:
        args.append(f'--lang={language}')
    window_size = fp.get('window_size')
    if isinstance(window_size, str) and ',' in window_size:
        args.append(f'--window-size={window_size}')
    return args


def build_fingerprint_script(fp: dict):
    entries = []
    user_agent = fp.get('user_agent')
    if user_agent:
        entries.append(
            f"try {{ Object.defineProperty(navigator, 'userAgent', {{get: () => {json.dumps(user_agent)}, configurable: true}}); }} catch(e) {{}}"
        )
    platform_val = fp.get('platform')
    if platform_val:
        entries.append(
            f"try {{ Object.defineProperty(navigator, 'platform', {{get: () => {json.dumps(platform_val)}, configurable: true}}); }} catch(e) {{}}"
        )
    languages = fp.get('languages') or fp.get('navigator_languages')
    if languages:
        if isinstance(languages, str):
            languages = [lang.strip() for lang in languages.split(',') if lang.strip()]
        entries.append(
            f"try {{ Object.defineProperty(navigator, 'languages', {{get: () => {json.dumps(languages)}, configurable: true}}); }} catch(e) {{}}"
        )
    vendor = fp.get('vendor')
    if vendor:
        entries.append(
            f"try {{ Object.defineProperty(navigator, 'vendor', {{get: () => {json.dumps(vendor)}, configurable: true}}); }} catch(e) {{}}"
        )
    if fp.get('webdriver') is not None:
        webdriver_val = str(fp.get('webdriver')).lower()
        entries.append(
            f"try {{ Object.defineProperty(navigator, 'webdriver', {{get: () => {webdriver_val}, configurable: true}}); }} catch(e) {{}}"
        )
    fingerprint_value = fp.get('fingerprint')
    if fingerprint_value:
        entries.append("""
        try {
            var fpVal = """ + json.dumps(fingerprint_value) + """;
            try {
                if (typeof window !== 'undefined' && window.Storage && window.Storage.prototype) {
                    if (!window.Storage.prototype.setItem.__org) {
                        const orgSetItem = window.Storage.prototype.setItem;
                        window.Storage.prototype.setItem = function(key, val) {
                            if (key === 'fingerprint') {
                                val = JSON.stringify(fpVal);
                            } else if (key === 'deviceProperties') {
                                try {
                                    let parsed = JSON.parse(val);
                                    if (parsed) {
                                        parsed.fingerprint = fpVal;
                                        val = JSON.stringify(parsed);
                                    }
                                } catch(e) {}
                            }
                            return orgSetItem.call(this, key, val);
                        };
                        window.Storage.prototype.setItem.__org = orgSetItem;
                    }
                }
            } catch (e) {}
            function setFp() {
                try {
                    if (typeof window !== 'undefined' && window.localStorage && window.Storage && window.Storage.prototype) {
                        const orgSetItem = window.Storage.prototype.setItem.__org || window.Storage.prototype.setItem;
                        if (orgSetItem) {
                            orgSetItem.call(window.localStorage, 'fingerprint', JSON.stringify(fpVal));
                            var dp = window.localStorage.getItem('deviceProperties');
                            if (dp) {
                                var parsed = JSON.parse(dp);
                                if (parsed && parsed.fingerprint !== fpVal) {
                                    parsed.fingerprint = fpVal;
                                    orgSetItem.call(window.localStorage, 'deviceProperties', JSON.stringify(parsed));
                                }
                            }
                            return true;
                        }
                    }
                } catch(e) {}
                return false;
            }
            setFp();
            if (typeof window !== 'undefined') {
                window.addEventListener('DOMContentLoaded', setFp);
                window.addEventListener('load', setFp);
                var interval = setInterval(function() { setFp(); }, 50);
                setTimeout(function() { clearInterval(interval); }, 10000);
            }
        } catch(e) {}
        """)
    if not entries:
        return None
    script = chr(10).join(entries)
    return "(() => {" + chr(10) + script + chr(10) + "})()"


def get_fingerprint_label(fp: dict) -> str:
    if not fp:
        return 'none'
    return fp.get('name') or fp.get('fingerprint', '')[:20] or fp.get('user_agent', '')[:40] or 'custom'


def setup_files():
    folders = ["config", "extension", "output", "data", "data/avatars", "input"]
    for folder in folders:
        Path(get_path(folder)).mkdir(exist_ok=True, parents=True)
    
    config_path = Path(get_path("config/config.yaml"))
    if not config_path.exists():
        with open(config_path, "w") as f:
            yaml.dump({"cybertemp_key": "", "hotmail007_key": "", "zeusx_key": "", "afham_mail_api9_key": "", "vpn": False, "vpn_delay": 120}, f)
    
    nopecha_path = Path(get_path("config/nopecha.txt"))
    if not nopecha_path.exists():
        nopecha_path.write_text("")

    fp_path = Path(get_path("input/fp.txt"))
    if not fp_path.exists():
        fp_path.write_text("")



SERVICES = {
    "c": ("Cybertemp", MailboxClient, "cybertemp_key", True),
    "h": ("Hotmail", Hotmail007Provider, "hotmail007_key", True),
    "z": ("Zeus-X", ZeusXProvider, "zeusx_key", True),
    "a": ("Afham", AfhamMailProvider, "afham_mail_api9_key", False),
    "d": ("DuckMail", DuckMailProvider, "duckmail_key", False),
    "r": ("CrowMail", CrowMailProvider, "crowmail_key", True),
}


def load_and_validate_config():
    """Return (cfg, use_vpn, vpn_delay) or None on any fatal config error.

    Every failure path emits one specific log_event so the user can fix
    the config without guessing what went wrong.
    """
    config_path = get_path("config/config.yaml")
    if not os.path.exists(config_path):
        log_event("ERROR", f"config not found at: {config_path}")
        return None
    try:
        with open(config_path, "r") as f:
            cfg = yaml.safe_load(f)
    except yaml.YAMLError as e:
        log_event("ERROR", f"config.yaml is not valid yaml: {str(e)[:200]}")
        return None
    except OSError as e:
        log_event("ERROR", f"could not read config.yaml: {e}")
        return None
    if cfg is None:
        cfg = {}
    if not isinstance(cfg, dict):
        log_event("ERROR", "config.yaml must be a mapping at the top level")
        return None
    use_vpn = bool(cfg.get("vpn", False))
    raw_delay = cfg.get("vpn_delay", 120)
    try:
        vpn_delay = int(raw_delay)
    except (TypeError, ValueError):
        log_event("ERROR", f"config.yaml vpn_delay must be an integer, got {raw_delay!r}")
        return None
    if vpn_delay < 0:
        log_event("ERROR", f"config.yaml vpn_delay must be >= 0, got {vpn_delay}")
        return None
    return cfg, use_vpn, vpn_delay


async def main():
    clear_screen()
    set_console_title()
    setup_files()

    loaded = load_and_validate_config()
    if loaded is None:
        prompt_user("press enter to exit")
        return
    cfg, use_vpn, vpn_delay = loaded

    if use_vpn:
        await mullvad_ensure_connected()

    if not check_environment():
        log_event("WARNING", "brave not found")

    proxies = load_proxies(cfg)

    show_interface()

    service_prompt = "Choose service - Cybertemp (C), Hotmail (H), Zeus-X (Z), Afham (A), DuckMail (D) or CrowMail (R): "
    choice = prompt_user(service_prompt).strip().lower()
    if choice not in SERVICES:
        log_event("WARNING", f"unrecognized service '{choice}', defaulting to Cybertemp")
        choice = "c"
    service_name, mailbox_class, key_field, key_required = SERVICES[choice]
    key = (cfg.get(key_field) or "").strip()
    if not key and key_required:
        log_event("WARNING", f"no api key found for {service_name} (config.yaml -> {key_field})")

    clear_screen()
    ext_path = await setup_leninja(log_event)
    _fp_count = len(_load_fp_lines())
    if _fp_count > 0:
        log_event("INFO", f"{_fp_count} fingerprint(s) loaded from input/fp.txt")
    else:
        log_event("INFO", "no fingerprints loaded (input/fp.txt empty) - running without fingerprints")

    
    if len(sys.argv) > 1:
        try:
            target = int(sys.argv[1])
        except:
            target = 1
    else:
        try:
            target = int(prompt_user("How many accounts to gen 0 = ∞: "))
        except:
            target = 1

    custom_display_name = None
    done = 0
    start = time.time()
    success = 0
    
    try:
        while True:
            if target != 0 and done >= target: break
            done += 1
            log_event("INFO", f"creating acc # {done}")
            
            try:
                _fp_dict, _fp_raw = peek_next_fingerprint()
                engine = AccountCreator(key, mailbox_class, extension_path=ext_path, proxy=get_random_proxy(proxies), custom_display_name=custom_display_name, fingerprint=_fp_dict)
                resp = await engine.run()

                # Consume fingerprint after every use (one-time use)
                if _fp_raw:
                    consume_fingerprint_line(_fp_raw)

                if resp and len(resp) == 2:
                    token, took = resp
                    if token == "LOCKED":
                        success += 1
                    elif token:
                        log_event("SUCCESS", "valid")
                        success += 1
                    else:
                        log_event("ERROR", f"failed #{done}")
                else:
                    log_event("ERROR", f"failed #{done}")
            except asyncio.CancelledError:
                break
            except Exception as e:
                log_event("ERROR", f"error: {e}")
                continue
                
            if target == 1: break
            elif target != 0 and done >= target: break
            else:
                if use_vpn:
                    await rotate_mullvad_ip()
                else:
                    await animated_cooldown(vpn_delay)
                
    except KeyboardInterrupt:
        log_event("SUCCESS", "exiting...")
    finally:
        await shutdown_engine()
        
    elapsed = time.time() - start
    log_event("INFO", f"generated {success} valid tokens in ({elapsed:.1f}s)")
    prompt_user("press enter to exit")

if __name__ == '__main__':
    def silent_error(loop, context):
        pass
        
    try:
        if hasattr(asyncio, 'WindowsSelectorEventLoopPolicy'):
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.set_exception_handler(silent_error)
        
        try:
            loop.run_until_complete(main())
        except (asyncio.CancelledError, KeyboardInterrupt):
            pass
        finally:
            loop.close()
    except Exception as e:
        with open("crash.log", "w") as f:
            f.write(f"CRASH: {str(e)}\n\n")
            f.write(traceback.format_exc())
        print(f"CRASH: {str(e)}")
        prompt_user("press enter to exit")
    finally:
        cleanup_resources()