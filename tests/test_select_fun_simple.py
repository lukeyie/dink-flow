import unittest
import sys, types

# inject fake playwright to allow importing dinkup_bot in this environment
sync_module = types.ModuleType('playwright.sync_api')
setattr(sync_module, 'sync_playwright', lambda *a, **k: None)
sys.modules['playwright.sync_api'] = sync_module

import dinkup_bot as bot

class SimpleSelectTest(unittest.TestCase):
    def test_only_fun_selected(self):
        events = [
            {
                'id': 'evt1',
                'title': '測試場次',
                'location': '松0高中',
                'divisions': [
                    {'id': 'comp1', 'level': 'competitive', 'courtCount': 1},
                    {'id': 'fun1', 'level': 'fun', 'courtCount': 1},
                ],
            },
            {
                'id': 'evt2',
                'title': '無歡樂場次',
                'location': '松0高中',
                'divisions': [
                    {'id': 'comp2', 'level': 'competitive', 'courtCount': 1},
                ],
            },
        ]
        selected = bot.select_registrations(events)
        # expect only the first event's fun division selected
        self.assertTrue(any(s['event_id'] == 'evt1' and s['level'] == 'fun' and s['division_id'] == 'fun1' for s in selected))
        # ensure no selection uses a competitive division
        self.assertFalse(any(s['level'] == 'competitive' for s in selected))

if __name__ == '__main__':
    unittest.main()
