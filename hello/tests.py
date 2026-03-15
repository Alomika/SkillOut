import json
import sys
import types
from unittest.mock import MagicMock, patch

import requests
from django.test import TestCase


class ScrapeSemesterValidationTests(TestCase):
	endpoint = "/api/scrape-text/"

	def _post(self, payload):
		return self.client.post(
			self.endpoint,
			data=json.dumps(payload),
			content_type="application/json",
		)

	def test_requires_from_and_to_semester(self):
		response = self._post({"url": "https://example.com"})

		self.assertEqual(response.status_code, 400)
		self.assertEqual(
			response.json()["error"],
			"Fields 'fromSemester' and 'toSemester' are required.",
		)

	def test_rejects_when_from_semester_is_greater_than_to_semester(self):
		response = self._post(
			{
				"url": "https://example.com",
				"fromSemester": 5,
				"toSemester": 3,
			}
		)

		self.assertEqual(response.status_code, 400)
		self.assertEqual(
			response.json()["error"],
			"fromSemester cannot be greater than toSemester.",
		)

	def test_rejects_semesters_below_one(self):
		response = self._post(
			{
				"url": "https://example.com",
				"fromSemester": 0,
				"toSemester": 3,
			}
		)

		self.assertEqual(response.status_code, 400)
		self.assertEqual(
			response.json()["error"],
			"fromSemester and toSemester must be at least 1.",
		)

	def test_rejects_semesters_above_eight(self):
		response = self._post(
			{
				"url": "https://example.com",
				"fromSemester": 1,
				"toSemester": 9,
			}
		)

		self.assertEqual(response.status_code, 400)
		self.assertEqual(
			response.json()["error"],
			"fromSemester and toSemester must be at most 8.",
		)


class ScrapeSubjectsResponseTests(TestCase):
	endpoint = "/api/scrape-text/"

	def _post(self, payload):
		return self.client.post(
			self.endpoint,
			data=json.dumps(payload),
			content_type="application/json",
		)

	@patch("hello.views.requests.get")
	def test_returns_subject_list_for_selected_semester_interval(self, mock_get):
		html = """
		<html><body>
			<h3>1 rudens semestras</h3>
			<p>Matematika</p>
			<h3>2 pavasario semestras</h3>
			<p>Programavimas</p>
			<h3>3 rudens semestras</h3>
			<p>Duomenu bazes</p>
		</body></html>
		"""
		mock_response = MagicMock()
		mock_response.text = html
		mock_response.raise_for_status.return_value = None
		mock_get.return_value = mock_response

		fake_ollama = types.SimpleNamespace(
			chat=lambda **kwargs: {
				"message": {
					"content": json.dumps(
						{
							"study_subjects": [
								"Programavimas",
								"Duomenu bazes",
							]
						}
					)
				}
			}
		)

		with patch.dict(sys.modules, {"ollama": fake_ollama}):
			response = self._post(
				{
					"url": "https://example.com/study-plan",
					"fromSemester": 2,
					"toSemester": 3,
				}
			)

		self.assertEqual(response.status_code, 200)
		data = response.json()
		self.assertIsInstance(data["study_subjects"], list)
		self.assertEqual(data["subjects_count"], 2)
		self.assertEqual(
			data["study_subjects"],
			["Programavimas", "Duomenu bazes"],
		)

	@patch("hello.views.requests.get")
	def test_returns_no_results_message_when_subjects_not_found(self, mock_get):
		html = """
		<html><body>
			<h3>4 pavasario semestras</h3>
			<p>Nera dalyku</p>
		</body></html>
		"""
		mock_response = MagicMock()
		mock_response.text = html
		mock_response.raise_for_status.return_value = None
		mock_get.return_value = mock_response

		fake_ollama = types.SimpleNamespace(
			chat=lambda **kwargs: {"message": {"content": '{"study_subjects": []}'}}
		)

		with patch.dict(sys.modules, {"ollama": fake_ollama}):
			response = self._post(
				{
					"url": "https://example.com/study-plan",
					"fromSemester": 4,
					"toSemester": 4,
				}
			)

		self.assertEqual(response.status_code, 200)
		data = response.json()
		self.assertEqual(data["study_subjects"], [])
		self.assertEqual(data["subjects_count"], 0)
		self.assertEqual(
			data["message"],
			"Rezultatu nerasta pasirinktame semestru intervale.",
		)


class ScrapeUrlValidationTests(TestCase):
	endpoint = "/api/scrape-text/"

	def _post(self, payload):
		return self.client.post(
			self.endpoint,
			data=json.dumps(payload),
			content_type="application/json",
		)

	def test_requires_url(self):
		response = self._post({
			"fromSemester": 1,
			"toSemester": 2,
		})

		self.assertEqual(response.status_code, 400)
		self.assertEqual(
			response.json()["error"],
			"Field 'url' is required.",
		)

	def test_rejects_invalid_url_format(self):
		response = self._post({
			"url": "ftp://example.com",
			"fromSemester": 1,
			"toSemester": 2,
		})

		self.assertEqual(response.status_code, 400)
		self.assertEqual(
			response.json()["error"],
			"URL must start with http:// or https://.",
		)

	@patch("hello.views.requests.get")
	def test_handles_4xx_error(self, mock_get):
		mock_response = MagicMock()
		http_error = requests.HTTPError("404 Client Error")
		http_error.response = MagicMock()
		http_error.response.status_code = 404
		mock_response.raise_for_status.side_effect = http_error
		mock_get.return_value = mock_response

		response = self._post({
			"url": "https://example.com",
			"fromSemester": 1,
			"toSemester": 2,
		})

		self.assertEqual(response.status_code, 400)
		self.assertIn("HTTP error: 404", response.json()["error"])

	@patch("hello.views.requests.get")
	def test_handles_5xx_error(self, mock_get):
		mock_response = MagicMock()
		http_error = requests.HTTPError("500 Server Error")
		http_error.response = MagicMock()
		http_error.response.status_code = 500
		mock_response.raise_for_status.side_effect = http_error
		mock_get.return_value = mock_response

		response = self._post({
			"url": "https://example.com",
			"fromSemester": 1,
			"toSemester": 2,
		})

		self.assertEqual(response.status_code, 400)
		self.assertIn("HTTP error: 500", response.json()["error"])

	@patch("hello.views.requests.get")
	@patch("hello.views.time.sleep")
	def test_handles_timeout_after_retries(self, mock_sleep, mock_get):
		mock_get.side_effect = requests.Timeout("Request timed out")

		response = self._post({
			"url": "https://example.com",
			"fromSemester": 1,
			"toSemester": 2,
		})

		self.assertEqual(response.status_code, 400)
		self.assertIn("Failed after 3 attempts", response.json()["error"])
		self.assertEqual(mock_get.call_count, 3)
		self.assertEqual(mock_sleep.call_count, 2)  # Sleeps after first two attempts

	@patch("hello.views.requests.get")
	@patch("hello.views.time.sleep")
	def test_handles_connection_error_with_retry_success(self, mock_sleep, mock_get):
		mock_get.side_effect = [
			requests.ConnectionError("Connection failed"),
			requests.ConnectionError("Connection failed"),
			MagicMock(text="<html></html>", raise_for_status=lambda: None)
		]

		fake_ollama = types.SimpleNamespace(
			chat=lambda **kwargs: {"message": {"content": '{"study_subjects": []}'}}
		)

		with patch.dict(sys.modules, {"ollama": fake_ollama}):
			response = self._post({
				"url": "https://example.com",
				"fromSemester": 1,
				"toSemester": 2,
			})

		self.assertEqual(response.status_code, 200)
		self.assertEqual(mock_get.call_count, 3)
		self.assertEqual(mock_sleep.call_count, 2)

	@patch("hello.views.requests.get")
	@patch("hello.views.time.sleep")
	def test_handles_connection_error_retry_fail(self, mock_sleep, mock_get):
		mock_get.side_effect = requests.ConnectionError("Connection failed")

		response = self._post({
			"url": "https://example.com",
			"fromSemester": 1,
			"toSemester": 2,
		})

		self.assertEqual(response.status_code, 400)
		self.assertIn("Failed after 3 attempts", response.json()["error"])
		self.assertEqual(mock_get.call_count, 3)
		self.assertEqual(mock_sleep.call_count, 2)
