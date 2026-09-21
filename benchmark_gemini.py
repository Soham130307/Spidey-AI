import time
import main

times = []
prompt = "Answer briefly: What is the capital of Japan?"

print("GEMINI 5-RUN BENCHMARK")
print("-----------------------")

for i in range(1, 6):
    start = time.perf_counter()

    r = main.gemini_client.models.generate_content(
        model=main.GEMINI_MODEL,
        contents=prompt,
        config={
            "temperature": 0.3,
            "max_output_tokens": 1000
        }
    )

    end = time.perf_counter()
    elapsed = end - start
    times.append(elapsed)

    print(f"Run {i}: {elapsed:.3f}s | {r.text!r}")

print("-----------------------")
print(f"FASTEST: {min(times):.3f}s")
print(f"SLOWEST: {max(times):.3f}s")
print(f"AVERAGE: {sum(times) / len(times):.3f}s")
