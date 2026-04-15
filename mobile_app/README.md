# JobGuard Mobile

Flutter Android client for the JobGuard AI scanner.

## Current state
- The app source is included in `lib/`
- It targets the Django API contract in [docs/API_CONTRACT.md](../docs/API_CONTRACT.md)
- Flutter SDK was not available in this environment, so platform folders were not generated here

## Generate the Android shell
After installing Flutter, run from `mobile_app/`:

```bash
flutter create .
```

Then keep the generated Android project and the existing `lib/` source together.

## Run locally
Example for Android emulator:

```bash
flutter run --dart-define=JOBGUARD_API_BASE_URL=http://10.0.2.2:8000/api/v1
```

For a physical device on the same network, replace `10.0.2.2` with your machine IP.

## Run against a hosted backend
Example Render deployment:

```bash
flutter run --dart-define=JOBGUARD_API_BASE_URL=https://your-render-service.onrender.com/api/v1
```

For a release APK:

```bash
flutter build apk --dart-define=JOBGUARD_API_BASE_URL=https://your-render-service.onrender.com/api/v1
```

## Planned Android integrations
- text scanning
- URL scanning
- image capture and gallery import
- result rendering
- scam reporting
- retry and loading states

## Remaining setup
- Generate platform folders with Flutter
- Add Android share-intent wiring in the generated `android/` project if you want direct browser sharing in v1
- Run `flutter test`
- Run `flutter build apk`
