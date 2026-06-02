"""
Stub heavy/absent dependencies before any test module is imported.
configparser.read is monkey-patched to inject fake config so db.py and
main.py can be imported without a real bot.conf or MongoDB connection.

NOTE: telebot.TeleBot must be a MagicMock *instance* (not the class itself).
      Passing MagicMock as the class would cause the first positional arg
      (the bot TOKEN) to be interpreted as `spec=`, restricting attribute
      access and breaking `bot.message_handler`.
"""
import sys
import configparser
from unittest.mock import MagicMock

# ── 1. Stub modules absent from the test venv ────────────────────────────────
_telebot_mod = MagicMock()
_telebot_mod.TeleBot = MagicMock()          # instance, not class — avoids spec= issue
sys.modules.setdefault('telebot', _telebot_mod)
sys.modules.setdefault('telebot.types', MagicMock())
sys.modules.setdefault('telebot.apihelper', MagicMock())
sys.modules.setdefault('telegraph', MagicMock())

_pymongo = MagicMock()
_pymongo.MongoClient.return_value.noticiasbrasil = MagicMock()
_pymongo.ASCENDING = 1
sys.modules.setdefault('pymongo', _pymongo)

# ── 2. Fake configparser.read (runs at module-level in db.py and main.py) ────
_FAKE_CONFIG = {
    'NEWS': {
        'TOKEN': 'fake_token',
        'NEWS_LOG': '100',
        'NEWS_CHANNEL': '200',
        'CHANNEL_USERNAME': 'testchannel',
        'BOT_NAME': 'TestBot',
        'BOT_USERNAME': 'testbot',
        'OWNER_ID': '1',
        'OWNER_USERNAME': 'owner',
        'TELEGRAPH_TOKEN': 'tgph_token',
    },
    'DB': {'MONGO_CON': 'mongodb://localhost'},
    'LOG': {'LOG_PATH': 'test.log'},
}


def _fake_read(self, *args, **kwargs):
    self.read_dict(_FAKE_CONFIG)


configparser.ConfigParser.read = _fake_read

# ── 3. Silence loguru — avoid creating real log files during tests ────────────
from loguru import logger  # noqa: E402

logger.remove()
