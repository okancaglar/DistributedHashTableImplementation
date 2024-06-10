import hashlib


class Node(object):

    def __init__(self, ip_address: str, port_number: int, network_space: int):
        """

        :param ip_address: ip address of the node
        :param port_number: port number of the node
        :param network_space: parameter for chord ring that specifies the size of it. (2**network_space)
        """

        self.ip_address = ip_address
        self.port_number = port_number
        self.network_space = network_space
        self.finger_table = [None] * network_space
        self.data = {}
        self.id = self.generate_id()
        self.predecessor = None
        self.successor = None

    def __str__(self) -> str:
        return f"Node: {self.id}"

    def generate_id(self) -> int:
        """
        this function encrypts ip and port value and returns hexadecimal integer

        :return: int value of encrypted ip and port value
        """
        return (int(hashlib.sha1(f"{self.ip_address}:{self.port_number}".encode()).hexdigest(), 16)
                % 2 ** self.network_space)

    def join(self, connected_node: 'Node'):

        if connected_node is None:
            raise Exception("the node that trying to connect is None")

        """
        self.successor = connected_node.find_successor(self.id)
        if self.successor.predecessor is None:
            self.predecessor = self.successor
        else:
            self.predecessor = self.successor.predecessor
        self.successor.predecessor = self
        self.predecessor.successor = self
"""
        self.init_finger_table(connected_node)
        self.update_other_nodes()

    def create_network(self) -> None:
        """
        this function creates chord ring and initializes the network
        :return: None
        """

        self.successor = self
        self.predecessor = None

        for i in range(self.network_space):
            self.finger_table[i] = self

    def find_predecessor(self, node_id) -> 'Node':
        """

        :param node_id: the predecessor of the node id that wants to be found
        :return: predecessor node
        """
        p_node = self
        if p_node.predecessor is None:
            return self

        if p_node.id == node_id:
            return self.predecessor

        #if the prime node is between some node and its successor then this node is predecessor of prime node
        #interval check returns true and program get our of the loop
        while not p_node.interval_check(node_id, p_node.id, p_node.successor.id):
            p_node = p_node.find_closest_preceding_node(node_id)
        return p_node

    def interval_check(self, node_id: int, left_interval: int, right_interval: int) -> bool:
        """

        :param node_id: the node that wants to be checked if its in interval or not
        :param left_interval: lower limiting value
        :param right_interval: upper limiting value
        :return: boolean value which implies whether node is in interval or not
        """
        if left_interval == right_interval:
            return True
        if left_interval <= node_id < right_interval:
            return True
        elif left_interval > right_interval and (node_id >= left_interval or node_id < right_interval):
            return True
        return False

    def find_successor(self, node_id: int) -> 'Node':
        """
        :param node_id: the successor of the node id that wants to be found
        :return: successor node
        """

        #if the key is stand for a node then the node key is successor of itself
        if self.is_node(node_id):
            return self.get_node(node_id)
        #the successor of the predecessor node is successor of node_id
        p = self.find_predecessor(node_id)
        return p.successor

    def is_node(self, node_id: int) -> bool:
        """
        this function founds whether key_id is a node or not
        :param node_id: the key id
        :return: if it is a node returns true, if not returns false
        """

        for node in self.finger_table:
            if node.id == node_id:
                return True
        return False

    def get_node(self, node_id: int) -> 'Node':
        """
        this function gets node if there is with specified node_id
        :param node_id: the key id of the node that wants to be found
        :return: id there is a node returns the node, if there is not a node returns None
        """
        for node in self.finger_table:
            if node.id == node_id:
                return node

        return None

    def init_finger_table(self, prime_node: 'Node') -> None:
        """
        this function initializes the finger table of the node
        :param prime_node: base node while creating the finger table
        :return: None
        """
        self.finger_table[0] = prime_node.find_successor(self.id + 1)

        self.successor = prime_node.find_successor(self.id)
        if self.successor.predecessor is None:
            self.predecessor = self.successor
        else:
            self.predecessor = self.successor.predecessor
        self.successor.predecessor = self
        self.predecessor.successor = self

        for i in range(0, self.network_space-1):
            #this if else strucute is shortcut. if preceding key has a same successor or not
            if self.interval_check(self.id + 2**(i+1), self.id, self.finger_table[i].id):
                self.finger_table[i+1] = self.finger_table[i]
            else:
                self.finger_table[i+1] = prime_node.find_successor(self.id + 2**(i+1))


    def find_closest_preceding_node(self, node_id: int) -> 'Node':
        """
        this function finds preceding node of the given key_id
        :param node_id: key id
        :return: preceding node
        """
        for i in range(self.network_space - 1, -1, -1):
            if (self.id != self.finger_table[i].id and (self.interval_check(self.finger_table[i].id, self.id, node_id)) or
            self.finger_table[i].id == node_id):
                return self.finger_table[i]
        return self

    def update_finger_table(self, updated_node: 'Node', finger_index: int) -> None:
        """
        this function updates finger table
        :param updated_node: new successor node
        :param finger_index: which key is going to be updated
        :return: None
        """
        if self.id != updated_node.id and self.interval_check(updated_node.id, self.id, self.finger_table[finger_index].id) or (
                self.id == self.finger_table[finger_index].id):
            self.finger_table[finger_index] = updated_node
            p = self.predecessor
            p.update_finger_table(updated_node, finger_index)

    def update_other_nodes(self) -> None:
        """
        this function updates all od the nodes finger table
        :return: None
        """
        for i in range(0, self.network_space):
            p = self.find_predecessor(self.id - (2 ** i) + 2 ** self.network_space % 2 ** self.network_space)
            if p.id != self.id:
                p.update_finger_table(self, i)


def test() -> None:

    test_node = Node("192.168.1.23", 80, 3)
    test_node.create()
    print(test_node)
    test_node_2 = Node("192.168.32.243", 9090, 3)
    test_node_2.join(test_node)
    print(test_node_2)
    test_node_3 = Node("143.200.40.2", 3000, 3)
    test_node_3.join(test_node)
    test_node_4 = Node("254.243.156.200", 6599, 3)
    test_node_4.join(test_node)
    print("Node1")
    print(len(test_node.finger_table))
    for i in range(len(test_node.finger_table)):
        print(test_node.finger_table[i])

    print("Node2")
    print(len(test_node_2.finger_table))
    for i in range(len(test_node_2.finger_table)):
        print(test_node_2.finger_table[i])
    print("Node3")
    print(len(test_node_3.finger_table))
    for i in range(len(test_node_3.finger_table)):
        print(test_node_3.finger_table[i])

    print("Node4")
    print(len(test_node_4.finger_table))
    for i in range(len(test_node_4.finger_table)):
        print(test_node_4.finger_table[i])






test()
