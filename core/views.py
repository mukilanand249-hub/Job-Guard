import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import ScanHistory
from .services import AnalysisService, ServiceError


def _service() -> AnalysisService:
    return AnalysisService()


def _json_body(request) -> dict:
    if not request.body:
        return {}
    return json.loads(request.body)


def _legacy_error(message: str, status: int) -> JsonResponse:
    return JsonResponse({'error': message}, status=status)


def _api_error(exc: ServiceError) -> JsonResponse:
    return JsonResponse(exc.as_dict(), status=exc.status)

def home(request):
    return render(request, 'index.html')


@csrf_exempt
def analyze(request):
    if request.method != 'POST':
        return _legacy_error('Invalid method', 405)

    try:
        service = _service()
        if request.content_type == 'application/json':
            data = _json_body(request)
            text = data.get('text', '')
            url = data.get('url', '')
            if url:
                result = service.analyze_url(url=url, text=text)
            else:
                result = service.analyze_text(text=text)
        else:
            image = request.FILES.get('image')
            if image:
                result = service.analyze_image(image.read())
            else:
                text = request.POST.get('text', '')
                url = request.POST.get('url', '')
                if url:
                    result = service.analyze_url(url=url, text=text)
                else:
                    result = service.analyze_text(text=text)

        legacy_payload = dict(result)
        legacy_payload.pop('scan_id', None)
        return JsonResponse(legacy_payload)
    except ServiceError as exc:
        return _legacy_error(exc.message, exc.status)
    except Exception as exc:
        return _legacy_error(str(exc), 500)


@csrf_exempt
def report_scam(request):
    if request.method != 'POST':
        return _legacy_error('Invalid method', 405)

    try:
        data = _json_body(request)
        result = _service().report_scam(url=data.get('url'), reason=data.get('reason', ''))
        return JsonResponse({'message': result['message']})
    except ServiceError as exc:
        return _legacy_error(exc.message, exc.status)
    except Exception as exc:
        return _legacy_error(str(exc), 500)


@csrf_exempt
def api_health(request):
    if request.method != 'GET':
        return JsonResponse({'error': {'code': 'method_not_allowed', 'message': 'Invalid method'}}, status=405)
    return JsonResponse({'status': 'ok', 'service': 'jobguard-api'})


@csrf_exempt
def api_analyze_text(request):
    if request.method != 'POST':
        return JsonResponse({'error': {'code': 'method_not_allowed', 'message': 'Invalid method'}}, status=405)

    try:
        data = _json_body(request)
        result = _service().analyze_text(text=data.get('text', ''))
        return JsonResponse(result)
    except ServiceError as exc:
        return _api_error(exc)


@csrf_exempt
def api_analyze_url(request):
    if request.method != 'POST':
        return JsonResponse({'error': {'code': 'method_not_allowed', 'message': 'Invalid method'}}, status=405)

    try:
        data = _json_body(request)
        result = _service().analyze_url(url=data.get('url', ''), text=data.get('text', ''))
        return JsonResponse(result)
    except ServiceError as exc:
        return _api_error(exc)


@csrf_exempt
def api_analyze_image(request):
    if request.method != 'POST':
        return JsonResponse({'error': {'code': 'method_not_allowed', 'message': 'Invalid method'}}, status=405)

    try:
        image = request.FILES.get('image')
        result = _service().analyze_image(image.read() if image else b'')
        return JsonResponse(result)
    except ServiceError as exc:
        return _api_error(exc)


@csrf_exempt
def api_report_scam(request):
    if request.method != 'POST':
        return JsonResponse({'error': {'code': 'method_not_allowed', 'message': 'Invalid method'}}, status=405)

    try:
        data = _json_body(request)
        result = _service().report_scam(url=data.get('url'), reason=data.get('reason', ''))
        return JsonResponse(result)
    except ServiceError as exc:
        return _api_error(exc)

def dashboard(request):
    scans = ScanHistory.objects.all()
    total_scans = scans.count()
    scam_count = scans.filter(verdict='SCAM').count()
    legit_count = scans.filter(verdict='LEGIT').count()
    suspicious_count = scans.filter(verdict='SUSPICIOUS').count()
    
    context = {
        'total_scans': total_scans,
        'scam_count': scam_count,
        'legit_count': legit_count,
        'suspicious_count': suspicious_count
    }
    return render(request, 'dashboard.html', context)
