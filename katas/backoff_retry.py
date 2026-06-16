import time


def retry_with_backoff(operation, retries, base_delay):
    """
    Retry an operation with exponential backoff.

    Args:
        operation: Zero-argument function to run.
        retries: Number of retries after the first attempt.
        base_delay: Initial delay in seconds.

    Returns:
        The operation result.

    Raises:
        Exception: The last exception if all attempts fail.
    """
    last_error = None

    for attempt in range(retries + 1):
        try:
            return operation()
        except Exception as error:  # pylint: disable=broad-exception-caught
            last_error = error

            if attempt < retries:
                delay = base_delay * (2 ** attempt)
                time.sleep(delay)

    raise last_error


if __name__ == "__main__":
    demo_attempt = 0

    def flaky():
        """Fail twice, then return ok."""
        global demo_attempt  # pylint: disable=global-statement
        demo_attempt += 1

        if demo_attempt < 3:
            raise ConnectionError("Service unavailable")

        return "ok"

    demo_result = retry_with_backoff(flaky, retries=3, base_delay=1.0)
    print(demo_result)