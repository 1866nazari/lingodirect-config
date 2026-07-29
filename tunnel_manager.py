import json
import re
import subprocess
import time
from pathlib import Path

import requests

# --- Configuration ---
CONFIG_PATH = Path("config.json")
LOCAL_SERVER = "http://127.0.0.1:5000"
# مسیر جدید برای بررسی سلامت بدون ایجاد خطای 404 نامفهوم
HEALTH_CHECK_URL = f"{LOCAL_SERVER}/health"
GITHUB_PAGES_URL = "https://1866nazari.github.io/lingodirect-config/config.json"
TUNNEL_COMMAND = "ssh -R 80:127.0.0.1:5000 nokey@localhost.run"
STARTUP_TIMEOUT = 30  # Increased timeout for a fresh connection
RENEWAL_INTERVAL = 100  # هر 1 دقیقه یکبار تونل را ری استارت و زنده می کند (600 ثانیه)


# --- Utility Functions ---

def run_command(command, cwd=None):
    """Executes a shell command."""
    result = subprocess.run(
        command,
        cwd=cwd,
        shell=True,
        capture_output=True,
        text=True,
    )
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def is_server_alive():
    """Checks if the local Flask server is running using the new health endpoint."""
    try:
        # ارسال User-Agent اختصاصی برای تشخیص در لاگ‌های فلسک
        headers = {"User-Agent": "Tunnel-Monitor/1.0"}
        response = requests.get(HEALTH_CHECK_URL, headers=headers, timeout=3)
        return response.status_code == 200
    except requests.RequestException:
        print("Local Flask server is not responding.")
        return False


def load_current_url():
    """Reads the current URL from the local config file."""
    if not CONFIG_PATH.exists():
        return None

    try:
        data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        return data.get("base_url")
    except (OSError, json.JSONDecodeError):
        return None


def save_url(new_url):
    """Writes the new URL to the local config file."""
    data = {"base_url": new_url}
    CONFIG_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def get_public_url():
    """Reads the current URL from the GitHub Pages config file."""
    try:
        response = requests.get(GITHUB_PAGES_URL, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get("base_url")
    except (requests.RequestException, ValueError):
        pass

    return None


def commit_and_push(new_url):
    """Updates config.json, keeps tunnel URL in a single amendable commit, and pushes safely."""
    print("Starting Git update process...")

    TUNNEL_COMMIT_PREFIX = "TunnelURL:"  # ثابت نگه دارید تا قابل تشخیص باشد
    TUNNEL_COMMIT_MESSAGE = f"{TUNNEL_COMMIT_PREFIX} update active tunnel endpoint"

    # 1. Make sure we are on main
    code, out, err = run_command("git branch --show-current")
    current_branch = (out or "").strip()
    if current_branch != "main":
        print("-> Git: Switching to main branch...")
        code, out, err = run_command("git checkout main")
        if code != 0:
            print("Git checkout failed:")
            print(out or err)
            return False

    # 2. Sync safely with remote without rewriting history
    print("-> Git: Pulling latest changes with fast-forward only...")
    code, out, err = run_command("git pull --ff-only origin main")
    if code != 0:
        print("Git pull failed:")
        print(out or err)
        return False

    # 3. Save new URL locally
    save_url(new_url)

    # Stage
    run_command("git add config.json")
    print(f"-> Git: Staging file with URL: {new_url}")

    # If nothing changed, skip
    code, out, err = run_command("git diff --cached --name-only")
    staged = (out or "").strip()
    if not staged:
        print("-> Git: No staged changes. Skipping commit/push.")
        return True

    # 4. Decide whether to amend last tunnel commit or create a new one
    code, out, err = run_command('git log -1 --pretty=%B')
    last_msg = (out or "").strip()

    if last_msg.startswith(TUNNEL_COMMIT_PREFIX):
        # Amend existing tunnel commit (single-commit rolling update)
        print("-> Git: Amending previous tunnel commit (no new commit will be created)...")
        # پیام ثابت نگه داشته می‌شود؛ محتوا (config.json) عوض می‌شود
        code, out, err = run_command(f'git commit --amend -m "{TUNNEL_COMMIT_MESSAGE}"')
        if code != 0:
            print("Git amend failed:")
            print(out or err)
            return False

        # Force-with-lease is safer than --force
        print("-> Git: Pushing amended commit (force-with-lease) to origin/main...")
        code, out, err = run_command("git push --force-with-lease origin main")
        if code != 0:
            print("Git push failed:")
            print(out or err)
            return False

        print("GitHub updated successfully (amended single tunnel commit).")
        return True

    else:
        # Create a new dedicated tunnel commit (only happens when last commit was not tunnel-related)
        print("-> Git: Creating a new dedicated tunnel commit (first time or after manual commits)...")
        code, out, err = run_command(f'git commit -m "{TUNNEL_COMMIT_MESSAGE}"')
        commit_output = "\n".join(part for part in (out, err) if part)

        if code != 0:
            # In case git says nothing to commit (race or identical)
            if "nothing to commit" in commit_output.lower():
                print("-> Git: No change detected (nothing to commit). Skipping push.")
                return True

            print("Git commit failed:")
            print(commit_output)
            return False

        print("-> Git: Commit successful.")

        # Normal push (no force needed here)
        print("-> Git: Pushing to origin/main...")
        code, out, err = run_command("git push origin main")
        if code != 0:
            print("Git push failed:")
            print(out or err)
            return False

        print("GitHub updated successfully (created tunnel commit).")
        return True


def extract_url(text):
    """Extracts the public URL from SSH output."""
    urls = re.findall(
        r"https://[a-zA-Z0-9.-]+(?:\.lhr\.life|\.localhost\.run)",
        text,
    )
    for url in urls:
        if url == "https://admin.localhost.run":
            continue
        return url
    return None


def start_tunnel():
    """Starts the SSH tunnel process."""
    # Use Popen to run in the background
    process = subprocess.Popen(
        TUNNEL_COMMAND,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1, # Line buffering
    )
    return process


def shutdown_process(process):
    """Safely terminates the SSH tunnel process."""
    if process.poll() is not None:
        return

    try:
        process.terminate()
        process.wait(timeout=3)
    except Exception:
        try:
            process.kill()
            process.wait(timeout=3)
        except Exception:
            pass


def monitor_tunnel_renewal():
    """
    Implements the proactive renewal strategy with tagged health checks.
    """
    print(f"Starting Proactive Tunnel Renewal Loop (Interval: {RENEWAL_INTERVAL}s)...")
    
    process = None
    attempt_id = 0 # شمارنده برای تشخیص در لاگ فلسک

    while True:
        attempt_id += 1
        # --- 1. Shut down existing tunnel ---
        if process:
            print(f"[{attempt_id}] Shutting down old tunnel for renewal...")
            shutdown_process(process)
            time.sleep(2)

        # --- 2. Check local server health (با ارسال شناسه تلاش) ---
        try:
            # ارسال شماره تلاش در User-Agent
            headers = {"User-Agent": f"Tunnel-Monitor/1.0 (Attempt-{attempt_id})"}
            response = requests.get(HEALTH_CHECK_URL, headers=headers, timeout=3)
            server_ok = (response.status_code == 200)
        except:
            server_ok = False

        if not server_ok:
            print(f"[{attempt_id}] Flask server offline. Retrying in {RENEWAL_INTERVAL}s...")
            time.sleep(RENEWAL_INTERVAL)
            continue
        
        # --- 3. Start new tunnel ---
        print(f"[{attempt_id}] Attempting to start new tunnel...")
        process = start_tunnel()
        public_url = None
        startup_deadline = time.time() + STARTUP_TIMEOUT

        # --- 4. Extract URL ---
        while time.time() < startup_deadline:
            if process.poll() is not None:
                break
            try:
                line = process.stdout.readline()
                if line:
                    line = line.strip()
                    print(f"[{attempt_id}] SSH: {line}")
                    public_url = extract_url(line)
                    if public_url:
                        break
            except Exception:
                pass
            time.sleep(0.5)

        # --- 5. Finalize (ارسال وضعیت بدون تغییر در منطق چرخه اصلی) ---
        if public_url:
            print(f"[{attempt_id}] SUCCESS: {public_url}")
            
            # اطلاع‌رسانی موفقیت به فلسک
            try:
                requests.post(
                    f"{LOCAL_SERVER}/tunnel_status",
                    json={"attempt_id": attempt_id, "status": "SUCCESS", "details": public_url},
                    timeout=2
                )
            except:
                pass

            # ادامه منطق پایدار قبلی شما
            current_url = load_current_url()
            github_url = get_public_url()
            if public_url != current_url or public_url != github_url:
                if not commit_and_push(public_url):
                    print(f"[{attempt_id}] Failed to update GitHub.")
            
            print(f"[{attempt_id}] Waiting {RENEWAL_INTERVAL}s for next renewal...")
            time.sleep(RENEWAL_INTERVAL)
        else:
            print(f"[{attempt_id}] FAILED to get URL. Retrying in 10s...")
            
            # اطلاع‌رسانی شکست به فلسک
            try:
                requests.post(
                    f"{LOCAL_SERVER}/tunnel_status",
                    json={"attempt_id": attempt_id, "status": "FAILED", "details": "Timeout or connection failed"},
                    timeout=2
                )
            except:
                pass

            shutdown_process(process)
            time.sleep(10)


if __name__ == "__main__":
    monitor_tunnel_renewal()
