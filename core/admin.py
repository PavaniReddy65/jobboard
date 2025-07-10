

# Register your models here.
# 7. admin.py
from django.contrib import admin
from .models import Employer, Candidate, JobListing, JobApplication

admin.site.register(Employer)
admin.site.register(Candidate)
admin.site.register(JobListing)
admin.site.register(JobApplication)