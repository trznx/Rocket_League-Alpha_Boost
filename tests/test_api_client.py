import json
import unittest

from api_client import RocketLeagueAPI


def make_packet(player):
    return json.dumps(
        {
            "Event": "UpdateState",
            "Data": json.dumps({"Players": [player]}),
        }
    )


class RocketLeagueAPITests(unittest.TestCase):
    def setUp(self):
        self.api = RocketLeagueAPI()

    def parse_player(self, player):
        self.api._parse_packet(make_packet(player))

    def test_bboosting_true_marks_real_boosting(self):
        self.parse_player({"Shortcut": 1, "Speed": 81.9, "Boost": 33, "bBoosting": True})
        self.assertTrue(self.api.is_boosting)

    def test_missing_bboosting_does_not_start_boost_on_its_own(self):
        self.parse_player({"Shortcut": 1, "Speed": 0.0, "Boost": 33})
        self.assertFalse(self.api.is_boosting)

    def test_falling_boost_amount_counts_as_real_boosting(self):
        self.parse_player({"Shortcut": 1, "Speed": 20.0, "Boost": 33})
        self.parse_player({"Shortcut": 1, "Speed": 25.0, "Boost": 32})
        self.assertTrue(self.api.is_boosting)

    def test_recent_real_boost_activity_survives_single_missing_packet(self):
        self.api.BOOST_ACTIVITY_WINDOW = 0.2
        self.parse_player({"Shortcut": 1, "Speed": 81.9, "Boost": 33, "bBoosting": True})
        self.parse_player({"Shortcut": 1, "Speed": 81.9, "Boost": 33})
        self.assertTrue(self.api.is_boosting)

    def test_constant_boost_without_flag_stays_false_after_window(self):
        self.api.BOOST_ACTIVITY_WINDOW = 0.0
        self.parse_player({"Shortcut": 1, "Speed": 81.9, "Boost": 33, "bBoosting": True})
        self.parse_player({"Shortcut": 1, "Speed": 81.9, "Boost": 33})
        self.assertFalse(self.api.is_boosting)


if __name__ == "__main__":
    unittest.main()
