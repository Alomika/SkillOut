import json
import tempfile
from pathlib import Path

from django.test import TestCase, override_settings


@override_settings(ROOT_URLCONF="hello.urls")
class SubjectRatingsTests(TestCase):
	def setUp(self):
		self._tmpdir = tempfile.TemporaryDirectory()
		self.base_dir = Path(self._tmpdir.name)
		(self.base_dir / "scraped_text").mkdir(parents=True, exist_ok=True)

	def tearDown(self):
		self._tmpdir.cleanup()

	def _post_json(self, url, payload):
		return self.client.post(url, data=json.dumps(payload), content_type="application/json")

	@override_settings(BASE_DIR=None)
	def test_save_subject_ratings_writes_file_and_count(self):
		with override_settings(BASE_DIR=self.base_dir):
			response = self._post_json(
				"/api/save-subject-ratings/",
				{
					"rows": [
						{"semester": 1, "subject": "Mathematics", "stars": 5},
						{"semester": 2, "subject": "Physics", "stars": 3},
					]
				},
			)

			self.assertEqual(response.status_code, 200)
			body = response.json()
			self.assertEqual(body["count"], 2)

			ratings_file = self.base_dir / "scraped_text" / "latest_subject_ratings.txt"
			self.assertTrue(ratings_file.exists())
			self.assertEqual(
				ratings_file.read_text(encoding="utf-8").splitlines(),
				[
					"Semester 1 | Mathematics | Stars: 5",
					"Semester 2 | Physics | Stars: 3",
				],
			)

	def test_save_subject_ratings_invalid_stars_defaults_to_zero(self):
		with override_settings(BASE_DIR=self.base_dir):
			response = self._post_json(
				"/api/save-subject-ratings/",
				{
					"rows": [
						{"semester": 1, "subject": "Algorithms", "stars": "not-a-number"},
					]
				},
			)

			self.assertEqual(response.status_code, 200)
			ratings_file = self.base_dir / "scraped_text" / "latest_subject_ratings.txt"
			self.assertIn("Stars: 0", ratings_file.read_text(encoding="utf-8"))

	def test_save_subject_ratings_ignores_empty_subject(self):
		with override_settings(BASE_DIR=self.base_dir):
			response = self._post_json(
				"/api/save-subject-ratings/",
				{
					"rows": [
						{"semester": 1, "subject": "", "stars": 5},
						{"semester": 1, "subject": "Databases", "stars": 4},
					]
				},
			)

			self.assertEqual(response.status_code, 200)
			self.assertEqual(response.json()["count"], 1)

	def test_latest_subjects_fast_returns_saved_stars(self):
		with override_settings(BASE_DIR=self.base_dir):
			scraped_dir = self.base_dir / "scraped_text"
			(scraped_dir / "latest_subjects.json").write_text(
				json.dumps(
					{
						"semester_subjects": {
							"1": ["Mathematics", "Physics"],
						}
					}
				),
				encoding="utf-8",
			)
			(scraped_dir / "latest_subject_ratings.txt").write_text(
				"Semester 1 | Mathematics | Stars: 5",
				encoding="utf-8",
			)

			response = self._post_json(
				"/api/latest-subjects-fast/",
				{"fromSemester": 1, "toSemester": 1},
			)

			self.assertEqual(response.status_code, 200)
			rows = response.json()["rows"]
			stars_by_subject = {row["subject"]: row["stars"] for row in rows}
			self.assertEqual(stars_by_subject["Mathematics"], 5)
			self.assertIsNone(stars_by_subject["Physics"])
