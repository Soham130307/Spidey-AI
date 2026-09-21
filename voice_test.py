import pyttsx3

print("Starting voice test...")

engine = pyttsx3.init()
engine.setProperty("rate", 175)
engine.setProperty("volume", 1.0)

print("Speaking now...")

engine.say("Hello Soham. This is your Jarvis voice test.")
engine.runAndWait()

print("Voice test finished.")