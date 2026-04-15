# Deploy JobGuard Backend To Render

Start with `docs/RENDER_PHONE_SETUP_GUIDE.md` if you want the most practical step-by-step version for getting the backend online and reconnecting the phone app.

This project can run on Render as a Django web service. The mobile app can then talk to the hosted API from anywhere.

## 1. Push this project to GitHub
- Render deploys from a Git repository.
- Commit the current project and push it to GitHub.

## 2. Create the Render web service
- In Render, choose `New` -> `Blueprint` if you want Render to read `render.yaml`
- Or choose `New` -> `Web Service` and connect the repository manually

If you create it manually, use:
- Runtime: `Python`
- Build Command: `./build.sh`
- Start Command: `gunicorn jobguard_project.wsgi:application`

## 3. Set environment variables
Render should have these values:

- `DJANGO_DEBUG=False`
- `DJANGO_SECRET_KEY=<generated-random-secret>`
- `DJANGO_ALLOWED_HOSTS=<your-render-service>.onrender.com`
- `DJANGO_CSRF_TRUSTED_ORIGINS=https://<your-render-service>.onrender.com`
- `JOBGUARD_PRELOAD_MODEL=False`

Optional:
- `DATABASE_URL=<Render Postgres database URL>`
- `TESSERACT_CMD=<only if your environment actually provides tesseract>`

## 4. Database choice
- For a quick demo, SQLite may still boot, but it is not a good long-term hosted database.
- For a proper hosted deployment, create a Render Postgres database and set `DATABASE_URL`.

## 5. Important OCR note
- The image scan feature depends on Tesseract.
- Standard Render Python services do not automatically provide system-level Tesseract binaries.
- Text scan and URL scan are the easiest features to get live first.
- If image OCR is required on Render, the safer next step is moving to a Docker-based deploy that installs Tesseract explicitly.

## 6. Verify the backend
After deploy, open:

`https://<your-render-service>.onrender.com/api/v1/health`

Expected response:

```json
{
  "status": "ok",
  "service": "jobguard-api"
}
```

## 7. Connect the Flutter app
Build the Android app with the hosted API URL:

```bash
flutter build apk --dart-define=JOBGUARD_API_BASE_URL=https://<your-render-service>.onrender.com/api/v1
```

Or run directly on a connected device:

```bash
flutter run --dart-define=JOBGUARD_API_BASE_URL=https://<your-render-service>.onrender.com/api/v1
```

## 8. What will work best first
- Paste text scanning
- URL scanning
- Scam reporting

## 9. What may need extra deployment work
- Image OCR on hosted infrastructure
- Selenium-based scraping on hosts with limited browser support
