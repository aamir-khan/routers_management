from enum import Enum

from django.db import models

from multiselectfield import MultiSelectField


class Neighbour(models.Model):

    class NeighbourCapability(Enum):
        ROUTER = 'R'
        BRIDGE = 'B'
        TELEPHONE = 'T'
        DOCSIS_Cable_Device = 'C'
        WLAN_ACCESS_POINT = 'W'
        REPEATER = 'R'
        STATION = 'S'
        OTHERS = 'O'

        @classmethod
        def model_choices(cls):
            return tuple([(attr.value, attr.name) for attr in cls])

    from_router = models.ForeignKey('Router', on_delete=models.CASCADE, related_name='connected_from')
    to_router = models.ForeignKey('Router', on_delete=models.CASCADE, related_name='connected_to')
    local_intf = models.CharField(max_length=100)
    local_interface = models.OneToOneField(
        'InterfacePort', on_delete=models.CASCADE, related_name='from_interface')
    external_interface = models.OneToOneField(
        'InterfacePort', on_delete=models.CASCADE, related_name='external_interface')
    hold_time = models.PositiveIntegerField()
    capability = MultiSelectField(choices=NeighbourCapability.model_choices(), null=False, blank=False)
    external_port_id = models.CharField(max_length=100)

    def __str__(self):
        return u"{}->{}".format(self.from_router, self.to_router)


class Router(models.Model):
    name = models.CharField(max_length=255, unique=True, null=False, blank=False)
    neighbours_router = models.ManyToManyField(
        'self', through='Neighbour', related_name='neighbours', symmetrical=False, blank=True)

    def __str__(self):
        return u"{}".format(self.name)


class Slot(models.Model):
    router = models.ForeignKey(Router, on_delete=models.CASCADE, related_name='slots')
    slot_number = models.PositiveIntegerField()

    class Meta:
        unique_together = ('router', 'slot_number')

    def __str__(self):
        return "{}".format(self.slot_number)


class Card(models.Model):

    class CardAdminState(Enum):
        UP = 'UP'
        DOWN = 'DOWN'

        @classmethod
        def model_choices(cls):
            return tuple([(attr.value, attr.name) for attr in cls])

    slot = models.OneToOneField(Slot, on_delete=models.CASCADE, related_name='card')
    # If the slots are placed on each other(multi-chassis system) it will show the vertical number.
    # In our case(single-chassis system) it should be always 0.
    vertical_row_number = models.IntegerField(blank=True, default=0)
    node_type = models.CharField(max_length=255)
    node_state = models.CharField(max_length=255)
    admin_state = models.CharField(max_length=100, choices=CardAdminState.model_choices(), blank=True, default='')
    config_state = models.CharField(max_length=100)

    @property
    def node_name(self):
        return "{}/{}".format(self.vertical_row_number, self.slot.slot_number)

    def __str__(self):
        return "{}".format(self.node_type)

    class Meta:
        ordering = ('slot__slot_number', )


class InterfacePort(models.Model):
    class StatusChoices(Enum):
        UP = 'UP'
        DOWN = 'DOWN'
        SHUTDOWN = 'SHUTDOWN'

        @classmethod
        def choices(cls):
            return tuple([(attr.value, attr.name) for attr in cls])

    class ProtocolChoices(Enum):
        UP = 'UP'
        DOWN = 'DOWN'
        SHUTDOWN = 'SHUTDOWN'

        @classmethod
        def choices(cls):
            return tuple([(attr.value, attr.name) for attr in cls])
    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='interfaces')
    # HundredGigE0/0/0/0 it is the last integer like 0 in this case.
    port_number_inside_card = models.PositiveIntegerField()
    # Something like this HundredGigE0/0/0/0
    name = models.CharField(max_length=255)
    ip_address = models.GenericIPAddressField(null=True, default='unassigned')
    status = models.CharField(max_length=100, choices=StatusChoices.choices())
    protocol = models.CharField(max_length=100, choices=ProtocolChoices.choices())

    def __str__(self):
        return "{}({})".format(self.name, self.card)
