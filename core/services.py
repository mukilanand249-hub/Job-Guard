import logging
from dataclasses import dataclass
from typing import Any
from typing import TYPE_CHECKING

from django.core.exceptions import ValidationError
from django.core.validators import URLValidator

from .models import Blacklist, ScanHistory

if TYPE_CHECKING:
    from .ai_engine import FraudDetector

logger = logging.getLogger(__name__)


@dataclass
class ServiceError(Exception):
    code: str
    message: str
    status: int

    def as_dict(self) -> dict[str, Any]:
        return {
            "error": {
                "code": self.code,
                "message": self.message,
            }
        }


class AnalysisService:
    def __init__(self, detector: 'FraudDetector' | None = None):
        self.detector = detector
        self._validator = URLValidator()

    def analyze_text(self, text: str) -> dict[str, Any]:
        normalized_text = self._normalize_text(text)
        if not normalized_text:
            raise ServiceError("empty_text", "Text is required.", 400)

        result = self._run_classifier(normalized_text)
        return self._persist_and_serialize(url="", text=normalized_text, result=result)

    def analyze_url(self, url: str, text: str = "") -> dict[str, Any]:
        normalized_url = self._normalize_url(url)
        normalized_text = self._normalize_text(text)

        blacklist_payload = self._check_blacklist(normalized_url)
        if blacklist_payload:
            return self._persist_and_serialize(
                url=normalized_url,
                text=normalized_text or normalized_url,
                result=blacklist_payload,
            )

        if not normalized_text:
            normalized_text = self._extract_text_from_url(normalized_url)

        result = self._run_classifier(normalized_text, normalized_url)
        return self._persist_and_serialize(url=normalized_url, text=normalized_text, result=result)

    def analyze_image(self, image_bytes: bytes) -> dict[str, Any]:
        if not image_bytes:
            raise ServiceError("unsupported_image", "Image upload is required.", 400)

        extracted_text = self._detector().extract_text_from_image(image_bytes)
        extracted_text = self._normalize_text(extracted_text)
        if not extracted_text:
            raise ServiceError(
                "ocr_failure",
                "Could not extract text from image. Ensure it is clear.",
                400,
            )

        result = self._run_classifier(extracted_text)
        return self._persist_and_serialize(url="", text=extracted_text, result=result)

    def report_scam(self, url: str, reason: str) -> dict[str, Any]:
        normalized_url = self._normalize_url(url)
        reason_text = self._normalize_text(reason) or "Reported by user"

        obj, created = Blacklist.objects.get_or_create(
            url=normalized_url,
            defaults={"reason": reason_text},
        )
        if not created:
            obj.report_count += 1
            if reason_text and obj.reason != reason_text:
                obj.reason = reason_text
            obj.save(update_fields=["report_count", "reason"])

        return {
            "message": "Report submitted successfully",
            "url": normalized_url,
            "report_count": obj.report_count,
        }

    def _normalize_text(self, text: str | None) -> str:
        return (text or "").strip()

    def _normalize_url(self, url: str | None) -> str:
        normalized_url = (url or "").strip()
        if not normalized_url:
            raise ServiceError("invalid_url", "URL is required.", 400)

        try:
            self._validator(normalized_url)
        except ValidationError as exc:
            raise ServiceError("invalid_url", "Enter a valid URL.", 400) from exc

        return normalized_url

    def _check_blacklist(self, url: str) -> dict[str, Any] | None:
        if not Blacklist.objects.filter(url=url).exists():
            return None

        return {
            "trust_score": 0,
            "verdict": "SCAM",
            "recommendation": "Do Not Apply",
            "analysis_summary": "This URL has been reported as a known scam by the community.",
            "red_flags": ["Listed in Community Blacklist"],
            "green_flags": [],
        }

    def _extract_text_from_url(self, url: str) -> str:
        try:
            extracted_text = self._detector().scrape_url(url)
        except Exception as exc:
            logger.exception("URL extraction failed for %s", url)
            raise ServiceError(
                "scrape_failure",
                "Could not extract text from the URL.",
                502,
            ) from exc

        extracted_text = self._normalize_text(extracted_text)
        if not extracted_text:
            raise ServiceError(
                "scrape_failure",
                "Could not extract text. The site might be using JavaScript or blocking bots. Please copy and paste the text manually.",
                400,
            )
        return extracted_text

    def _run_classifier(self, text: str, url: str | None = None) -> dict[str, Any]:
        try:
            return self._detector().analyze(text, url)
        except ServiceError:
            raise
        except Exception as exc:
            logger.exception("Classifier failure")
            raise ServiceError(
                "classifier_failure",
                "The analysis engine could not complete the scan.",
                500,
            ) from exc

    def _persist_and_serialize(self, url: str, text: str, result: dict[str, Any]) -> dict[str, Any]:
        scan = ScanHistory.objects.create(
            url=url or None,
            text_content=text[:500],
            trust_score=result["trust_score"],
            verdict=result["verdict"],
        )
        return {
            "scan_id": scan.id,
            "trust_score": result["trust_score"],
            "verdict": result["verdict"],
            "recommendation": result["recommendation"],
            "analysis_summary": result["analysis_summary"],
            "red_flags": result["red_flags"],
            "green_flags": result["green_flags"],
        }

    def _detector(self) -> 'FraudDetector':
        if self.detector is None:
            from .ai_engine import FraudDetector

            self.detector = FraudDetector()
        return self.detector
