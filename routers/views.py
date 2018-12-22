from django.db.models import F, Q
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from routers.models import Router, Card, Neighbour
from routers.serializers import RouterSerializer, CardSerializer, RouterDetailSerializer, NeighbourSerializer


class RouterListView(ListAPIView):
    serializer_class = RouterSerializer
    queryset = Router.objects.all()


class RouterDetailView(RetrieveAPIView):
    # permission_classes = (IsAuthenticated, )
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
        return queryset


class TopologyView(APIView):

    def get(self, request, router_id=None, format=None):
        connected_routers = set()
        routers = Router.objects.all().values('id', label=F('name'))
        neighbours = Neighbour.objects.all().values('from_router', 'to_router')
        if router_id:
            neighbours = neighbours.filter(Q(from_router_id=router_id) | Q(to_router_id=router_id))

        if router_id:
            # If the router_id is provided then only display the routers that are connected to this router.
            edges = []
            for edge in neighbours:
                edges.append({'from': edge['from_router'], 'to': edge['to_router']})
                connected_routers.add(edge['from_router'])
                connected_routers.add(edge['to_router'])
            routers = [router for router in routers if router['id'] in connected_routers]
        else:
            edges = [{'from': edge['from_router'], 'to': edge['to_router']} for edge in neighbours]
        data = {'nodes': list(routers), 'edges': edges}
        return Response(data)
