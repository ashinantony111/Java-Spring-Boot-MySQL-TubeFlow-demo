import unittest
from fastapi.testclient import TestClient
from app.main import app
from app.database import db_manager

class TubeFlowTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_database_initialization(self):
        status = db_manager.get_status()
        print("\nDatabase Engine:", status["active_engine"], "- Connected:", status["is_connected"])
        self.assertTrue(status["is_connected"])
        self.assertIn("videos", status["tables"])
        self.assertGreater(status["table_counts"].get("videos", 0), 0)

    def test_home_page(self):
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("TubeFlow", resp.text)
        self.assertIn("Blooming Flora", resp.text)

    def test_api_videos_list(self):
        resp = self.client.get("/api/videos")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("videos", data)
        self.assertGreaterEqual(len(data["videos"]), 6)

    def test_watch_page(self):
        resp = self.client.get("/watch?v=1")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("custom-video-player", resp.text)
        self.assertIn("Planet Earth 4K", resp.text)

    def test_video_reactions(self):
        # Like video 1 as user 1
        resp = self.client.post("/api/videos/1/reaction", json={"user_id": 1, "reaction_type": "like"})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data["success"])
        self.assertIn("likes", data)

    def test_comment_creation_and_deletion(self):
        # Add comment
        resp = self.client.post("/api/videos/1/comments", json={"user_id": 1, "content": "Awesome MySQL video platform!"})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data["success"])
        comment_id = data["comment"]["id"]

        # Delete comment
        del_resp = self.client.delete(f"/api/comments/{comment_id}?user_id=1")
        self.assertEqual(del_resp.status_code, 200)
        self.assertTrue(del_resp.json()["success"])

    def test_channel_subscription(self):
        # Toggle sub
        resp = self.client.post("/api/channels/2/subscribe", json={"user_id": 1})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data["success"])
        self.assertIn("subscribed", data)

    def test_video_range_streaming(self):
        # Test HTTP 206 Partial Content range request
        resp = self.client.get("/api/stream/sample_nature_flower.mp4", headers={"Range": "bytes=0-1024"})
        self.assertEqual(resp.status_code, 206)
        self.assertEqual(resp.headers.get("Content-Type"), "video/mp4")
        self.assertIn("bytes 0-1024/", resp.headers.get("Content-Range", ""))
        self.assertEqual(len(resp.content), 1025)
        print("Range stream test passed: returned 1025 bytes with HTTP 206")

    def test_raw_sql_query(self):
        resp = self.client.post("/api/db/query", json={"sql": "SELECT id, title, views_count FROM videos LIMIT 3;"})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["row_count"], 3)
        print("Raw SQL execution duration:", data["duration_ms"], "ms")

    def test_channel_page(self):
        resp = self.client.get("/channel/techvoyager")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("TechVoyager", resp.text)

    def test_history_page(self):
        resp = self.client.get("/history")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("Watch History", resp.text)

    def test_subscriptions_page(self):
        resp = self.client.get("/subscriptions")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("Subscription Feed", resp.text)

    def test_database_page(self):
        resp = self.client.get("/database")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("MySQL Database Center", resp.text)

if __name__ == "__main__":
    unittest.main()
