import time


def retry_with_backoff(operation, retries, base_delay):
    """
    Retries a failing HTTP request with increasing wait times between attempts,
    preventing your code from hammering an overwhelmed service with rapid retries.

    When a request fails, waits base_delay * 2^attempt seconds before the next try.
    If all retries are exhausted, the last exception is re-raised.
    Do NOT use third-party retry libraries (e.g. tenacity).

    Args:
        operation:  the request to send (e.g. a database query or HTTP call) — a zero-argument function
        retries:    maximum number of retries after the first request (total requests <= retries + 1)
        base_delay: base delay in seconds; doubles on each successive failed request

    Returns:
        the response from the successful request

    Raises:
        Exception: re-raises the last exception if all retries are exhausted
    """
    for attempt in range(retries + 1):
        try:
            return operation()

        except Exception:
            if attempt == retries:
                raise

            delay = base_delay * (2 ** attempt)
            time.sleep(delay)


if __name__ == '__main__':
    attempt = 0

    def flaky():
        global attempt
        attempt += 1
        if attempt < 3:
            raise ConnectionError("Service unavailable")
        return "ok"

    result = retry_with_backoff(flaky, retries=3, base_delay=1.0)
    print(result)  # ok  (called 3 times, slept 1s then 2s)
