from django.contrib import admin
from django.urls import path, include
from core.views import home_page
from core.views import job_list_view
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_page, name='home'),
    path('job-list/', job_list_view, name='job-list'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # login
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'), # refresh token
    path('api/', include('core.urls')),  # API routes live here
    # Optionally add path('', include('core.urls')) if you want homepage at root
]

