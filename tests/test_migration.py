import sys
from unittest.mock import MagicMock, patch, call


def _import_main(env_vars, redis1, redis2):
    """Import main.py with mocked dependencies."""
    sys.modules.pop("main", None)
    with patch("dotenv.dotenv_values", return_value=env_vars), \
         patch("redis.Redis", side_effect=[redis1, redis2]):
        import main  # noqa: F401


ENV = {
    "REDIS1_HOST": "localhost",
    "REDIS1_PORT": "6379",
    "REDIS1_PASSWORD": "pass1",
    "REDIS2_HOST": "localhost",
    "REDIS2_PORT": "6380",
    "REDIS2_PASSWORD": "pass2",
}


def test_keys_are_copied():
    redis1 = MagicMock()
    redis2 = MagicMock()
    redis1.keys.return_value = ["key1", "key2"]
    redis1.get.side_effect = lambda k: f"value_{k}"

    _import_main(ENV, redis1, redis2)

    assert redis1.keys.call_count == 1
    assert redis2.set.call_args_list == [
        call("key1", "value_key1"),
        call("key2", "value_key2"),
    ]


def test_save_is_called():
    redis1 = MagicMock()
    redis2 = MagicMock()
    redis1.keys.return_value = ["key1"]
    redis1.get.return_value = "val"

    _import_main(ENV, redis1, redis2)

    redis2.save.assert_called_once()


def test_failed_key_does_not_abort():
    redis1 = MagicMock()
    redis2 = MagicMock()
    redis1.keys.return_value = ["bad_key", "good_key"]
    redis1.get.side_effect = Exception("type error")

    _import_main(ENV, redis1, redis2)

    # bad_key failed, good_key also failed on get — no sets should have happened
    redis2.set.assert_not_called()
    # but save should still be called
    redis2.save.assert_called_once()


def test_empty_source_redis():
    redis1 = MagicMock()
    redis2 = MagicMock()
    redis1.keys.return_value = []

    _import_main(ENV, redis1, redis2)

    redis2.set.assert_not_called()
    redis2.save.assert_called_once()
