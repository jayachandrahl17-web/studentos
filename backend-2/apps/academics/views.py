from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Semester, Subject, Module, Topic, TopicProgress
from .serializers import (
    SemesterSerializer,
    SubjectSerializer,
    ModuleSerializer,
    TopicSerializer,
)


class SemesterViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Semester.objects.all()
    serializer_class = SemesterSerializer

    @action(detail=False, methods=["get"])
    def current(self, request):
        semester = Semester.objects.order_by("-number").first()
        if not semester:
            return Response({"detail": "No semester is configured."}, status=404)
        return Response(SemesterSerializer(semester).data)


class SubjectViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = (
        Subject.objects
        .select_related("semester")
        .prefetch_related("modules__topics")
    )
    serializer_class = SubjectSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        semester = self.request.query_params.get("semester")

        if semester:
            queryset = queryset.filter(semester_id=semester)

        return queryset

    @action(detail=True, methods=["get"])
    def syllabus(self, request, pk=None):
        """
        Return one subject together with all its modules and topics.
        """
        subject = self.get_object()

        modules = []

        for module in subject.modules.all():
            module_data = ModuleSerializer(module, context=self.get_serializer_context()).data

            module_data["topics"] = TopicSerializer(
                module.topics.all(),
                many=True,
                context=self.get_serializer_context(),
            ).data

            modules.append(module_data)

        subject_data = SubjectSerializer(subject, context=self.get_serializer_context()).data
        subject_data["modules"] = modules

        return Response(subject_data)


class ModuleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = (
        Module.objects
        .select_related("subject")
        .prefetch_related("topics")
    )
    serializer_class = ModuleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        subject = self.request.query_params.get("subject")

        if subject:
            queryset = queryset.filter(subject_id=subject)

        return queryset

    @action(detail=True, methods=["get"])
    def syllabus(self, request, pk=None):
        """
        Return one module together with all its topics.
        """
        module = self.get_object()

        module_data = ModuleSerializer(module, context=self.get_serializer_context()).data

        module_data["topics"] = TopicSerializer(
            module.topics.all(),
            many=True,
            context=self.get_serializer_context(),
        ).data

        return Response(module_data)


class TopicViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = (
        Topic.objects
        .select_related("module__subject")
        .prefetch_related("quiz_attempts", "past_questions")
    )
    serializer_class = TopicSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        module = self.request.query_params.get("module")
        subject = self.request.query_params.get("subject")

        if module:
            queryset = queryset.filter(module_id=module)

        if subject:
            queryset = queryset.filter(
                module__subject_id=subject
            )

        return queryset

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        """
        Mark a topic as completed or not completed.
        """
        topic = self.get_object()

        completed = request.data.get("completed", True)
        if not isinstance(completed, bool):
            return Response({"detail": "completed must be a boolean."}, status=400)

        progress, _ = TopicProgress.objects.get_or_create(user=request.user, topic=topic)
        progress.completed = completed
        progress.save(update_fields=["completed"])

        return Response(
            TopicSerializer(topic, context=self.get_serializer_context()).data
        )