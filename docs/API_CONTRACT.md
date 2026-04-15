# JobGuard API Contract

Base URL examples:
- Local Android emulator: `http://10.0.2.2:8000/api/v1`
- Local physical device on same LAN: `http://<your-machine-ip>:8000/api/v1`

## `GET /health`
Response:

```json
{
  "status": "ok",
  "service": "jobguard-api"
}
```

## `POST /analyze-text`
Request:

```json
{
  "text": "Full job description text"
}
```

## `POST /analyze-url`
Request:

```json
{
  "url": "https://example.com/job-posting",
  "text": ""
}
```

The optional `text` field lets thin clients provide already extracted page text while still preserving the URL for analysis history.

## `POST /analyze-image`
Request:
- Multipart form upload with `image`

## Shared analysis response

```json
{
  "scan_id": 42,
  "trust_score": 84,
  "verdict": "LEGIT",
  "recommendation": "Safe to Apply",
  "analysis_summary": "This job posting appears to be legitimate based on standard indicators.",
  "red_flags": [],
  "green_flags": [
    "Detailed description"
  ]
}
```

## `POST /report-scam`
Request:

```json
{
  "url": "https://example.com/job-posting",
  "reason": "Suspicious recruiter details"
}
```

Response:

```json
{
  "message": "Report submitted successfully",
  "url": "https://example.com/job-posting",
  "report_count": 1
}
```

## Error shape

```json
{
  "error": {
    "code": "invalid_url",
    "message": "Enter a valid URL."
  }
}
```

Known error codes:
- `empty_text`
- `invalid_url`
- `unsupported_image`
- `ocr_failure`
- `scrape_failure`
- `classifier_failure`
- `method_not_allowed`
