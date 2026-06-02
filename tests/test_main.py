"""Tests for main.py — external services (Telegram, Telegraph, MongoDB) are mocked."""
from unittest.mock import MagicMock, patch, call
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import main as main_module
import db as db_module


# ---------------------------------------------------------------------------
# sudo()
# ---------------------------------------------------------------------------

class TestSudo:
    def test_returns_true_for_sudo_user(self):
        with patch.object(db_module, 'db') as mock_db:
            mock_db.users.find_one.return_value = {'user_id': 1, 'sudo': 'true'}
            assert main_module.sudo(1) is True

    def test_returns_false_when_flag_is_false(self):
        with patch.object(db_module, 'db') as mock_db:
            mock_db.users.find_one.return_value = {'user_id': 2, 'sudo': 'false'}
            assert main_module.sudo(2) is False

    def test_returns_false_when_user_not_found(self):
        with patch.object(db_module, 'db') as mock_db:
            mock_db.users.find_one.return_value = None
            assert main_module.sudo(0) is False


# ---------------------------------------------------------------------------
# get_news()
# ---------------------------------------------------------------------------

class TestGetNews:
    def test_returns_empty_list_on_http_error(self):
        bad = MagicMock()
        bad.status_code = 503

        with patch('requests.get', return_value=bad):
            result = main_module.get_news()

        assert result == []

    def test_returns_empty_list_on_exception(self):
        with patch('requests.get', side_effect=ConnectionError('timeout')):
            result = main_module.get_news()

        assert result == []

    def test_respects_limit(self):
        feed_item = '''
            <div class="bastian-feed-item">
                <a class="feed-post-link" href="https://g1.globo.com/n">T</a>
                <div class="feed-post-body-resumo">D</div>
                <img class="bstn-fd-picture-image" src="https://img.jpg">
            </div>'''

        feed_html = f'<html><body>{"" + feed_item * 10}</body></html>'
        article_html = b'<html><body><div class="mc-column content-text active-extra-styles">X</div></body></html>'

        feed_resp = MagicMock(status_code=200, content=feed_html.encode())
        art_resp = MagicMock(status_code=200, content=article_html)

        with patch('requests.get', side_effect=[feed_resp] + [art_resp] * 10):
            result = main_module.get_news(limit=3)

        assert len(result) <= 3

    def test_news_item_has_required_keys(self):
        feed_html = '''<html><body>
            <div class="bastian-feed-item">
                <a class="feed-post-link" href="https://g1.globo.com/n1">Manchete</a>
                <div class="feed-post-body-resumo">Resumo</div>
                <img class="bstn-fd-picture-image" src="https://img.jpg">
            </div>
        </body></html>'''.encode('utf-8')

        article_html = '''<html><body>
            <div class="mc-column content-text active-extra-styles">Texto completo</div>
            <p class="content-publication-data__from">Reporter</p>
        </body></html>'''.encode('utf-8')

        feed_resp = MagicMock(status_code=200, content=feed_html)
        art_resp = MagicMock(status_code=200, content=article_html)

        with patch('requests.get', side_effect=[feed_resp, art_resp]):
            result = main_module.get_news(limit=1)

        assert len(result) == 1
        assert set(result[0].keys()) >= {'title', 'description', 'link', 'image', 'autor', 'full_text'}

    def test_regression_no_src_literal_appended(self):
        """Regression: bug concatenava a string literal 'src' ao full_text para cada imagem."""
        feed_html = '''<html><body>
            <div class="bastian-feed-item">
                <a class="feed-post-link" href="https://g1.globo.com/n1">Titulo</a>
                <div class="feed-post-body-resumo">Desc</div>
                <img class="bstn-fd-picture-image" src="https://img.jpg">
            </div>
        </body></html>'''.encode('utf-8')

        article_html = '''<html><body>
            <div class="mc-column content-text active-extra-styles">Corpo</div>
            <div class="mc-column content-media__container">
                <img src="https://media1.jpg">
            </div>
            <div class="mc-column content-media__container">
                <img src="https://media2.jpg">
            </div>
        </body></html>'''.encode('utf-8')

        feed_resp = MagicMock(status_code=200, content=feed_html)
        art_resp = MagicMock(status_code=200, content=article_html)

        with patch('requests.get', side_effect=[feed_resp, art_resp]):
            result = main_module.get_news(limit=1)

        full_text = result[0]['full_text']
        isolated_src = [tok for tok in full_text.split() if tok == 'src']
        assert len(isolated_src) == 0, f"Bug regressão: 'src' literal isolado no full_text: {full_text!r}"

    def test_autor_is_none_when_missing(self):
        feed_html = '''<html><body>
            <div class="bastian-feed-item">
                <a class="feed-post-link" href="https://g1.globo.com/n">T</a>
                <div class="feed-post-body-resumo">D</div>
                <img class="bstn-fd-picture-image" src="https://i.jpg">
            </div>
        </body></html>'''.encode('utf-8')

        article_html = b'<html><body><div class="mc-column content-text active-extra-styles">X</div></body></html>'

        feed_resp = MagicMock(status_code=200, content=feed_html)
        art_resp = MagicMock(status_code=200, content=article_html)

        with patch('requests.get', side_effect=[feed_resp, art_resp]):
            result = main_module.get_news(limit=1)

        assert result[0]['autor'] is None


# ---------------------------------------------------------------------------
# upload_telegraph_image()
# ---------------------------------------------------------------------------

class TestUploadTelegraphImage:
    def test_returns_none_at_max_attempts(self):
        result = main_module.upload_telegraph_image('https://img.jpg', attempt=3)
        assert result is None

    def test_returns_none_when_image_download_fails(self):
        bad = MagicMock(status_code=404)

        with patch('requests.get', return_value=bad):
            with patch('telegraph.Telegraph'):
                result = main_module.upload_telegraph_image('https://img.jpg')

        assert result is None

    def test_returns_full_url_on_success(self):
        ok = MagicMock(status_code=200, content=b'bytes')
        mock_tg = MagicMock()
        mock_tg.upload_file.return_value = [{'src': '/file/abc123.jpg'}]

        with patch('requests.get', return_value=ok):
            with patch('telegraph.Telegraph', return_value=mock_tg):
                result = main_module.upload_telegraph_image('https://img.jpg')

        assert result == 'https://telegra.ph/file/abc123.jpg'

    def test_returns_none_on_exception(self):
        with patch('requests.get', side_effect=Exception('network down')):
            with patch('telegraph.Telegraph'):
                result = main_module.upload_telegraph_image('https://img.jpg')

        assert result is None


# ---------------------------------------------------------------------------
# create_telegraph_post()
# ---------------------------------------------------------------------------

class TestCreateTelegraphPost:
    def test_returns_url_title_link_tuple(self):
        mock_tg = MagicMock()
        mock_tg.create_page.return_value = {'url': 'https://telegra.ph/post-1'}

        with patch('telegraph.Telegraph', return_value=mock_tg):
            url, title, link = main_module.create_telegraph_post(
                'Título', 'Desc', 'https://g1.globo.com/n',
                'https://img.jpg', 'Autor', 'Texto completo'
            )

        assert url == 'https://telegra.ph/post-1'
        assert title == 'Título'
        assert link == 'https://g1.globo.com/n'

    def test_returns_none_triple_on_exception(self):
        with patch('telegraph.Telegraph', side_effect=Exception('api error')):
            url, title, link = main_module.create_telegraph_post(
                'T', 'D', 'L', 'I', 'A', 'F'
            )

        assert (url, title, link) == (None, None, None)

    def test_no_placeholder_text_in_html(self):
        captured = {}

        def fake_create(t, html_content='', author_name=''):
            captured['html'] = html_content
            return {'url': 'https://telegra.ph/x'}

        mock_tg = MagicMock()
        mock_tg.create_page.side_effect = fake_create

        with patch('telegraph.Telegraph', return_value=mock_tg):
            main_module.create_telegraph_post('T', 'D', 'L', 'I', 'A', 'F')

        assert 'Algum outro conteúdo aqui' not in captured.get('html', '')

    def test_html_contains_original_link(self):
        captured = {}

        def fake_create(t, html_content='', author_name=''):
            captured['html'] = html_content
            return {'url': 'https://telegra.ph/x'}

        mock_tg = MagicMock()
        mock_tg.create_page.side_effect = fake_create

        with patch('telegraph.Telegraph', return_value=mock_tg):
            main_module.create_telegraph_post(
                'T', 'D', 'https://g1.globo.com/materia', 'I', 'A', 'Texto'
            )

        assert 'https://g1.globo.com/materia' in captured.get('html', '')


# ---------------------------------------------------------------------------
# total_news() / delete_news()
# ---------------------------------------------------------------------------

class TestScheduledJobs:
    def test_total_news_sends_count_to_group(self):
        mock_bot = MagicMock()
        fake_news = [{'id': i} for i in range(4)]

        with patch.object(db_module, 'db') as mock_db:
            mock_db.news.find.return_value = iter(fake_news)
            with patch.object(main_module, 'bot', mock_bot):
                main_module.total_news()

        mock_bot.send_message.assert_called_once()
        msg = mock_bot.send_message.call_args[0][1]
        assert '4' in msg

    def test_delete_news_calls_remove_all(self):
        with patch.object(db_module, 'db') as mock_db:
            mock_db.news.delete_many = MagicMock()
            main_module.delete_news()
            mock_db.news.delete_many.assert_called_once_with({})


# ---------------------------------------------------------------------------
# _wait_minutes() — verifica que o scheduler é acionado a cada minuto
# ---------------------------------------------------------------------------

class TestWaitMinutes:
    def test_calls_run_pending_n_times(self):
        run_calls = []

        with patch('schedule.run_pending', side_effect=lambda: run_calls.append(1)):
            with patch('main.sleep'):
                main_module._wait_minutes(5)

        assert len(run_calls) == 5

    def test_sleeps_60s_per_iteration(self):
        sleep_calls = []

        with patch('schedule.run_pending'):
            with patch('main.sleep', side_effect=lambda s: sleep_calls.append(s)):
                main_module._wait_minutes(3)

        assert sleep_calls == [60, 60, 60]
