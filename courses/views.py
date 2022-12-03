from rest_framework import generics

from courses.models import Course


class CoursesListAPIView(generics.ListCreateAPIView):
    queryset = Course.objects.all()
