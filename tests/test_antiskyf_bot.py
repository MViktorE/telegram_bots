import pytest
import json
import os
from unittest.mock import MagicMock
import antiskyf_bot as bot


@pytest.fixture(autouse=True)
def setup_user_data(monkeypatch):
    """Setup and cleanup for user_data.json."""
    # Create a temporary user_data.json file
    temp_file = "user_data.json"
    initial_data = {"InGroupUser": {"dates": [], "values": []}}
    with open(temp_file, "w") as f:
        json.dump(initial_data, f, indent=4)

    # Patch DATA_FILE and reload user_data in the bot module
    monkeypatch.setattr(bot, "DATA_FILE", temp_file)
    bot.user_data = bot.load_user_data()

    yield temp_file

    # Cleanup
    try:
        os.remove(temp_file)
    except FileNotFoundError:
        pass

@pytest.fixture
def mock_update():
    return MagicMock()

@pytest.fixture
def mock_context():
    return MagicMock()


def test_start_command(mock_update, mock_context):
    """Test /start command"""
    mock_update.message.reply_text = MagicMock()
    bot.start(mock_update, mock_context)
    mock_update.message.reply_text.assert_called_once_with(bot.ResponseUpon.Start())


def test_handle_message(mock_update, mock_context):
    """Test handle_message with various inputs."""
    mock_update.message.reply_text = MagicMock()

    # Valid weight
    mock_update.message.text = "70.0"
    mock_update.message.from_user.first_name = "InGroupUser"
    bot.handle_message(mock_update, mock_context)
    mock_update.message.reply_text.assert_called_once_with(bot.ResponseUpon.ValidWeight(70.0))
    mock_update.message.reply_text.reset_mock()
    mock_update.message.reset_mock()

    # Valid weight
    mock_update.message.text = "70,0"
    mock_update.message.from_user.first_name = "InGroupUser"
    bot.handle_message(mock_update, mock_context)
    mock_update.message.reply_text.assert_called_once_with(bot.ResponseUpon.ValidWeight(70.0))
    mock_update.message.reply_text.reset_mock()
    mock_update.message.reset_mock()


    # Valid. Parsed from string
    mock_update.message.text = "SmileFace::70Lol"
    mock_update.message.from_user.first_name = "InGroupUser"
    bot.handle_message(mock_update, mock_context)
    mock_update.message.reply_text.assert_called_once_with(bot.ResponseUpon.ValidWeight(70.0))
    mock_update.message.reply_text.reset_mock()
    mock_update.message.reset_mock()

    # Invalid weight. It's too high
    mock_update.message.text = "500"
    mock_update.message.from_user.first_name = "InGroupUser"
    bot.handle_message(mock_update, mock_context)
    mock_update.message.reply_text.assert_called_once_with(bot.ResponseUpon.InvalidWeight(500.0))
    mock_update.message.reply_text.reset_mock()
    mock_update.message.reset_mock()

    # No numbers
    mock_update.message.text = "Привет"
    mock_update.message.from_user.first_name = "InGroupUser"
    bot.handle_message(mock_update, mock_context)
    mock_update.message.reply_text.assert_called_once_with(bot.ResponseUpon.NonNumericInput())
    mock_update.message.reply_text.reset_mock()
    mock_update.message.reset_mock()

    # Multiple numbers
    mock_update.message.text = "Мой вес -70.0, а нет 75"
    mock_update.message.from_user.first_name = "InGroupUser"
    bot.handle_message(mock_update, mock_context)
    mock_update.message.reply_text.assert_called_once_with(bot.ResponseUpon.MultipleNumbers())
    mock_update.message.reply_text.reset_mock()
    mock_update.message.reset_mock()

    # Check that non-registered user is ignored
    mock_update.message.text = "70.0"
    mock_update.message.from_user.first_name = "NotInGroupUser"
    bot.handle_message(mock_update, mock_context)
    mock_update.message.reply_text.assert_not_called()
    mock_update.message.reply_text.reset_mock()


def test_add_command(mock_update, mock_context):
    """Test /add_me command."""
    mock_update.message.reply_text = MagicMock()

    # If user already registered by /add_me
    mock_update.message.text = "/add_me 70"
    mock_update.message.from_user.first_name = "InGroupUser"
    bot.add_me(mock_update, mock_context)
    mock_update.message.reply_text.assert_called_with(
        bot.ResponseUpon.AlreadyInTheUserList("InGroupUser")
    )
    mock_update.message.reply_text.reset_mock()

    # Valid new user
    mock_update.message.text = "/add_me 75"
    mock_update.message.from_user.first_name = "NotInGroupUser"
    bot.add_me(mock_update, mock_context)
    mock_update.message.reply_text.assert_called_with(
        bot.ResponseUpon.ValidAddMe("NotInGroupUser"))
    mock_update.message.reply_text.reset_mock()

    # Valid new user but invalid weight value
    mock_update.message.text = "/add_me asd"
    mock_update.message.from_user.first_name = "AnotherNotInGroupUser"
    bot.add_me(mock_update, mock_context)
    mock_update.message.reply_text.assert_called_with(
        bot.ResponseUpon.InvalidAddMe("AnotherNotInGroupUser")
    )
