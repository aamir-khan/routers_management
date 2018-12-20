import os
from os import listdir
from os.path import isfile, join

from django.core.management import BaseCommand

from routers.models import Router, Slot, Card, Neighbour, InterfacePort


class Command(BaseCommand):
    help = 'Loads the routers data'

    VALID_CARDS = ['0/0', '0/1', '0/2', '0/3', '0/4', '0/5', '0/6', '0/7']
    VALID_INTERFACES = ['HundredGigE', 'TenGigE']

    @staticmethod
    def add_routers(router_files_names):
        for router_files_name in router_files_names:
            router_name = router_files_name.split('.')[0]
            router, created = Router.objects.get_or_create(name=router_name)
            if created:
                Command.add_slots(router)

    @staticmethod
    def add_slots(router):
        number = 0
        while number < 8:
            Slot.objects.get_or_create(router=router, slot_number=number)
            number += 1

    @staticmethod
    def add_cards_info(router, router_data):
        index = 4
        while True:
            data = router_data[index]
            # The start of the data from "show platform" command
            if '---------------------------' in data:
                cards_port_data = router_data[index+1:]
                cards_port_data_index = 0
                while cards_port_data_index < len(cards_port_data):
                    data_ = cards_port_data[cards_port_data_index]
                    cards_port_data_index += 1
                    data_ = data_.split()
                    if not data_:
                        continue
                    if data_[1] != 'Slice':
                        slot_number = data_[0].split('/')[1]
                        try:
                            slot_number = int(slot_number)
                            if not 0 <= slot_number < 8:
                                continue
                        except ValueError:
                            continue
                        slot = Slot.objects.get(router=router, slot_number=slot_number)

                        Card.objects.get_or_create(slot=slot, defaults={
                            'node_type': data_[1], 'node_state': data_[2], 'admin_state': data_[3],
                            'config_state': data_[4]
                        })
                break
            index += 1

    @staticmethod
    def add_neighbour(router, data):
        index = 0
        while index < len(data):
            single_line = data[index]
            if 'show lldp neighbor' in single_line:
                index += 7
                neighbours_data = data[index:]

                for neighbor in neighbours_data:
                    if neighbor == '\n':
                        break
                    else:
                        neighbor = neighbor.split()
                        name = neighbor[0]
                        try:
                            name_without_dotted_extension = name.split('.')[0]
                            neighbor_router = Router.objects.filter(name=name_without_dotted_extension).first()
                            if not neighbor_router:
                                continue
                            local_intf = neighbor[1]
                            #Hu0/0/0/1
                            local_intf_parts = local_intf.split('/')
                            slot_number = local_intf_parts[1]
                            port_number = local_intf_parts[-1]

                            external_intf = neighbor[-1]
                            # Hu0/0/0/1
                            external_intf_parts = external_intf.split('/')
                            external_slot_number = external_intf_parts[1]
                            external_port_number = external_intf_parts[-1]

                            local_interface = InterfacePort.objects.get(
                                card__slot__router=router,
                                card__slot__slot_number=slot_number,
                                port_number_inside_card=port_number
                            )
                            external_interface = InterfacePort.objects.get(
                                card__slot__router=neighbor_router,
                                card__slot__slot_number=external_slot_number,
                                port_number_inside_card=external_port_number
                            )
                            neighbor_obj, created = Neighbour.objects.get_or_create(
                                from_router=router, to_router=neighbor_router, local_intf=neighbor[1],
                                external_port_id=neighbor[4],
                                defaults={'hold_time': neighbor[2], 'capability': neighbor[3],
                                          'local_interface': local_interface, 'external_interface': external_interface}
                            )
                            print(neighbor_obj, created)
                        except Router.DoesNotExist:
                            # Ignore the neighbour other than project's 12 routers
                            pass
                break
            index += 1

    @staticmethod
    def add_interface_ports_info(router, data):
        for interface_data in data:
            if interface_data == '\n':
                return
            interface_data = interface_data.split()

            interface_name = interface_data[0]  # HundredGigE0/0/0/0

            interface_name_parts = interface_name.split('/')
            card_name = interface_name_parts[0][:-1]
            if card_name in Command.VALID_INTERFACES:
                slot_number = int(interface_name_parts[1])
                port_number_inside_card = int(interface_name_parts[-1])
                try:
                    card = Card.objects.get(
                        slot__router=router,
                        slot__slot_number=slot_number,
                        vertical_row_number=int(interface_name_parts[0][-1]),
                    )
                except Exception as exp:
                    return
                interface_port, created = InterfacePort.objects.get_or_create(
                    card=card,
                    name=interface_name,
                    defaults={
                        'port_number_inside_card': port_number_inside_card,
                        'ip_address': interface_data[1],
                        'status': interface_data[2],
                        'protocol': interface_data[3],
                    }
                )

    def handle(self, *args, **kwargs):
        routers_data_dir = os.path.abspath(os.path.join(__file__, '../../../../../routers_files'))
        router_files_names = [f for f in listdir(routers_data_dir) if isfile(join(routers_data_dir, f))]
        # Add the routers
        self.add_routers(router_files_names)

        for router_file_name in router_files_names:
            router_file = join(routers_data_dir, router_file_name)
            router_name = router_file_name.split('.')[0]
            router = Router.objects.get(name=router_name)

            print(router_name)

            with open(router_file) as fp:
                data = fp.readlines()
                data = data[4:]

                # Add cards from "show platform" command's data
                self.add_cards_info(router, data)

                # Add the interface ports info from "show ipv4 interface brief"
                self.add_interface_ports_info(router, data)

                # Add the neighbour data from "show lldp neighbor" command
                # self.add_neighbour(router, data)

        for router_file_name in router_files_names:
            router_file = join(routers_data_dir, router_file_name)
            router_name = router_file_name.split('.')[0]
            router = Router.objects.get(name=router_name)

            with open(router_file) as fp:
                data = fp.readlines()
                data = data[4:]

                # Add the neighbour data from "show lldp neighbor" command
                self.add_neighbour(router, data)
