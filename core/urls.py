from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('analyze', views.analyze, name='analyze'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('report_scam', views.report_scam, name='report_scam'),
    path('api/v1/health', views.api_health, name='api_health'),
    path('api/v1/analyze-text', views.api_analyze_text, name='api_analyze_text'),
    path('api/v1/analyze-url', views.api_analyze_url, name='api_analyze_url'),
    path('api/v1/analyze-image', views.api_analyze_image, name='api_analyze_image'),
    path('api/v1/report-scam', views.api_report_scam, name='api_report_scam'),
]
