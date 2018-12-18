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
    port = models.OneToOneField('Port', on_delete=models.PROTECT, null=True, blank=True,
                                related_name='connect_neighbour')
    hold_time = models.PositiveIntegerField()
    capability = MultiSelectField(choices=NeighbourCapability.model_choices(), null=False, blank=False)
    external_port_id = models.CharField(max_length=100)

    def __str__(self):
        return u"{}->{}".format(self.from_router, self.to_router)


class Router(models.Model):
    name = models.CharField(max_length=255, unique=True, null=False, blank=False)
    neighbours = models.ManyToManyField('self', related_name='neighbours', symmetrical=True, blank=True)

    def __str__(self):
        return u"{}".format(self.name)


class Slot(models.Model):
    router = models.ForeignKey(Router, on_delete=models.CASCADE, related_name='slots')
    # It shows the slot number on the router where it is placed on the router. e.g in node name -> 0/0/NPU0
    # 0(vertical row number)/0(slot number)/NPU0(Name of the port and last 0 shows the number of the port inside
    # the given slot)
    slot_number = models.PositiveIntegerField()

    class Meta:
        unique_together = ('router', 'slot_number')

    def __str__(self):
        return "{}({})".format(self.slot_number, self.router)


class CardAdminState(Enum):
    UP = 'UP'
    DOWN = 'DOWN'

    @classmethod
    def model_choices(cls):
        return tuple([(attr.value, attr.name) for attr in cls])


class Card(models.Model):
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


class Port(models.Model):
    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='ports')
    # 0/0/NPU0 it is the last integer like 0 in this case.
    port_number_inside_slot = models.PositiveIntegerField()
    # From 0/0/NPU0 it is NPU0
    node_name = models.CharField(max_length=255)
    node_type = models.CharField(max_length=255, default='Slice', blank=True)
    node_state = models.CharField(max_length=255)
    admin_state = models.CharField(max_length=100, choices=CardAdminState.model_choices(), blank=True, default='')

    class Meta:
        unique_together = ('card', 'port_number_inside_slot')

    @property
    def port_name(self):
        return "{}".format(self.node_name)

    def __str__(self):
        return self.port_name


class Interface(models.Model):
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

    name = models.CharField(max_length=255)
    port = models.OneToOneField(Port, on_delete=models.CASCADE, related_name='interface')
    ip_address = models.GenericIPAddressField(null=True, default='unassigned')
    status = models.CharField(max_length=100, choices=StatusChoices.choices())
    protocol = models.CharField(max_length=100, choices=ProtocolChoices.choices())
