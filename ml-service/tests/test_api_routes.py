"""Tests for the model-serving API scaffold while inference is blocked."""

import unittest

from fastapi.testclient import TestClient

from src.api.main import app


class ApiRouteTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_health_reports_liveness_without_claiming_model_readiness(self):
        response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})
        self.assertNotIn("model", response.text.lower())

    def test_model_info_reports_blocker_without_local_paths(self):
        response = self.client.get("/model-info")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "blocked")
        self.assertFalse(response.json()["prediction_available"])
        self.assertIn("fitted pipeline", response.json()["reason"])
        self.assertNotIn("D:\\", response.text)
        self.assertNotIn("C:\\", response.text)

    def test_predict_returns_service_unavailable_not_a_fake_prediction(self):
        response = self.client.post("/predict", json={"unverified": "input"})

        self.assertEqual(response.status_code, 503)
        self.assertEqual(
            response.json(),
            {"detail": "Prediction is unavailable because no deployable model is configured."},
        )
        self.assertNotIn("traceback", response.text.lower())
        self.assertNotIn("prediction", response.json())

    def test_openapi_lists_routes_without_claiming_a_prediction_schema(self):
        response = self.client.get("/openapi.json")

        self.assertEqual(response.status_code, 200)
        paths = response.json()["paths"]
        self.assertIn("/health", paths)
        self.assertIn("/model-info", paths)
        self.assertIn("/predict", paths)
        self.assertNotIn("requestBody", paths["/predict"]["post"])


if __name__ == "__main__":
    unittest.main()
