import json
import os
import time
import threading
import subprocess
from datetime import datetime, timedelta


ALARM_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "spidey_alarms.json"
)


def _load_alarms():
    if not os.path.exists(ALARM_FILE):
        return []

    try:
        with open(ALARM_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def _save_alarms(alarms):
    with open(ALARM_FILE, "w", encoding="utf-8") as f:
        json.dump(alarms, f, indent=2)


def set_alarm(minutes):
    try:
        minutes = float(minutes)

        if minutes <= 0:
            return False, "Alarm time must be greater than zero."

        alarm_time = datetime.now() + timedelta(minutes=minutes)

        alarm = {
            "id": str(int(time.time() * 1000)),
            "trigger_time": alarm_time.isoformat(),
            "message": "Master, your alarm is ringing."
        }

        alarms = _load_alarms()
        alarms.append(alarm)
        _save_alarms(alarms)

        return True, alarm_time

    except Exception as e:
        print("Alarm error:", e)
        return False, "I couldn't set the alarm."


def get_alarms():
    return _load_alarms()


def cancel_all_alarms():
    _save_alarms([])
    return True


def _ring_alarm(message):
    print("\n🔔 ALARM:", message)

    safe_message = message.replace("'", "''")

    subprocess.Popen(
        [
            "powershell",
            "-NoProfile",
            "-Command",
            (
                "Add-Type -AssemblyName System.Speech; "
                "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
                f"$s.Speak('{safe_message}')"
            )
        ],
        creationflags=subprocess.CREATE_NO_WINDOW
    )


def _alarm_monitor():
    while True:
        try:
            alarms = _load_alarms()
            now = datetime.now()
            remaining = []

            for alarm in alarms:
                try:
                    trigger_time = datetime.fromisoformat(
                        alarm["trigger_time"]
                    )

                    if now >= trigger_time:
                        _ring_alarm(
                            alarm.get(
                                "message",
                                "Master, your alarm is ringing."
                            )
                        )
                    else:
                        remaining.append(alarm)

                except Exception as e:
                    print("Alarm check error:", e)

            _save_alarms(remaining)

        except Exception as e:
            print("Alarm monitor error:", e)

        time.sleep(1)


def start_alarm_monitor():
    thread = threading.Thread(
        target=_alarm_monitor,
        daemon=True
    )
    thread.start()