from django.test import TestCase

from bulbs.utils.vault import read, VaultError, _make_key

from django.core.cache import cache

from mock import patch

MEMORY_CACHE = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'vault-test',
    }
}

class VaultReadTestCase(TestCase):

    def test_make_key(self):
        self.assertEqual('vault:read:1:one:two', _make_key('one', 'two'))

    def test_backstop_hit(self):
        with self.settings(CACHES=MEMORY_CACHE):
            cache.clear()

            # Saved to backstop cache
            with patch('bulbs.utils.vault._read_endpoint', return_value='RESPONSE'):
                self.assertEqual('RESPONSE', read('path'))

            # Loads from backstop cache
            with patch('bulbs.utils.vault._read_endpoint', side_effect=VaultError):
                self.assertEqual('RESPONSE', read('path'))

    def test_backstop_miss(self):
        with patch('bulbs.utils.vault._read_endpoint', side_effect=VaultError):
            with patch('bulbs.utils.vault.logger') as mock_logger:
                with self.assertRaises(VaultError):
                    self.assertEqual('RESPONSE', read('path'))
                    self.assertTrue(mock_logger.exception.call_args)  # Exception logged

    def test_cache_miss_then_hit(self):
        with self.settings(CACHES=MEMORY_CACHE):
            cache.clear()

            with patch('bulbs.utils.vault._read_endpoint', return_value='RESPONSE') as mock_endpoint:

                self.assertEqual('RESPONSE', read('path'))
                self.assertEqual(1, mock_endpoint.call_count)

                self.assertEqual('RESPONSE', read('path'))
                self.assertEqual(1, mock_endpoint.call_count)
