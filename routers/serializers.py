from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer

from routers.models import Router, Neighbour, Card, Slot, InterfacePort


class NeighbourSerializer(ModelSerializer):

    class Meta:
        model = Neighbour
        fields = '__all__'


class RouterNeighbourSerializer(ModelSerializer):

    class Meta:
        model = Router
        fields = ('id', 'name')


class RouterSerializer(ModelSerializer):

    class Meta:
        model = Router
        fields = ('id', 'name')


class InterfacePortSerializer(ModelSerializer):
    connected_router = SerializerMethodField()

    class Meta:
        model = InterfacePort
        fields = '__all__'

    # noinspection PyMethodMayBeStatic
    def get_connected_router(self, obj):
        neighbour = Neighbour.objects.filter(local_interface=obj).first()

        return neighbour.to_router.pk if neighbour else ""


class CardDetailSerializer(ModelSerializer):
    interfaces = InterfacePortSerializer(many=True)

    class Meta:
        model = Card
        fields = '__all__'


class SlotDetailSerializer(ModelSerializer):
    card = CardDetailSerializer()

    class Meta:
        model = Slot
        fields = ('id', 'slot_number', 'card')


class RouterDetailSerializer(ModelSerializer):
    neighbours = RouterNeighbourSerializer(source='neighbours_router', many=True)
    slots = SlotDetailSerializer(many=True)

    class Meta:
        model = Router
        fields = ('id', 'name', 'slots', 'neighbours')


class CardSerializer(ModelSerializer):

    class Meta:
        model = Card
        fields = '__all__'
