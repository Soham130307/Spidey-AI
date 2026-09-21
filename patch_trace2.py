from pathlib import Path

p = Path("main.py")
lines = p.read_text(encoding="utf-8").splitlines()

out = []

for line in lines:
    if 'response = ollama.chat(' in line:
        indent = line[:len(line) - len(line.lstrip())]
        out.append(indent + 'print("AI TRACE: ABOUT TO CALL OLLAMA")')
        out.append(indent + 'print("AI TRACE: USER =", repr(user_input))')
        out.append(indent + 'print("AI TRACE: MESSAGES =", len(messages))')

    out.append(line)

    if line.strip() == ')':
        # Don't use this generic location; handled below
        pass

text = "\n".join(out) + "\n"

# Add a marker immediately after the Ollama call's closing parenthesis.
needle = '''                    )

                reply = response['''

replacement = '''                    )

                print("AI TRACE: OLLAMA CALL RETURNED")
                print("AI TRACE: RESPONSE TYPE =", type(response).__name__)

                reply = response['''

if needle not in text:
    raise SystemExit("OLLAMA RETURN LOCATION NOT FOUND")

text = text.replace(needle, replacement, 1)

p.write_text(text, encoding="utf-8")
print("AI TRACE 2 PATCH APPLIED")
print("BACKUP: main_backup_before_ai_trace2.py")
