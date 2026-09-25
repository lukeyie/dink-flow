import unittest
import requests
from unittest.mock import patch
import dinkup_bot as bot
from tests.test_dinkup_bot import response, event


class FallbackTests(unittest.TestCase):
    def setUp(self):
        p1 = patch.object(bot.requests, "Session")
        self.session_factory = p1.start()
        self.addCleanup(p1.stop)
        self.session = self.session_factory.return_value.__enter__.return_value

    def test_register_once_uses_fallback_on_explicit_rejection(self):
        # Manually construct a registration that includes a fallback entry
        registration = {
            "event_id": "event-1",
            "division_id": "comp",
            "level": "competitive",
            "title": "測試競技場",
            "location": "松山",
            "fallback": {
                "event_id": "event-1",
                "division_id": "fun",
                "level": "fun",
                "title": "測試歡樂場",
                "location": "松山",
            },
        }

        # Simulate POST: first response is explicit rejection (409), second is success
        self.session.post.side_effect = [response({"error": "名額已滿"}, 409), response(status=201)]
        attempted = set()
        from threading import Lock
        lock = Lock()
        headers = {}
        bot.register_once(self.session, headers, registration, attempted, lock, "2026-09-27")
        # register_once marks attempted entries in the provided set
        self.assertEqual(attempted, {("event-1", "comp"), ("event-1", "fun")})


if __name__ == "__main__":
    unittest.main()
