from django.urls import path, include

from rest_framework.routers import DefaultRouter
from .views import (
    EmployerViewSet,
    CandidateViewSet,
    JobListingViewSet,
    JobApplicationViewSet,
    home_page,
    jobs_page,
    job_list_view,
    UserRegistrationAPIView,
    job_stats,
    job_listings_page,
    apply_to_job
)

router = DefaultRouter()
router.register(r'employers', EmployerViewSet)
router.register(r'candidates', CandidateViewSet)
router.register(r'jobs', JobListingViewSet)
router.register(r'applications', JobApplicationViewSet)

urlpatterns = [
    path('', home_page, name='home'),
    path('register/', UserRegistrationAPIView.as_view(), name='user-register'),
    path('job-stats/', job_stats, name='job-stats'),
    path('', include(router.urls)),
    path('job-listings/', job_list_view, name='job-list'),
    path('jobs/', job_listings_page, name='job_listings'),
    path('apply/<int:job_id>/', apply_to_job, name='apply_job'),
    path('jobs/', jobs_page, name='jobs'),
    
]
