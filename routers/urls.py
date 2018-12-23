from django.urls import path

from routers.views import RouterListView, RouterDetailView, RouterCardsListView, TopologyView

urlpatterns = [
    path('', RouterListView.as_view(), name='routers_list'),
    path('topology/', TopologyView.as_view(), name='routers_topology'),
    path('topology/<int:router_id>', TopologyView.as_view(), name='single_routers_topology'),
    path('<int:pk>/', RouterDetailView.as_view(), name='routers_detail'),
    path('<int:router_id>/cards/', RouterCardsListView.as_view(), name='cards_list'),
]
