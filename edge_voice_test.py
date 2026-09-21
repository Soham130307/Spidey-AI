import asyncio
import edge_tts

async def speak():
    text = "Hello Soham. This is JARVIS. My voice system is working correctly."

    voice = "en-US-GuyNeural"

    communicate = edge_tts.Communicate(text, voice)

    await communicate.save("jarvis_test.mp3")

asyncio.run(speak())

print("Voice file created: jarvis_test.mp3")