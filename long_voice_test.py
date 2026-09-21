import pyttsx3

text = """A simple yet classic math question! The answer, of course, is 4.
Would you like me to help with anything else, perhaps a recipe for chicken
that incorporates that delightful number?"""

print("Starting long voice test...")

engine = pyttsx3.init()
engine.setProperty("rate", 175)
engine.setProperty("volume", 1.0)

engine.say(text)
engine.runAndWait()
engine.stop()

print("Finished.")