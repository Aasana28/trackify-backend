# apps/braindump/views.py
# Brain Dump CRUD + AI proxy using Groq (free, works in India)

import httpx
from django.conf import settings as django_settings
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import BrainDump
from .serializers import BrainDumpSerializer


class BrainDumpListCreateView(generics.ListCreateAPIView):
    serializer_class = BrainDumpSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return BrainDump.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class BrainDumpDetailView(generics.RetrieveDestroyAPIView):
    serializer_class = BrainDumpSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return BrainDump.objects.filter(user=self.request.user)


class AIProxyView(APIView):
    """
    POST /api/ai/chat/
    Uses Groq API (free, fast, works in India)
    Model: llama3-8b-8192
    """
    permission_classes = [IsAuthenticated]

    GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
    MODEL    = "llama-3.3-70b-versatile"

    def post(self, request):
        messages = request.data.get("messages", [])
        system   = request.data.get("system", "")
        api_key  = django_settings.GROQ_API_KEY

        if not api_key:
            return Response(
                {"error": "AI service is not configured. Please set GROQ_API_KEY."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        # Build messages list for Groq (OpenAI-compatible format)
        groq_messages = []
        if system:
            groq_messages.append({"role": "system", "content": system})
        groq_messages.extend(messages)

        payload = {
            "model":       self.MODEL,
            "messages":    groq_messages,
            "max_tokens":  1200,
            "temperature": 0.7,
        }

        try:
            with httpx.Client(timeout=60) as client:
                resp = client.post(
                    self.GROQ_URL,
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type":  "application/json",
                    },
                    json=payload,
                )

            if resp.status_code != 200:
                error_body = resp.json() if resp.content else {}
                error_msg  = error_body.get("error", {}).get("message", "AI request failed.")
                return Response({"error": error_msg}, status=status.HTTP_502_BAD_GATEWAY)

            data    = resp.json()
            content = data["choices"][0]["message"]["content"]
            return Response({"content": content.strip()})

        except httpx.TimeoutException:
            return Response(
                {"error": "AI request timed out. Please try again."},
                status=status.HTTP_504_GATEWAY_TIMEOUT,
            )
        except Exception as exc:
            return Response(
                {"error": f"AI request failed: {str(exc)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
