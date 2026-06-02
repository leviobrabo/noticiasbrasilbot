"""Tests for db.py — all MongoDB calls are mocked via patch.object."""
from unittest.mock import MagicMock, patch, call
import pytest
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import db as db_module


class TestAddNews:
    def test_first_news_gets_id_1(self):
        mock_col = MagicMock()
        mock_col.find.return_value.sort.return_value.limit.return_value = iter([])

        with patch.object(db_module, 'db') as mock_db:
            mock_db.news = mock_col
            db_module.add_news('Título', '01/06/2026 - 10:00', 'https://g1.globo.com/1')

        inserted = mock_col.insert_one.call_args[0][0]
        assert inserted['id'] == 1

    def test_subsequent_news_increments_id(self):
        mock_col = MagicMock()
        mock_col.find.return_value.sort.return_value.limit.return_value = iter([{'id': 7}])

        with patch.object(db_module, 'db') as mock_db:
            mock_db.news = mock_col
            db_module.add_news('Título 2', '01/06/2026', 'https://g1.globo.com/2')

        inserted = mock_col.insert_one.call_args[0][0]
        assert inserted['id'] == 8

    def test_link_stored_in_document(self):
        mock_col = MagicMock()
        mock_col.find.return_value.sort.return_value.limit.return_value = iter([])

        with patch.object(db_module, 'db') as mock_db:
            mock_db.news = mock_col
            db_module.add_news('T', 'd', 'https://link.com')

        inserted = mock_col.insert_one.call_args[0][0]
        assert inserted['link'] == 'https://link.com'

    def test_link_defaults_to_empty_string(self):
        mock_col = MagicMock()
        mock_col.find.return_value.sort.return_value.limit.return_value = iter([])

        with patch.object(db_module, 'db') as mock_db:
            mock_db.news = mock_col
            db_module.add_news('T', 'd')

        inserted = mock_col.insert_one.call_args[0][0]
        assert inserted['link'] == ''

    def test_all_fields_present(self):
        mock_col = MagicMock()
        mock_col.find.return_value.sort.return_value.limit.return_value = iter([])

        with patch.object(db_module, 'db') as mock_db:
            mock_db.news = mock_col
            db_module.add_news('Título', '2026', 'https://link.com')

        inserted = mock_col.insert_one.call_args[0][0]
        assert set(inserted.keys()) == {'id', 'title', 'date', 'link'}


class TestSearchFunctions:
    def test_search_title_found(self):
        mock_col = MagicMock()
        mock_col.find_one.return_value = {'title': 'Matéria'}

        with patch.object(db_module, 'db') as mock_db:
            mock_db.news = mock_col
            result = db_module.search_title('Matéria')

        mock_col.find_one.assert_called_once_with({'title': 'Matéria'})
        assert result == {'title': 'Matéria'}

    def test_search_title_not_found(self):
        mock_col = MagicMock()
        mock_col.find_one.return_value = None

        with patch.object(db_module, 'db') as mock_db:
            mock_db.news = mock_col
            result = db_module.search_title('Inexistente')

        assert result is None

    def test_check_history_queries_by_link(self):
        mock_col = MagicMock()
        mock_col.find_one.return_value = None

        with patch.object(db_module, 'db') as mock_db:
            mock_db.news = mock_col
            db_module.check_history('https://g1.globo.com/noticia')

        mock_col.find_one.assert_called_once_with({'link': 'https://g1.globo.com/noticia'})

    def test_check_history_returns_match(self):
        mock_col = MagicMock()
        mock_col.find_one.return_value = {'link': 'https://g1.globo.com/noticia', 'id': 3}

        with patch.object(db_module, 'db') as mock_db:
            mock_db.news = mock_col
            result = db_module.check_history('https://g1.globo.com/noticia')

        assert result is not None
        assert result['id'] == 3

    def test_search_user_found(self):
        mock_col = MagicMock()
        mock_col.find_one.return_value = {'user_id': 123, 'sudo': 'false'}

        with patch.object(db_module, 'db') as mock_db:
            mock_db.users = mock_col
            result = db_module.search_user(123)

        mock_col.find_one.assert_called_once_with({'user_id': 123})
        assert result['user_id'] == 123

    def test_search_user_not_found(self):
        mock_col = MagicMock()
        mock_col.find_one.return_value = None

        with patch.object(db_module, 'db') as mock_db:
            mock_db.users = mock_col
            result = db_module.search_user(999)

        assert result is None


class TestRemoveNews:
    def test_remove_all_news_calls_delete_many(self):
        mock_col = MagicMock()

        with patch.object(db_module, 'db') as mock_db:
            mock_db.news = mock_col
            db_module.remove_all_news()

        mock_col.delete_many.assert_called_once_with({})


class TestUserOperations:
    def test_set_user_sudo(self):
        mock_col = MagicMock()

        with patch.object(db_module, 'db') as mock_db:
            mock_db.users = mock_col
            db_module.set_user_sudo(42)

        mock_col.update_one.assert_called_once_with(
            {'user_id': 42}, {'$set': {'sudo': 'true'}}
        )

    def test_un_set_user_sudo(self):
        mock_col = MagicMock()

        with patch.object(db_module, 'db') as mock_db:
            mock_db.users = mock_col
            db_module.un_set_user_sudo(42)

        mock_col.update_one.assert_called_once_with(
            {'user_id': 42}, {'$set': {'sudo': 'false'}}
        )

    def test_add_user_db_stores_correct_fields(self):
        mock_col = MagicMock()
        message = MagicMock()
        message.from_user.id = 77
        message.from_user.first_name = 'João'
        message.from_user.last_name = None
        message.from_user.username = None

        with patch.object(db_module, 'db') as mock_db:
            mock_db.users = mock_col
            db_module.add_user_db(message)

        inserted = mock_col.insert_one.call_args[0][0]
        assert inserted['user_id'] == 77
        assert inserted['first_name'] == 'João'
        assert inserted['sudo'] == 'false'


class TestChatOperations:
    def test_add_chat_db(self):
        mock_col = MagicMock()

        with patch.object(db_module, 'db') as mock_db:
            mock_db.chats = mock_col
            db_module.add_chat_db(-100123, 'Grupo Teste')

        inserted = mock_col.insert_one.call_args[0][0]
        assert inserted['chat_id'] == -100123
        assert inserted['chat_name'] == 'Grupo Teste'
        assert inserted['banned'] == 'false'

    def test_remove_chat_db(self):
        mock_col = MagicMock()

        with patch.object(db_module, 'db') as mock_db:
            mock_db.chats = mock_col
            db_module.remove_chat_db(-100123)

        mock_col.delete_one.assert_called_once_with({'chat_id': -100123})
