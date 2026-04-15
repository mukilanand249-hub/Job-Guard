import json
from unittest.mock import Mock, patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from .models import Blacklist, ScanHistory
from .services import AnalysisService, ServiceError


def sample_result(**overrides):
    payload = {
        "trust_score": 84,
        "verdict": "LEGIT",
        "recommendation": "Safe to Apply",
        "analysis_summary": "This looks legitimate.",
        "red_flags": [],
        "green_flags": ["Detailed description"],
    }
    payload.update(overrides)
    return payload


class AnalysisServiceTests(TestCase):
    def test_analyze_text_requires_non_empty_text(self):
        service = AnalysisService(detector=Mock())

        with self.assertRaises(ServiceError) as ctx:
            service.analyze_text("   ")

        self.assertEqual(ctx.exception.code, "empty_text")

    def test_analyze_url_returns_blacklist_result_and_persists_scan(self):
        Blacklist.objects.create(url="https://scam.example.com/job", reason="Known scam")
        detector = Mock()
        service = AnalysisService(detector=detector)

        result = service.analyze_url("https://scam.example.com/job")

        self.assertEqual(result["verdict"], "SCAM")
        self.assertEqual(result["scan_id"], 1)
        detector.scrape_url.assert_not_called()
        self.assertEqual(ScanHistory.objects.count(), 1)

    def test_analyze_url_scrape_failure_returns_specific_error(self):
        detector = Mock()
        detector.scrape_url.return_value = ""
        service = AnalysisService(detector=detector)

        with self.assertRaises(ServiceError) as ctx:
            service.analyze_url("https://example.com/job")

        self.assertEqual(ctx.exception.code, "scrape_failure")

    def test_analyze_image_ocr_failure_returns_specific_error(self):
        detector = Mock()
        detector.extract_text_from_image.return_value = ""
        service = AnalysisService(detector=detector)

        with self.assertRaises(ServiceError) as ctx:
            service.analyze_image(b"fake-image")

        self.assertEqual(ctx.exception.code, "ocr_failure")

    def test_analyze_text_persists_standardized_result(self):
        detector = Mock()
        detector.analyze.return_value = sample_result()
        service = AnalysisService(detector=detector)

        result = service.analyze_text("Software engineer role")

        self.assertEqual(result["verdict"], "LEGIT")
        self.assertIn("scan_id", result)
        self.assertEqual(ScanHistory.objects.count(), 1)

    def test_classifier_failure_is_wrapped(self):
        detector = Mock()
        detector.analyze.side_effect = RuntimeError("pipeline unavailable")
        service = AnalysisService(detector=detector)

        with self.assertRaises(ServiceError) as ctx:
            service.analyze_text("Software engineer role")

        self.assertEqual(ctx.exception.code, "classifier_failure")


class ApiViewTests(TestCase):
    def test_health_endpoint(self):
        response = self.client.get(reverse("api_health"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    @patch("core.views._service")
    def test_api_analyze_text_returns_standardized_payload(self, service_factory):
        service_factory.return_value.analyze_text.return_value = sample_result(scan_id=7)

        response = self.client.post(
            reverse("api_analyze_text"),
            data=json.dumps({"text": "Backend engineer"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["scan_id"], 7)
        self.assertEqual(body["verdict"], "LEGIT")

    @patch("core.views._service")
    def test_api_analyze_url_returns_validation_error(self, service_factory):
        service_factory.return_value.analyze_url.side_effect = ServiceError(
            "invalid_url",
            "Enter a valid URL.",
            400,
        )

        response = self.client.post(
            reverse("api_analyze_url"),
            data=json.dumps({"url": "not-a-url"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"]["code"], "invalid_url")

    @patch("core.views._service")
    def test_api_analyze_image_accepts_multipart_upload(self, service_factory):
        service_factory.return_value.analyze_image.return_value = sample_result(scan_id=9)
        image = SimpleUploadedFile("job.png", b"fake-image-bytes", content_type="image/png")

        response = self.client.post(reverse("api_analyze_image"), data={"image": image})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["scan_id"], 9)

    @patch("core.views._service")
    def test_api_report_scam_returns_success_payload(self, service_factory):
        service_factory.return_value.report_scam.return_value = {
            "message": "Report submitted successfully",
            "url": "https://example.com/job",
            "report_count": 1,
        }

        response = self.client.post(
            reverse("api_report_scam"),
            data=json.dumps({"url": "https://example.com/job", "reason": "fake recruiter"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["report_count"], 1)

    @patch("core.views._service")
    def test_legacy_analyze_endpoint_keeps_existing_shape(self, service_factory):
        service_factory.return_value.analyze_text.return_value = sample_result(scan_id=11)

        response = self.client.post(
            reverse("analyze"),
            data=json.dumps({"text": "Product manager"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["verdict"], "LEGIT")
        self.assertNotIn("scan_id", body)

    def test_report_scam_regression_path_updates_blacklist(self):
        response = self.client.post(
            reverse("report_scam"),
            data=json.dumps({"url": "https://example.com/job", "reason": "suspicious"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Blacklist.objects.count(), 1)
        self.assertEqual(Blacklist.objects.first().report_count, 1)
