"""
Backend/ComputerControl.py
Full Computer Control Module — Cross-Platform (Windows/macOS/Linux)
Provides: CommandExecutor, FileManager, AppController, CommandLogger
"""

import subprocess
import platform
import os
import sys
import json
import uuid
import shutil
import datetime
import glob


# ─────────────────────────────────────────────────────────────
#  Utility: Detect OS once
# ─────────────────────────────────────────────────────────────
CURRENT_OS = platform.system()  # "Windows", "Darwin", "Linux"


def get_desktop_path():
    """Return the Desktop path for the current OS."""
    if CURRENT_OS == "Windows":
        return os.path.join(os.environ.get("USERPROFILE", os.path.expanduser("~")), "Desktop")
    else:
        return os.path.join(os.path.expanduser("~"), "Desktop")


# ─────────────────────────────────────────────────────────────
#  CommandLogger — logs every command to Desktop/AI_Command_Logs/
# ─────────────────────────────────────────────────────────────
class CommandLogger:
    """Logs every command the user gives to a JSON file on the Desktop."""

    def __init__(self):
        self.session_id = str(uuid.uuid4())[:8]
        self.log_dir = os.path.join(get_desktop_path(), "AI_Command_Logs")
        os.makedirs(self.log_dir, exist_ok=True)
        self.log_file = os.path.join(
            self.log_dir,
            f"session_{self.session_id}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        self.entries = []
        # Write initial empty array
        self._flush()

    def log(self, command: str, status: str, output: str):
        """Add a log entry and save to disk."""
        entry = {
            "session_id": self.session_id,
            "timestamp": datetime.datetime.now().isoformat() + "Z",
            "command": command,
            "status": status,  # "success" or "failed"
            "output": output
        }
        self.entries.append(entry)
        self._flush()
        return entry

    def _flush(self):
        """Write current entries to the JSON log file."""
        try:
            with open(self.log_file, "w", encoding="utf-8") as f:
                json.dump(self.entries, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[CommandLogger] Error writing log: {e}")


# Create a global logger instance for this session
_logger = CommandLogger()


# ─────────────────────────────────────────────────────────────
#  DANGEROUS COMMAND DETECTION
# ─────────────────────────────────────────────────────────────
DANGEROUS_PATTERNS = [
    "rm -rf /", "rm -rf ~", "rm -rf *",
    "del /s /q C:\\", "format C:",
    "mkfs", ":(){:|:&};:",
    "dd if=", "shutdown", "restart",
    "reg delete", "Remove-Item -Recurse -Force C:\\",
    "> /dev/sda", "chmod -R 777 /",
]


def is_dangerous_command(cmd: str) -> bool:
    """Check if a command matches known dangerous patterns."""
    cmd_lower = cmd.lower().strip()
    for pattern in DANGEROUS_PATTERNS:
        if pattern.lower() in cmd_lower:
            return True
    return False


# ─────────────────────────────────────────────────────────────
#  CommandExecutor — run any terminal command
# ─────────────────────────────────────────────────────────────
class CommandExecutor:
    """Execute arbitrary terminal/command-line commands cross-platform."""

    @staticmethod
    def execute(command: str, cwd: str = None, timeout: int = 60) -> dict:
        """
        Execute a shell command and return result dict.
        Returns: {"success": bool, "output": str, "error": str}
        """
        # Safety check
        if is_dangerous_command(command):
            result = {
                "success": False,
                "output": "",
                "error": f"BLOCKED: This command was detected as potentially dangerous: {command}"
            }
            _logger.log(command, "blocked", result["error"])
            return result

        try:
            if CURRENT_OS == "Windows":
                # Use cmd.exe on Windows
                proc = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    cwd=cwd
                )
            else:
                # Use bash on macOS/Linux
                proc = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    cwd=cwd,
                    executable="/bin/bash"
                )

            success = proc.returncode == 0
            output = proc.stdout.strip() if proc.stdout else ""
            error = proc.stderr.strip() if proc.stderr else ""

            status = "success" if success else "failed"
            _logger.log(command, status, output or error)

            return {
                "success": success,
                "output": output,
                "error": error
            }
        except subprocess.TimeoutExpired:
            _logger.log(command, "failed", f"Command timed out after {timeout}s")
            return {
                "success": False,
                "output": "",
                "error": f"Command timed out after {timeout} seconds"
            }
        except Exception as e:
            _logger.log(command, "failed", str(e))
            return {
                "success": False,
                "output": "",
                "error": str(e)
            }


# ─────────────────────────────────────────────────────────────
#  FileManager — CRUD for files and folders
# ─────────────────────────────────────────────────────────────
class FileManager:
    """Cross-platform file and folder operations."""

    @staticmethod
    def resolve_path(path: str) -> str:
        """Resolve ~ and relative paths, and handle 'Desktop' references."""
        path = os.path.expanduser(path)
        # If path starts with "Desktop", prepend the actual Desktop path
        if path.lower().startswith("desktop"):
            desktop = get_desktop_path()
            remainder = path[len("desktop"):].lstrip(os.sep).lstrip("/").lstrip("\\")
            path = os.path.join(desktop, remainder)
        return os.path.abspath(path)

    @staticmethod
    def create_folder(path: str) -> dict:
        """Create a folder (and parent directories)."""
        path = FileManager.resolve_path(path)
        try:
            os.makedirs(path, exist_ok=True)
            _logger.log(f"create_folder: {path}", "success", f"Folder created: {path}")
            return {"success": True, "message": f"Folder created: {path}"}
        except Exception as e:
            _logger.log(f"create_folder: {path}", "failed", str(e))
            return {"success": False, "message": str(e)}

    @staticmethod
    def create_file(path: str, content: str = "") -> dict:
        """Create a file with optional content."""
        path = FileManager.resolve_path(path)
        try:
            # Create parent directories if needed
            parent = os.path.dirname(path)
            if parent:
                os.makedirs(parent, exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            _logger.log(f"create_file: {path}", "success", f"File created: {path}")
            return {"success": True, "message": f"File created: {path}"}
        except Exception as e:
            _logger.log(f"create_file: {path}", "failed", str(e))
            return {"success": False, "message": str(e)}

    @staticmethod
    def read_file(path: str) -> dict:
        """Read a file and return its content."""
        path = FileManager.resolve_path(path)
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            _logger.log(f"read_file: {path}", "success", f"Read {len(content)} chars")
            return {"success": True, "content": content}
        except Exception as e:
            _logger.log(f"read_file: {path}", "failed", str(e))
            return {"success": False, "content": "", "message": str(e)}

    @staticmethod
    def write_file(path: str, content: str) -> dict:
        """Write content to an existing/new file."""
        path = FileManager.resolve_path(path)
        try:
            parent = os.path.dirname(path)
            if parent:
                os.makedirs(parent, exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            _logger.log(f"write_file: {path}", "success", f"Wrote {len(content)} chars")
            return {"success": True, "message": f"File written: {path}"}
        except Exception as e:
            _logger.log(f"write_file: {path}", "failed", str(e))
            return {"success": False, "message": str(e)}

    @staticmethod
    def append_file(path: str, content: str) -> dict:
        """Append content to a file."""
        path = FileManager.resolve_path(path)
        try:
            with open(path, "a", encoding="utf-8") as f:
                f.write(content)
            _logger.log(f"append_file: {path}", "success", f"Appended {len(content)} chars")
            return {"success": True, "message": f"Content appended to: {path}"}
        except Exception as e:
            _logger.log(f"append_file: {path}", "failed", str(e))
            return {"success": False, "message": str(e)}

    @staticmethod
    def delete_file(path: str) -> dict:
        """Delete a file."""
        path = FileManager.resolve_path(path)
        try:
            if os.path.isfile(path):
                os.remove(path)
                _logger.log(f"delete_file: {path}", "success", f"File deleted: {path}")
                return {"success": True, "message": f"File deleted: {path}"}
            else:
                return {"success": False, "message": f"File not found: {path}"}
        except Exception as e:
            _logger.log(f"delete_file: {path}", "failed", str(e))
            return {"success": False, "message": str(e)}

    @staticmethod
    def delete_folder(path: str) -> dict:
        """Delete a folder and its contents."""
        path = FileManager.resolve_path(path)
        try:
            if os.path.isdir(path):
                shutil.rmtree(path)
                _logger.log(f"delete_folder: {path}", "success", f"Folder deleted: {path}")
                return {"success": True, "message": f"Folder deleted: {path}"}
            else:
                return {"success": False, "message": f"Folder not found: {path}"}
        except Exception as e:
            _logger.log(f"delete_folder: {path}", "failed", str(e))
            return {"success": False, "message": str(e)}

    @staticmethod
    def move(src: str, dst: str) -> dict:
        """Move a file or folder from src to dst."""
        src = FileManager.resolve_path(src)
        dst = FileManager.resolve_path(dst)
        try:
            shutil.move(src, dst)
            _logger.log(f"move: {src} -> {dst}", "success", f"Moved: {src} -> {dst}")
            return {"success": True, "message": f"Moved: {src} -> {dst}"}
        except Exception as e:
            _logger.log(f"move: {src} -> {dst}", "failed", str(e))
            return {"success": False, "message": str(e)}

    @staticmethod
    def copy(src: str, dst: str) -> dict:
        """Copy a file or folder from src to dst."""
        src = FileManager.resolve_path(src)
        dst = FileManager.resolve_path(dst)
        try:
            if os.path.isdir(src):
                shutil.copytree(src, dst)
            else:
                parent = os.path.dirname(dst)
                if parent:
                    os.makedirs(parent, exist_ok=True)
                shutil.copy2(src, dst)
            _logger.log(f"copy: {src} -> {dst}", "success", f"Copied: {src} -> {dst}")
            return {"success": True, "message": f"Copied: {src} -> {dst}"}
        except Exception as e:
            _logger.log(f"copy: {src} -> {dst}", "failed", str(e))
            return {"success": False, "message": str(e)}

    @staticmethod
    def list_directory(path: str) -> dict:
        """List contents of a directory."""
        path = FileManager.resolve_path(path)
        try:
            items = os.listdir(path)
            detailed = []
            for item in items:
                full = os.path.join(path, item)
                detailed.append({
                    "name": item,
                    "is_dir": os.path.isdir(full),
                    "size": os.path.getsize(full) if os.path.isfile(full) else None
                })
            _logger.log(f"list_directory: {path}", "success", f"Found {len(items)} items")
            return {"success": True, "items": detailed}
        except Exception as e:
            _logger.log(f"list_directory: {path}", "failed", str(e))
            return {"success": False, "items": [], "message": str(e)}


# ─────────────────────────────────────────────────────────────
#  AppController — open/close applications cross-platform
# ─────────────────────────────────────────────────────────────

# Common app name → executable mapping for Windows
WINDOWS_APP_MAP = {
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "calc": "calc.exe",
    "paint": "mspaint.exe",
    "cmd": "cmd.exe",
    "terminal": "wt.exe",
    "powershell": "powershell.exe",
    "explorer": "explorer.exe",
    "file explorer": "explorer.exe",
    "task manager": "taskmgr.exe",
    "control panel": "control.exe",
    "settings": "ms-settings:",
    "edge": "msedge.exe",
    "chrome": "chrome.exe",
    "google chrome": "chrome.exe",
    "firefox": "firefox.exe",
    "brave": "brave.exe",
    "vscode": "code.exe",
    "vs code": "code.exe",
    "visual studio code": "code.exe",
    "word": "winword.exe",
    "excel": "excel.exe",
    "powerpoint": "powerpnt.exe",
    "outlook": "outlook.exe",
    "discord": "discord.exe",
    "spotify": "spotify.exe",
    "telegram": "telegram.exe",
    "whatsapp": "whatsapp.exe",
    "slack": "slack.exe",
    "zoom": "zoom.exe",
    "obs": "obs64.exe",
    "vlc": "vlc.exe",
    "media player": "wmplayer.exe",
    "snipping tool": "snippingtool.exe",
    "wordpad": "wordpad.exe",
}

# Windows process names for killing (app name → process name)
WINDOWS_PROCESS_MAP = {
    "notepad": "notepad",
    "calculator": "Calculator",
    "calc": "Calculator",
    "paint": "mspaint",
    "chrome": "chrome",
    "google chrome": "chrome",
    "firefox": "firefox",
    "edge": "msedge",
    "brave": "brave",
    "vscode": "Code",
    "vs code": "Code",
    "word": "WINWORD",
    "excel": "EXCEL",
    "powerpoint": "POWERPNT",
    "outlook": "OUTLOOK",
    "discord": "Discord",
    "spotify": "Spotify",
    "telegram": "Telegram",
    "whatsapp": "WhatsApp",
    "slack": "slack",
    "zoom": "Zoom",
    "vlc": "vlc",
    "explorer": "explorer",
}


class AppController:
    """Open and close applications by name, cross-platform."""

    @staticmethod
    def open_app(app_name: str) -> dict:
        """Open an application by name."""
        app_lower = app_name.lower().strip()

        try:
            # Check if it's a website URL
            if app_lower.startswith(("http://", "https://", "www.")):
                import webbrowser
                webbrowser.open(app_lower if app_lower.startswith("http") else f"https://{app_lower}")
                _logger.log(f"open_app: {app_name}", "success", f"Opened URL: {app_lower}")
                return {"success": True, "message": f"Opened URL: {app_lower}"}

            # Check if it's a known website name
            websites = {
                "facebook": "https://www.facebook.com",
                "instagram": "https://www.instagram.com",
                "twitter": "https://www.twitter.com",
                "x": "https://www.x.com",
                "youtube": "https://www.youtube.com",
                "github": "https://www.github.com",
                "google": "https://www.google.com",
                "gmail": "https://mail.google.com",
                "linkedin": "https://www.linkedin.com",
                "reddit": "https://www.reddit.com",
                "amazon": "https://www.amazon.com",
                "netflix": "https://www.netflix.com",
                "stackoverflow": "https://stackoverflow.com",
                "chatgpt": "https://chat.openai.com",
                "whatsapp web": "https://web.whatsapp.com",
            }

            if app_lower in websites:
                import webbrowser
                webbrowser.open(websites[app_lower])
                _logger.log(f"open_app: {app_name}", "success", f"Opened website: {websites[app_lower]}")
                return {"success": True, "message": f"Opened {app_name}"}

            if CURRENT_OS == "Windows":
                # Try the app map first
                if app_lower in WINDOWS_APP_MAP:
                    executable = WINDOWS_APP_MAP[app_lower]
                    if executable.startswith("ms-"):
                        # It's a URI scheme (like ms-settings:)
                        os.startfile(executable)
                    else:
                        subprocess.Popen(executable, shell=True)
                else:
                    # Try os.startfile (handles Start Menu items and registered apps)
                    try:
                        os.startfile(app_name)
                    except OSError:
                        # Try via 'start' command
                        subprocess.Popen(f'start "" "{app_name}"', shell=True)

            elif CURRENT_OS == "Darwin":
                subprocess.Popen(["open", "-a", app_name])

            else:  # Linux
                # Try common approaches
                subprocess.Popen([app_lower], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            _logger.log(f"open_app: {app_name}", "success", f"Opened app: {app_name}")
            return {"success": True, "message": f"Opened {app_name}"}

        except Exception as e:
            _logger.log(f"open_app: {app_name}", "failed", str(e))
            return {"success": False, "message": f"Failed to open {app_name}: {e}"}

    @staticmethod
    def close_app(app_name: str) -> dict:
        """Close an application by name."""
        app_lower = app_name.lower().strip()

        try:
            if CURRENT_OS == "Windows":
                # Get the process name
                process = WINDOWS_PROCESS_MAP.get(app_lower, app_lower)
                result = subprocess.run(
                    f'taskkill /F /IM "{process}.exe"',
                    shell=True,
                    capture_output=True,
                    text=True
                )
                if result.returncode != 0:
                    # Try with the original name
                    result = subprocess.run(
                        f'taskkill /F /IM "{app_name}.exe"',
                        shell=True,
                        capture_output=True,
                        text=True
                    )

            elif CURRENT_OS == "Darwin":
                subprocess.run(["pkill", "-f", app_name], capture_output=True)

            else:  # Linux
                subprocess.run(["pkill", "-f", app_lower], capture_output=True)

            _logger.log(f"close_app: {app_name}", "success", f"Closed app: {app_name}")
            return {"success": True, "message": f"Closed {app_name}"}

        except Exception as e:
            _logger.log(f"close_app: {app_name}", "failed", str(e))
            return {"success": False, "message": f"Failed to close {app_name}: {e}"}


# ─────────────────────────────────────────────────────────────
#  SystemControl — volume, brightness, etc.
# ─────────────────────────────────────────────────────────────
class SystemControl:
    """Cross-platform system controls (volume, etc.)."""

    @staticmethod
    def mute():
        if CURRENT_OS == "Windows":
            # Use PowerShell to mute via SendKeys
            subprocess.run(
                'powershell -Command "(New-Object -ComObject WScript.Shell).SendKeys([char]173)"',
                shell=True, capture_output=True
            )
        elif CURRENT_OS == "Darwin":
            subprocess.run(["osascript", "-e", "set Volume 0"])
        else:
            subprocess.run(["amixer", "set", "Master", "mute"], capture_output=True)
        _logger.log("system: mute", "success", "System muted")

    @staticmethod
    def unmute():
        if CURRENT_OS == "Windows":
            subprocess.run(
                'powershell -Command "(New-Object -ComObject WScript.Shell).SendKeys([char]173)"',
                shell=True, capture_output=True
            )
        elif CURRENT_OS == "Darwin":
            subprocess.run(["osascript", "-e", "set Volume 5"])
        else:
            subprocess.run(["amixer", "set", "Master", "unmute"], capture_output=True)
        _logger.log("system: unmute", "success", "System unmuted")

    @staticmethod
    def volume_up():
        if CURRENT_OS == "Windows":
            subprocess.run(
                'powershell -Command "(New-Object -ComObject WScript.Shell).SendKeys([char]175)"',
                shell=True, capture_output=True
            )
        elif CURRENT_OS == "Darwin":
            subprocess.run(["osascript", "-e", "set Volume output volume (output volume of (get volume settings) + 10)"])
        else:
            subprocess.run(["amixer", "set", "Master", "10%+"], capture_output=True)
        _logger.log("system: volume_up", "success", "Volume increased")

    @staticmethod
    def volume_down():
        if CURRENT_OS == "Windows":
            subprocess.run(
                'powershell -Command "(New-Object -ComObject WScript.Shell).SendKeys([char]174)"',
                shell=True, capture_output=True
            )
        elif CURRENT_OS == "Darwin":
            subprocess.run(["osascript", "-e", "set Volume output volume (output volume of (get volume settings) - 10)"])
        else:
            subprocess.run(["amixer", "set", "Master", "10%-"], capture_output=True)
        _logger.log("system: volume_down", "success", "Volume decreased")


# ─────────────────────────────────────────────────────────────
#  High-level function for the AI to call
# ─────────────────────────────────────────────────────────────
executor = CommandExecutor()
file_manager = FileManager()
app_controller = AppController()
system_control = SystemControl()


def ExecuteComputerCommand(command_text: str) -> str:
    """
    Parse and execute a computer control command from natural language.
    Returns a human-readable result string.
    """
    cmd_lower = command_text.lower().strip()

    # ── File/Folder creation ──
    if "create folder" in cmd_lower or "make folder" in cmd_lower or "create directory" in cmd_lower:
        # Extract folder name/path
        for prefix in ["create folder ", "make folder ", "create directory ", "create a folder ", "make a folder "]:
            if cmd_lower.startswith(prefix):
                path = command_text[len(prefix):].strip().strip('"').strip("'")
                result = file_manager.create_folder(path)
                return result["message"]
        # Fallback: use everything after the keyword
        parts = cmd_lower.split("folder")
        if len(parts) > 1:
            path = parts[-1].strip().strip('"').strip("'")
            if path:
                result = file_manager.create_folder(path)
                return result["message"]

    if "create file" in cmd_lower or "make file" in cmd_lower:
        for prefix in ["create file ", "make file ", "create a file ", "make a file "]:
            if cmd_lower.startswith(prefix):
                rest = command_text[len(prefix):].strip().strip('"').strip("'")
                # Check if there's content specified
                if " content " in rest:
                    parts = rest.split(" content ", 1)
                    path = parts[0].strip()
                    content = parts[1].strip()
                else:
                    path = rest
                    content = ""
                result = file_manager.create_file(path, content)
                return result["message"]

    if "delete file" in cmd_lower or "remove file" in cmd_lower:
        for prefix in ["delete file ", "remove file ", "delete the file ", "remove the file "]:
            if cmd_lower.startswith(prefix):
                path = command_text[len(prefix):].strip().strip('"').strip("'")
                result = file_manager.delete_file(path)
                return result["message"]

    if "delete folder" in cmd_lower or "remove folder" in cmd_lower:
        for prefix in ["delete folder ", "remove folder ", "delete the folder ", "remove the folder "]:
            if cmd_lower.startswith(prefix):
                path = command_text[len(prefix):].strip().strip('"').strip("'")
                result = file_manager.delete_folder(path)
                return result["message"]

    if "move file" in cmd_lower or "move folder" in cmd_lower:
        # Format: "move file X to Y"
        if " to " in cmd_lower:
            parts = command_text.split(" to ", 1)
            src_part = parts[0]
            for prefix in ["move file ", "move folder ", "move "]:
                if src_part.lower().startswith(prefix):
                    src_part = src_part[len(prefix):]
            src = src_part.strip().strip('"').strip("'")
            dst = parts[1].strip().strip('"').strip("'")
            result = file_manager.move(src, dst)
            return result["message"]

    if "read file" in cmd_lower or "show file" in cmd_lower or "open file" in cmd_lower:
        for prefix in ["read file ", "show file ", "open file ", "read the file ", "show the file "]:
            if cmd_lower.startswith(prefix):
                path = command_text[len(prefix):].strip().strip('"').strip("'")
                result = file_manager.read_file(path)
                if result["success"]:
                    return f"Contents of {path}:\n{result['content']}"
                return result.get("message", "Failed to read file")

    if "write to file" in cmd_lower or "write file" in cmd_lower:
        # Format: "write to file X content Y" or "write 'content' to file X"
        if " content " in command_text:
            parts = command_text.split(" content ", 1)
            for prefix in ["write to file ", "write file "]:
                if parts[0].lower().startswith(prefix):
                    parts[0] = parts[0][len(prefix):]
            path = parts[0].strip().strip('"').strip("'")
            content = parts[1].strip()
            result = file_manager.write_file(path, content)
            return result["message"]

    if "list files" in cmd_lower or "list directory" in cmd_lower or "list folder" in cmd_lower:
        for prefix in ["list files in ", "list directory ", "list folder ", "list files "]:
            if cmd_lower.startswith(prefix):
                path = command_text[len(prefix):].strip().strip('"').strip("'")
                result = file_manager.list_directory(path)
                if result["success"]:
                    items_str = "\n".join(
                        f"  {'[DIR]' if i['is_dir'] else '[FILE]'} {i['name']}"
                        for i in result["items"]
                    )
                    return f"Contents of {path}:\n{items_str}"
                return result.get("message", "Failed to list directory")

    # ── Run terminal command (fallback) ──
    if cmd_lower.startswith("run ") or cmd_lower.startswith("execute ") or cmd_lower.startswith("terminal "):
        for prefix in ["run ", "execute ", "terminal "]:
            if cmd_lower.startswith(prefix):
                actual_cmd = command_text[len(prefix):].strip()
                result = executor.execute(actual_cmd)
                if result["success"]:
                    return f"Command executed successfully.\nOutput: {result['output']}" if result['output'] else "Command executed successfully."
                else:
                    return f"Command failed.\nError: {result['error']}"

    # ── If nothing matched, try running it as a raw command ──
    result = executor.execute(command_text)
    if result["success"]:
        return f"Executed: {command_text}\nOutput: {result['output']}" if result['output'] else f"Executed: {command_text}"
    else:
        return f"Failed to execute: {command_text}\nError: {result['error']}"


# ─────────────────────────────────────────────────────────────
#  Interactive test
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"Computer Control Module — Running on {CURRENT_OS}")
    print(f"Logs → {_logger.log_dir}")
    print("Type commands (e.g., 'create folder Desktop/test_project', 'run echo hello', 'open notepad')")
    print("Type 'exit' to quit.\n")
    while True:
        cmd = input(">>> ").strip()
        if cmd.lower() in ("exit", "quit", "bye"):
            break
        print(ExecuteComputerCommand(cmd))
        print()
