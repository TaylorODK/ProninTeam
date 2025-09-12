from django.urls import path, include
from rest_framework_nested import routers

from api.views import (
    LikeViewSet,
    CommentViewSet,
    PaymentViewSet,
    CollectViewSet,
)

router = routers.SimpleRouter()
router.register(r"collects", CollectViewSet, basename="collect")

collect_router = routers.NestedSimpleRouter(
    router, r"collects", lookup="collect"
)
collect_router.register(
    r"payments", PaymentViewSet, basename="collect-payments"
)

payment_router = routers.NestedSimpleRouter(
    collect_router, r"payments", lookup="payment"
)
payment_router.register(r"like", LikeViewSet, basename="payment-like")
payment_router.register(r"comment", CommentViewSet, basename="payment-comment")


urlpatterns = [
    path("", include(router.urls)),
    path("", include(collect_router.urls)),
    path("", include(payment_router.urls)),
]
