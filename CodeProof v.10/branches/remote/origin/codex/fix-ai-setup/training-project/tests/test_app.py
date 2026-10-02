"""Healthy baseline expectations for the three controlled incidents."""
import json
import unittest
from datetime import datetime, timezone

from app import fresh_count, request_name, serialize_date


class TrainingTests(unittest.TestCase):
    def test_request_name(self):
        self.assertEqual(request_name({"username": "learner"}), "learner")

    def test_date_serialization(self):
        value = datetime(2026, 1, 1, tzinfo=timezone.utc)
        self.assertEqual(json.loads(serialize_date(value)),
                         {"created_at": "2026-01-01T00:00:00+00:00"})

    def test_database_initialization(self):
        self.assertEqual(fresh_count(), 0)
