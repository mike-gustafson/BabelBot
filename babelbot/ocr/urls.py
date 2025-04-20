from django.urls import path
from .views import OCRAdminView, OCRLogsView

urlpatterns = [
    path('admin/', OCRAdminView.as_view(), name='ocr_admin'),
    path('admin/logs/', OCRLogsView.as_view(), name='ocr_logs'),
] 