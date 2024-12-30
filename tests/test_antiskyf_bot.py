import pytest
from unittest.mock import MagicMock
import antiskyf_bot as bot

@pytest.fixture
def mock_update():
    return MagicMock()

@pytest.fixture
def mock_context():
    return MagicMock()


# Test the /start command
def test_start_command(mock_update, mock_context):
    mock_update.message.reply_text = MagicMock()
    bot.start(mock_update, mock_context)

    mock_update.message.reply_text.assert_called_once_with(
        'Привет! Отправь мне сообщения с числами, и я построю график раз в сутки!'
    )


@pytest.mark.parametrize('input_message, expected_response', [
    ('70', bot.ResponseUpon.ValidWeight(70.0)),
    ('70.0', bot.ResponseUpon.ValidWeight(70.0)),
    ('70,0', bot.ResponseUpon.ValidWeight(70.0)),
    ('Мой вес - 70,0', bot.ResponseUpon.ValidWeight(70.0)),
    ('SmileFace70,0::lol', bot.ResponseUpon.ValidWeight(70.0)),
    ('Мой вес семьдесят киллограмм', bot.ResponseUpon.NonNumericInput()),
    ('Мой вес - 25,0', bot.ResponseUpon.InvalidWeight(25.0)),
    ('Мой вес - 500', bot.ResponseUpon.InvalidWeight(500.0)),
    ('Мой вес - 20, ой то есть 50', bot.ResponseUpon.MultipleNumbers()),
])
def test_handle_message(mock_update, mock_context, input_message, expected_response):
    mock_update.message.text = input_message
    # mock user name
    mock_update.message.from_user.first_name = 'Vasiliy'
    bot.handle_message(mock_update, mock_context)

    mock_update.message.reply_text.assert_called_once_with(expected_response)
