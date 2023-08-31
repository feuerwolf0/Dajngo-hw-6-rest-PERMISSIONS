from django_filters import rest_framework as filters

from .models import Advertisement


class AdvertisementFilter(filters.FilterSet):
    """Фильтры для объявлений."""

    creator = filters.CharFilter('creator__id')
    username = filters.CharFilter('creator__username', lookup_expr='icontains')
    first_name = filters.CharFilter('creator__first_name', lookup_expr='icontains')
    last_name = filters.CharFilter('creator__last_name', lookup_expr='icontains')
    created_at_before = filters.DateFilter('created_at', lookup_expr='lte')

    class Meta:
        model = Advertisement
        fields = ['creator', 'username', 'first_name', 'last_name', 'created_at_before']
