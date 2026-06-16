import unittest
from unittest.mock import Mock, patch

from backoff_retry import retry_with_backoff


class TestRetryWithBackoff(unittest.TestCase):

    @patch("time.sleep")
    def test_success_on_first_attempt(self, mock_sleep):
        operation = Mock(return_value="ok")

        result = retry_with_backoff(operation, retries=3, base_delay=1)

        self.assertEqual(result, "ok")
        self.assertEqual(operation.call_count, 1)
        mock_sleep.assert_not_called()

    @patch("time.sleep")
    def test_succeeds_after_retries(self, mock_sleep):
        operation = Mock(side_effect=[
            ConnectionError(),
            ConnectionError(),
            "ok",
        ])

        result = retry_with_backoff(operation, retries=3, base_delay=1)

        self.assertEqual(result, "ok")
        self.assertEqual(operation.call_count, 3)
        mock_sleep.assert_any_call(1)
        mock_sleep.assert_any_call(2)

    @patch("time.sleep")
    def test_raises_after_all_retries_exhausted(self, mock_sleep):
        operation = Mock(side_effect=ConnectionError("Service unavailable"))

        with self.assertRaises(ConnectionError):
            retry_with_backoff(operation, retries=2, base_delay=1)

        self.assertEqual(operation.call_count, 3)