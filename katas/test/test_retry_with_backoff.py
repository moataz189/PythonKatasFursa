from unittest.mock import Mock

import pytest

from katas.retry_with_backoff import retry_with_backoff


def test_success_on_first_attempt(mocker):
    operation = Mock(return_value="ok")
    mock_sleep = mocker.patch("time.sleep")

    result = retry_with_backoff(operation, retries=3, base_delay=1)

    assert result == "ok"
    assert operation.call_count == 1
    mock_sleep.assert_not_called()


def test_succeeds_after_retries(mocker):
    operation = Mock(side_effect=[
        ConnectionError(),
        ConnectionError(),
        "ok",
    ])
    mock_sleep = mocker.patch("time.sleep")

    result = retry_with_backoff(operation, retries=3, base_delay=1)

    assert result == "ok"
    assert operation.call_count == 3
    mock_sleep.assert_any_call(1)
    mock_sleep.assert_any_call(2)


def test_raises_after_all_retries_exhausted(mocker):
    operation = Mock(side_effect=ConnectionError("Service unavailable"))
    mocker.patch("time.sleep")

    with pytest.raises(ConnectionError):
        retry_with_backoff(operation, retries=2, base_delay=1)

    assert operation.call_count == 3