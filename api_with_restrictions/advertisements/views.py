from django.http import Http404
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .filters import AdvertisementFilter
from .manager import ManageFavorite
from .models import Advertisement, AdvertisementDraftChoices
from .permissions import IsOwner
from .serializers import AdvertisementSerializer


class AdvertisementViewSet(ModelViewSet, ManageFavorite):
    """ViewSet для объявлений."""
    queryset = Advertisement.objects.all()
    serializer_class = AdvertisementSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = AdvertisementFilter

    def get_queryset(self):
        queryset = Advertisement.objects.all()
        # Применяю фильтрацию
        queryset = self.filter_queryset(queryset)
        # Добавляю аннотацию в виде дополнитеьного поля "в избранном"
        queryset = self.annotate_qs_is_favorite_field(queryset)
        return queryset

    def get_permissions(self):
        """Получение прав для действий."""
        if self.action in ["create", "update", "partial_update", 'destroy']:
            return [IsAuthenticated(), IsOwner()]
        return []

    def list(self, request, *args, **kwargs):
        base_queryset = self.get_queryset()
        # Получаю все опубликованные посты
        queryset = base_queryset.filter(draft=AdvertisementDraftChoices.NO)
        queryset_owner_unpublished = None
        if request.user.is_authenticated:
            # Выбираю все неопубликованные объявления автора
            queryset_owner_unpublished = base_queryset.filter(creator=request.user,
                                             draft=AdvertisementDraftChoices.YES)

        if queryset_owner_unpublished:
            # Объединяю все неопубликованные посты автора и все опубликованные посты
            queryset = queryset.union(queryset_owner_unpublished)

        # Если пользователь суперюзер отобразить все опубликованные и черновые объявления
        if request.user.is_superuser:
            queryset = base_queryset

        serializer_class = self.get_serializer_class()
        serializer = serializer_class(queryset, many=True)
        return Response(serializer.data, status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        queryset = self.get_queryset()

        instance = get_object_or_404(queryset, pk=pk)

        if request.user.is_authenticated:
            # Если суперпользователь - черновик отобразиться любого пользователя
            if not request.user.is_superuser:
                # Если пользователь не является владельцем и объявление не опубликовано
                if instance.creator != request.user and instance.draft == AdvertisementDraftChoices.YES:
                    raise Http404
        else:
            # Если объявление не опубликовано
            if instance.draft == AdvertisementDraftChoices.YES:
                raise Http404

        serializer_class = self.get_serializer_class()
        serializer = serializer_class(instance)
        return Response(serializer.data, status.HTTP_200_OK)

