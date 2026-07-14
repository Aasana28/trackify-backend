# apps/applications/views.py
# CRUD endpoints for job applications

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Application, TimelineEntry
from .serializers import ApplicationSerializer, TimelineEntrySerializer


class ApplicationListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/applications/     — get all applications of logged-in user
    POST /api/applications/     — create new application
    """
    serializer_class   = ApplicationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Only return applications belonging to the logged-in user
        queryset = Application.objects.filter(user=self.request.user)

        # Optional filters from query params
        # Example: /api/applications/?status=Applied
        status_filter = self.request.query_params.get("status")
        search        = self.request.query_params.get("search")

        if status_filter and status_filter != "All":
            queryset = queryset.filter(status=status_filter)

        if search:
            queryset = queryset.filter(
                company__icontains=search
            ) | queryset.filter(
                role__icontains=search
            )

        return queryset


class ApplicationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/applications/<id>/  — get single application
    PUT    /api/applications/<id>/  — update application
    DELETE /api/applications/<id>/  — delete application
    """
    serializer_class   = ApplicationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # User can only access their own applications
        return Application.objects.filter(user=self.request.user)


class AddTimelineEntryView(APIView):
    """
    POST /api/applications/<id>/timeline/
    Body: { stage, date, note }
    Adds a new stage to an application's timeline
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            application = Application.objects.get(pk=pk, user=request.user)
        except Application.DoesNotExist:
            return Response({"error": "Application not found."}, status=404)

        serializer = TimelineEntrySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(application=application)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
