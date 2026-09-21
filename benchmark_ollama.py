import time
import ollama

times = []
prompt = "Answer briefly: What is the capital of Japan?"

print("OLLAMA 5-RUN BENCHMARK")
print("-----------------------")

for i in range(1, 6):
    start = time.perf_counter()

    r = ollama.chat(
        model="llama3.2:3b",
        messages=[
            {"role": "user", "content": prompt}
        ],
        options={
            "temperature": 0.3,
            "num_predict": 100
        }
    )

    end = time.perf_counter()
    elapsed = end - start
    times.append(elapsed)

    print(f"Run {i}: {elapsed:.3f}s | {r['message']['content']!r}")

print("-----------------------")
print(f"FASTEST: {min(times):.3f}s")
print(f"SLOWEST: {max(times):.3f}s")
print(f"AVERAGE: {sum(times) / len(times):.3f}s")
