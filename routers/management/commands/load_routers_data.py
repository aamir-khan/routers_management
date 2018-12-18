import os
from os import listdir
from os.path import isfile, join

from django.core.management import BaseCommand

from routers.models import Router, Slot, Card, Port, Neighbour


class Command(BaseCommand):
    help = 'Loads the routers data'

    VALID_CARDS = ['0/0', '0/1', '0/2', '0/3', '0/4', '0/5', '0/6', '0/7']

    @staticmethod
    def add_routers(router_files_names):
        for router_files_name in router_files_names:
            router_name = router_files_name.split('.')[0]
            Router.objects.get_or_create(name=router_name)

    @staticmethod
    def add_slots(router):
        number = 0
        while number < 8:
            slot, created = Slot.objects.get_or_create(router=router, slot_number=number)
            number += 1

    @staticmethod
    def add_port_data(card, port_data):
        port_number_inside_slot = port_data[0][-1]
        port, created = Port.objects.get_or_create(card=card, port_number_inside_slot=port_number_inside_slot, defaults={
            'node_name': port_data[0], 'node_type': port_data[1], 'node_state': port_data[2],
            'admin_state': port_data[3]
        })

    @staticmethod
    def add_cards_info(router, router_data):
        index = 4
        while True:
            data = router_data[index]
            # The start of the data from show platform command
            if '---------------------------' in data:
                cards_port_data = router_data[index+1:]
                cards_port_data_index = 0
                while cards_port_data_index < len(cards_port_data):
                    data_ = cards_port_data[cards_port_data_index]
                    cards_port_data_index += 1
                    data_ = data_.split()
                    if not data_:
                        continue
                    if data_[0] in Command.VALID_CARDS:
                        slot_number = data_[0].split('/')[1]
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
                            name_with_dotted_extension = name.split('.')[0]
                            neighbor_router = Router.objects.get(name=name_with_dotted_extension)
                            # port = Port.objects.get()
                            neighbor_obj, created = Neighbour.objects.get_or_create(
                                from_router=router, to_router=neighbor_router, local_intf=neighbor[1],
                                external_port_id=neighbor[4],
                                defaults={'hold_time': neighbor[2], 'capability': neighbor[3]}
                            )
                            print(neighbor_obj, created)
                        except Router.DoesNotExist:
                            # Ignore the neighbour other than project's 12 routers
                            pass
                break
            index += 1
        pass

    def handle(self, *args, **kwargs):
        routers_data_dir = os.path.abspath(os.path.join(__file__, '../../../../../routers_files'))
        router_files_names = [f for f in listdir(routers_data_dir) if isfile(join(routers_data_dir, f))]
        # Add the routers
        self.add_routers(router_files_names)

        for router_file_name in router_files_names:
            router_file = join(routers_data_dir, router_file_name)
            router_name = router_file_name.split('.')[0]
            router = Router.objects.get(name=router_name)

            self.add_slots(router)

            print(router_name)

            with open(router_file) as fp:
                data = fp.readlines()
                data = data[4:]

                # Add cards from "show platform" command's data
                self.add_cards_info(router, data)

                # Add the neighbour data from "show lldp neighbor" command

                self.add_neighbour(router, data)
