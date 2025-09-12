from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from api.models import Collect, Payment, Comment, Like
from api.serializers import (
    LikeSerializer,
    CommentShowSerializer,
    CommentCreateSerializer,
    PaymentCreateSerializer,
    PaymentShowSerializer,
    CollectShowSerializer,
    CollectCreateSerializer,
    CollectReactivateSerializer,
    CollectChangeSerializer,
    CollectDeactivateSerializer,
)
from api.permissions import AuthorPermission

# Create your views here.


class LikeViewSet(CreateModelMixin, GenericViewSet):

    queryset = Like.objects.all()
    serializer_class = LikeSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        payment = get_object_or_404(Payment, id=self.kwargs.get("post_id"))
        serializer.save(author=user, payment=payment)
    
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return Response(
            {
                "Succes": True,
                "Message": "Лайк успешно создан",
                "Data": response.data,
            },
            status=status.HTTP_201_CREATED
        )


class CommentViewSet(CreateModelMixin, GenericViewSet):

    queryset = Comment.objects.all()
    serializer_class = CommentCreateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        payment = get_object_or_404(Payment, id=self.kwargs.get("payment_id"))
        serializer.save(author=user, payment=payment)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return Response(
            {
                "Succes": True,
                "Message": "Комментарий успешно создан",
                "Data": response.data,
            },
            status=status.HTTP_201_CREATED
        )


class PaymentViewSet(CreateModelMixin, GenericViewSet):

    queryset = Payment.objects.all()
    serializer_class = PaymentCreateSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    def perform_create(self, serializer):
        user = self.request.user
        payment = get_object_or_404(Payment, id=self.kwargs.get("payment_id"))
        serializer.save(author=user, payment=payment)


class CollectViewSet(ModelViewSet):

    queryset = Collect.objects.all()
    permission_classes = [AuthorPermission]
    lookup_field = "id"

    def get_queryset(self):
        return Collect.objects.prefetch_related(
            Prefetch(
                "payments",
                queryset=Payment.objects.prefetch_related("comments", "likes")
            )
        )

    def get_serializer_class(self):
        if self.action == "create":
            return CollectCreateSerializer
        if self.action == "retrieve":
            return CollectShowSerializer
        if self.action == "activate":
            return CollectReactivateSerializer
        if self.action == "update":
            return CollectChangeSerializer
        if self.action == "deactivate":
            return CollectDeactivateSerializer
        return CollectShowSerializer

    def get_permissions(self):
        if self.action == "create":
            return [
                IsAuthenticated()
            ]
        return [
            AuthorPermission(),
        ]

    def create(self, request):
        user = self.request.user
        serializer = CollectCreateSerializer(author=user, data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
            except Exception:
                return Response("Ошибка создания сбора")
            return Response(
                {
                    "Succes": True,
                    "Message": "Сбор успешно создан",
                    "Data": serializer.data
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {
                "Succes": False,
                "Message": "Ошибка создания сбора",
                "Error": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(
        methods=["PATCH"],
        url_path="activate"
    )
    def activate(self, request):
        user = self.request.user
        collect = get_object_or_404(Collect, id=self.kwargs.get("collect_id"))
        serializer = CollectReactivateSerializer(collect, author=user, data=request.data, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
            except Exception:
                return Response("Ошибка активации сбора")
            return Response(
                {
                    "Succes": True,
                    "Message": "Сбор успешно активирован",
                    "Data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {
                "Succes": False,
                "Message": "Ошибка активации сбора",
                "Error": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(
        methods=["PATCH"],
        url_path="deactivate",
    )
    def deactivate(self, request):
        user = self.request.user
        collect = get_object_or_404(Collect, id=self.kwargs.get("collect_id"))
        serializer = CollectDeactivateSerializer(collect, author=user)
        if serializer.is_valid():
            try:
                serializer.save()
            except Exception:
                return Response("Ошибка остановки сбора")
            return Response(
                {
                    "Succes": True,
                    "Message": "Сбор успешно остановлен",
                    "Data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {
                "Succes": False,
                "Message": "Ошибка остановки сбора",
                "Error": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
