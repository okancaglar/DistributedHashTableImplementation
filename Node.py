import hashlib
from exceptions.DHTExceptions import NodeException


class Node(object):

    def __init__(self, ip: str, port: int, identifier_space: int):

        self.ip = ip
        self.port = port
        self.identifier_space = identifier_space
        self.id = self.generate_id(ip, port)
        self.finger_table = [None] * identifier_space
        self.predecessor = self
        self.successor = self
        self.data = dict()

    def __str__(self):
        return f"Node({self.id})"

    def generate_id(self, ip: str, port: int) -> int:

        hash_obj = hashlib.sha1(f"{ip}:{port}".encode())
        return int(hash_obj.hexdigest(), 16) % (2 ** self.identifier_space)

    def join(self, connected_node) -> None:
        """

        :param connected_node:
        :return:
        """
        if connected_node:
            self.init_finger_table(connected_node)
            self.update_others()
        else:
            self.create_network()

    def create_network(self):

        for i in range(self.identifier_space):
            self.finger_table[i] = self
        self.predecessor = self



    def init_finger_table(self, node_prime) -> None:

        self.finger_table[0] = node_prime.find_successor(
            self.id + 2**0
        )
        if self.finger_table[0] is not None:
            self.predecessor = self.finger_table[0].predecessor
            self.finger_table[0].predecessor = self
        else:
            raise NodeException("logic error in init_finger_Tables")

        for i in range(0, self.identifier_space-1):
            start = self.id + 2**i
            if self.id <= start < self.finger_table[i].id:
                self.finger_table[i+1] = self.finger_table[i]
            else:
                self.finger_table[i+1] = node_prime.find_successor(self.id + 2**(i+1))

    def find_successor(self, index:int) -> 'Node':
        predecessor = self.find_predecessor(index)
        return predecessor.successor

    def find_predecessor(self, id_n: int) -> 'Node':

        node_prime = self
        while not (self.id <= id_n <= self.successor.id):
            node_prime = node_prime.find_closest_preceding_finger(id_n)
        return node_prime


    def find_closest_preceding_finger(self, id_n: int) :

        for i in range(self.identifier_space - 1, -1, -1):
            if self.id <= self.finger_table[i].id <= id_n:
                return self.finger_table[i]
        return self
    def update_others(self) -> None:

        for i in range(0, self.identifier_space):
            p = self.find_predecessor(self.id - 2**i)
            p.update_finger_tables(self, i)

    def update_finger_tables(self, node_update: 'Node', finger_table_index: int) -> None:

        if self.id < node_update.id < self.finger_table[finger_table_index].id:
            self.finger_table[finger_table_index] = node_update
            self.predecessor.update_finger_tables(node_update, finger_table_index)




def test() -> None:

    test_node = Node("192.168.1.23", 80, 3)
    test_node.join(None)
    print(test_node)
    test_node_2 = Node("192.168.32.243", 9090, 3)
    test_node_2.join(test_node)
    print(test_node_2)
    print(len(test_node_2.finger_table))
    for i in range(len(test_node_2.finger_table)):
        print(test_node_2.finger_table[i])


test()



