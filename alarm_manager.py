import json
import os
import time
import threading
import subprocess
from datetime import datetime, timedelta


alarm_speech_process = None
alarm_speech_lock = threading.Lock()
alarm_speech_stop = threading.Event()

# Active in-memory alarm timers
alarm_timers = {}
alarm_timers_lock = threading.Lock()


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

        # Start an in-memory timer so the alarm triggers
        # directly at the requested time.
        delay_seconds = minutes * 60.0

        timer = threading.Timer(
            delay_seconds,
            _direct_alarm_trigger,
            args=(alarm["id"], alarm["message"])
        )
        timer.daemon = True

        with alarm_timers_lock:
            alarm_timers[alarm["id"]] = timer

        timer.start()

        print(
            "ALARM TIMER STARTED:",
            alarm["id"],
            "in",
            delay_seconds,
            "seconds"
        )

        return True, alarm_time

    except Exception as e:
        print("Alarm error:", e)
        return False, "I couldn't set the alarm."


def _direct_alarm_trigger(alarm_id, message):
    print()
    print("================================")
    print("     DIRECT ALARM TRIGGERED")
    print("================================")

    with alarm_timers_lock:
        alarm_timers.pop(alarm_id, None)

    # Remove this alarm from persistent storage.
    alarms = _load_alarms()
    remaining = [
        alarm for alarm in alarms
        if alarm.get("id") != alarm_id
    ]
    _save_alarms(remaining)

    _ring_alarm(message)

def get_alarms():
    return _load_alarms()


def cancel_all_alarms():
    _save_alarms([])
    return True


def _ring_alarm(message):
    global alarm_speech_process

    print()
    print("================================")
    print("        SPIDEY ALARM")
    print("================================")
    print("ALARM:", message)

    safe_message = (message or "Master, your alarm is ringing.").replace("'", "''")

    alarm_speech_stop.clear()

    try:
        command = (
            "Add-Type -AssemblyName System.Speech; "
            "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
            f"for ($i = 0; $i -lt 10; $i++) {{ "
            f"$s.Speak('{safe_message}'); "
            "}"
        )

        process = subprocess.Popen(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                command
            ],
            creationflags=subprocess.CREATE_NO_WINDOW
        )

        with alarm_speech_lock:
            alarm_speech_process = process

        print("ALARM SPEECH STARTED")

        while process.poll() is None:
            if alarm_speech_stop.is_set():
                try:
                    process.terminate()
                except Exception:
                    pass
                break

            time.sleep(0.05)

        print("ALARM SPEECH FINISHED")

    except Exception as e:
        print("Alarm speech error:", e)

    finally:
        with alarm_speech_lock:
            alarm_speech_process = None


def stop_alarm_speech():
    global alarm_speech_process

    alarm_speech_stop.set()

    with alarm_speech_lock:
        process = alarm_speech_process

    if process is not None:
        try:
            process.terminate()
        except Exception:
            pass

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
                        alarm_message = alarm.get(
                            "message",
                            "Master, your alarm is ringing."
                        )

                        print(
                            "ALARM TRIGGERED:",
                            alarm_message
                        )

                        threading.Thread(
                            target=_ring_alarm,
                            args=(alarm_message,),
                            daemon=True
                        ).start()

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



