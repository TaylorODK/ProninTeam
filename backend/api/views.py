from django.shortcuts import render
from django.db.models import Prefetch, Sum
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.mixins import (
    CreateModelMixin,
    RetrieveModelMixin,
    DestroyModelMixin,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from api.models import Collect, Payment, Comment, Like
from api.serializers import (
    LikeSerializer,
    CommentCreateSerializer,
    PaymentCreateSerializer,
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

    def get_permissions(self):
        if self.action == "create":
            return [IsAuthenticated()]
        return [
            AuthorPermission(),
        ]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["payment"] = get_object_or_404(
            Payment, id=self.kwargs.get("payment_id")
        )
        context["author"] = self.request.user
        return context

    def perform_create(self, serializer):
        user = self.request.user
        payment = get_object_or_404(Payment, id=self.kwargs.get("payment_id"))
        serializer.save(author=user, payment=payment)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return Response(
            {
                "Succes": True,
                "Message": "Лайк успешно создан",
                "Data": response.data,
            },
            status=status.HTTP_201_CREATED,
        )

    @action(
        detail=False,
        url_path=("delete"),
        methods=["DELETE"]
    )
    def delete_by_id(self, request, *args, **kwargs):
        payment = get_object_or_404(Payment, id=self.kwargs.get("payment_id"))
        like = Like.objects.filter(author=self.request.user, payment=payment).first()
        if not like:
            return Response(
                {
                    "Succes": False,
                    "Message": "Лайк не был найден",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        like.delete()
        return Response(
                {
                    "Succes": True,
                    "Message": "Лайк удален",
                },
                status=status.HTTP_200_OK,
            )


class CommentViewSet(DestroyModelMixin, GenericViewSet):

    queryset = Comment.objects.all()
    serializer_class = CommentCreateSerializer

    def get_permissions(self):
        if self.action == "create":
            return [IsAuthenticated()]
        return [
            AuthorPermission(),
        ]

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
            status=status.HTTP_201_CREATED,
        )

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class PaymentViewSet(CreateModelMixin, GenericViewSet):

    queryset = Payment.objects.all()
    serializer_class = PaymentCreateSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["collect"] = get_object_or_404(
            Collect, id=self.kwargs.get("collect_id")
        )
        return context

    def perform_create(self, serializer):
        collect = get_object_or_404(Collect, id=self.kwargs.get("collect_id"))
        serializer.save(author=self.request.user, collect=collect)


class CollectViewSet(RetrieveModelMixin, DestroyModelMixin, GenericViewSet):

    queryset = Collect.objects.all()
    permission_classes = [AuthorPermission]
    lookup_field = "id"

    def get_queryset(self):
        return Collect.objects.annotate(
            payments_sum=Sum("payments__amount")
        ).prefetch_related(
            Prefetch(
                "payments",
                queryset=Payment.objects.prefetch_related("comments", "likes"),
            )
        )

    def get_serializer_class(self):
        if self.action == "create":
            return CollectCreateSerializer
        if self.action == "retrieve":
            return CollectShowSerializer
        if self.action == "activate":
            return CollectReactivateSerializer
        if self.action == "partial_update":
            return CollectChangeSerializer
        if self.action == "deactivate":
            return CollectDeactivateSerializer
        return CollectShowSerializer

    def get_permissions(self):
        if self.action == "create":
            return [IsAuthenticated()]
        return [
            AuthorPermission(),
        ]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def create(self, request):
        serializer = CollectCreateSerializer(data=request.data)
        if serializer.is_valid():
            print(serializer.data)
            try:
                serializer.save()
            except Exception:
                return Response(
                    {
                        "success": False,
                        "message": "Ошибка создания сбора",
                        "errors": serializer.errors,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            return Response(
                {
                    "Succes": True,
                    "Message": "Сбор успешно создан",
                    "Data": serializer.data,
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

    @action(detail=True, methods=["PATCH"], url_path="activate")
    def activate(self, request, id=None):
        collect = self.get_object()
        serializer = CollectReactivateSerializer(
            collect, data=request.data, partial=True
        )
        if serializer.is_valid():
            try:
                serializer.save()
            except Exception:
                return Response(
                    {
                        "success": False,
                        "message": "Ошибка активации сбора",
                        "errors": serializer.errors,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
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
        detail=True,
        methods=["PATCH"],
        url_path="deactivate",
    )
    def deactivate(self, request, id=None):
        collect = self.get_object()
        serializer = CollectDeactivateSerializer(collect, data=request.data)
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

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
