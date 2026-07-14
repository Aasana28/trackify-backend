# apps/reminders/views.py

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Reminder
from .serializers import ReminderSerializer


class ReminderListCreateView(generics.ListCreateAPIView):
    serializer_class   = ReminderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Reminder.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ReminderDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class   = ReminderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Reminder.objects.filter(user=self.request.user)


class ToggleReminderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            reminder = Reminder.objects.get(pk=pk, user=request.user)
        except Reminder.DoesNotExist:
            return Response({"error": "Reminder not found."}, status=404)

        reminder.done = not reminder.done
        reminder.save()
        return Response(ReminderSerializer(reminder).data)
