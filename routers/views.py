from rest_framework.generics import ListAPIView, RetrieveAPIView

from routers.models import Router, Card, Neighbour
from routers.serializers import RouterSerializer, CardSerializer, RouterDetailSerializer, NeighbourSerializer


class RouterListView(ListAPIView):
    serializer_class = RouterSerializer
    queryset = Router.objects.all().prefetch_related('neighbours_router')

    def get(self, request, *args, **kwargs):
        s = super().get(request, *args, **kwargs)
        print(s)
        return s


class RouterDetailView(RetrieveAPIView):
    serializer_class = RouterDetailSerializer
    queryset = Router.objects.all().prefetch_related('neighbours_router')


class RouterCardsListView(ListAPIView):
    serializer_class = CardSerializer
    queryset = Card.objects.all()

    def get_queryset(self):
        return super().get_queryset().filter(slot__router__pk=self.kwargs['router_id'])


class RouterNeighboursListView(ListAPIView):
    serializer_class = NeighbourSerializer
    queryset = Neighbour.objects.all()

    def get_queryset(self):
        queryset = super().get_queryset().filter(from_router__id=self.kwargs['pk']).select_related('to_router')
        print(queryset.query)
        return queryset
