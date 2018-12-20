from django.urls import path

from routers.views import RouterListView, RouterDetailView, RouterCardsListView, RouterNeighboursListView

urlpatterns = [
    path('', RouterListView.as_view(), name='routers_list'),
    path('<int:pk>/', RouterDetailView.as_view(), name='routers_detail'),
    path('<int:pk>/neighbours/', RouterNeighboursListView.as_view(), name='routers_detail'),
    path('<int:router_id>/cards/', RouterCardsListView.as_view(), name='cards_list'),
]