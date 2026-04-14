import time
import random

def retry(max_attempts, delay):
    def decorator(func):
        def wrapper(*args, **kwargs):
            attempts = 0
            while attempts < max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempts += 1
                    if attempts < max_attempts:
                        print(f"Attempt {attempts} failed: {e}. Retrying in {delay} seconds...")
                        time.sleep(delay)
                    else:
                        print(f"All {max_attempts} attempts failed: {e}")
                        raise
        return wrapper
    return decorator

@retry(max_attempts=3, delay=2)
def example_function():
    if random.random() < 0.5:
        raise Exception("Simulated error")
    else:
        return "Success"

print(example_function())