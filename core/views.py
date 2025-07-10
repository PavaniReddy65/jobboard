from django.shortcuts import get_object_or_404
from rest_framework import viewsets, generics, pagination, permissions, filters, status, serializers
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.db import models
from django.http import HttpResponse
from rest_framework import filters
from django.shortcuts import render
from .models import JobListing
from django.contrib.auth.decorators import login_required
from .models import Employer, Candidate, JobListing, JobApplication
from .serializers import (
    EmployerSerializer,
    CandidateSerializer,
    JobListingSerializer,
    JobApplicationSerializer,
    UserRegistrationSerializer
)


# Home View
def home_page(request):
    return render(request, 'index.html')
def jobs_page(request):
    return render(request, 'jobs.html')

def job_list_view(request):
    jobs = JobListing.objects.all()
    return render(request, 'job_list.html', {'jobs': jobs})

# User Registration with Email Notification
class UserRegistrationAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer

    def perform_create(self, serializer):
        user = serializer.save()
        # Send simple welcome email (console backend)
        send_mail(
            'Welcome to JobBoard',
            f'Hello {user.username}, thanks for registering!',
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=True,
        )


# Employer CRUD
class EmployerViewSet(viewsets.ModelViewSet):
    queryset = Employer.objects.all()
    serializer_class = EmployerSerializer
    permission_classes = [IsAuthenticated]


# Candidate CRUD - connected to logged in user automatically on create
class CandidateViewSet(viewsets.ModelViewSet):
    queryset = Candidate.objects.all()
    serializer_class = CandidateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# Pagination for jobs
class JobListingPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50


# Job Listings with filtering, pagination, public read but authenticated to post
from rest_framework import filters

class JobListingViewSet(viewsets.ModelViewSet):
    queryset = JobListing.objects.all()
    serializer_class = JobListingSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = JobListingPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    
    # Enable search on these fields
    search_fields = ['location', 'title', 'employer__company_name']

    # Enable ordering on these fields
    ordering_fields = ['salary', 'posted_on']
    ordering = ['-posted_on']  # Default ordering: latest first

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by minimum salary
        salary = self.request.query_params.get('salary')
        if salary:
            queryset = queryset.filter(salary__gte=salary)

        # Filter by posted_on date (e.g. jobs posted after a certain date)
        posted_after = self.request.query_params.get('posted_after')
        if posted_after:
            queryset = queryset.filter(posted_on__gte=posted_after)

        return queryset




# Job Applications CRUD
class JobApplicationViewSet(viewsets.ModelViewSet):
    queryset = JobApplication.objects.all()
    serializer_class = JobApplicationSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        candidate = get_object_or_404(Candidate, user=self.request.user)
        job = serializer.validated_data.get('job_listing')

        # Check if candidate already applied for this job
        if JobApplication.objects.filter(candidate=candidate, job_listing=job).exists():
            raise serializers.ValidationError("You have already applied for this job.")

        serializer.save(candidate=candidate)


# Job stats API - authenticated users only
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def job_stats(request):
    total_jobs = JobListing.objects.count()
    total_applications = JobApplication.objects.count()
    jobs_per_employer = Employer.objects.annotate(job_count=models.Count('joblisting')).values('company_name', 'job_count')
    return Response({
        'total_jobs': total_jobs,
        'total_applications': total_applications,
        'jobs_per_employer': list(jobs_per_employer),
    })
def job_listings_page(request):
    jobs = JobListing.objects.all()

    # Filters
    title = request.GET.get('title')
    location = request.GET.get('location')
    salary = request.GET.get('salary')

    if title:
        jobs = jobs.filter(title__icontains=title)
    if location:
        jobs = jobs.filter(location__icontains=location)
    if salary:
        jobs = jobs.filter(salary__gte=salary)

    return render(request, 'job_listings.html', {'jobs': jobs})


# Apply to a job (POST only, requires login)
@login_required
def apply_to_job(request, job_id):
    if request.method == 'POST':
        candidate = get_object_or_404(Candidate, user=request.user)
        job = get_object_or_404(JobListing, id=job_id)

        # Prevent duplicate applications
        if JobApplication.objects.filter(candidate=candidate, job_listing=job).exists():
            return HttpResponse("You already applied.")

        JobApplication.objects.create(candidate=candidate, job_listing=job)
        return redirect('job_listings')

    return HttpResponse("Invalid request method", status=405)