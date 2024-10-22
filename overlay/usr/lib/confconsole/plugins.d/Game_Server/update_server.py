"""Update game server version"""

import os
import subprocess
import re

SERVER_DIR = "/home/gameuser/gameserver"
SERVER_NAME_FILE = "/etc/gameserver/gameserver"


def get_game():
    try:
        with open(SERVER_NAME_FILE, "r") as file:
            info = {
                line.split("=")[0]: line.split("=")[1].strip().strip('"')
                for line in file
            }
            return info.get("GAME"), info.get("GAME_LONG_NAME")
    except FileNotFoundError:
        return ("error", f"File not found: {SERVER_NAME_FILE}")
    except Exception as e:
        return ("error", str(e))


def get_versions(stdout):
    def remove_ansi_escape_codes(text):
        ansi_escape = re.compile(r"\x1B[@-_][0-?]*[ -/]*[@-~]")
        return ansi_escape.sub("", text)

    clean_output = remove_ansi_escape_codes(stdout)

    current_version_match = re.search(
        r"\* Local build:\s*([\S\s]+)\s*\* Remote build:", clean_output
    )
    new_version_match = re.search(
        r"\* Remote build:\s*([\S\s]+)\s*\* Branch:", clean_output
    )

    current_version = (
        current_version_match.group(1).strip() if current_version_match else None
    )
    new_version = new_version_match.group(1).strip() if new_version_match else None

    return current_version, new_version


def run():
    if not os.path.exists("/etc/gameserver/installation.done"):
        console.msgbox("Info", "No game server is installed")
        return

    curdir = os.getcwd()
    os.chdir(SERVER_DIR)

    game_code, game_name = get_game()
    gameserver = f"./{game_code}server"

    console.infobox(f"Searching for available updates for {game_name}...")
    ret = subprocess.run(
        ["sudo", "-H", "-u", "gameuser", gameserver, "check-update"],
        capture_output=True,
        text=True,
    )
    if ret.returncode != 0:
        yesno = console.yesno(
            "An error occurred while checking for an update. Attempt to update regardless?\n"
            + ret.stderr
        )
        if yesno == "cancel":
            console.msgbox("Cancelling", "Update was cancelled by the user.")
            os.chdir(curdir)
            return

    current_version, new_version = get_versions(ret.stdout)
    if "No update available" in ret.stdout:
        console.msgbox(
            "No Update Available",
            f"No update is available, cancelling the update.\nCurrent version: {current_version}",
        )
        os.chdir(curdir)
        return

    yesno = console.yesno(
        f"Update found. Proceed with update?\nCurrent version: {current_version}\nNew version: {new_version}"
    )
    if yesno == "cancel":
        console.msgbox("Cancelling", "Update was cancelled by the user.")
        os.chdir(curdir)
        return

    console.infobox(
        f"Attemting to update {game_name}. Be patient, this may take a while..."
    )
    ret = subprocess.run(
        ["sudo", "-H", "-u", "gameuser", gameserver, "update"],
        capture_output=True,
        text=True,
    )
    if ret.returncode != 0:
        console.msgbox("Error", "An error occurred during the update:\n" + ret.stderr)
    else:
        console.msgbox(
            "Update Success",
            f"{game_name} was successfully updated to version {current_version}\nThe server has been restarted.",
        )

    os.chdir(curdir)
