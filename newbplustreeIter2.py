from __future__ import annotations
from math import ceil, floor
from datetime import datetime
import time
import csv

"""
Developed by:
 - Vasilis Dimitriadis - WckdAwe ( http://github.com/WckdAwe )
 - Taxiarchis Kouskouras - TheNotoriousCS ( https://github.com/TheNotoriousCS )
The following algorithms have been developed based on:
 - https://en.wikipedia.org/wiki/B%2B_tree
 - https://www.javatpoint.com/b-plus-tree
 - https://web.stanford.edu/class/cs346/2015/notes/Blink.pptx

Influenced a lot by:
 - https://gist.github.com/savarin/69acd246302567395f65ad6b97ee503d
 - https://github.com/pschafhalter/python-b-plus-tree
 - http://www.cburch.com/cs/340/reading/btree/
"""
"""
Additions made for CS4525 Final Project
"""


class Node:
    uid_counter = 0
    """
    Base node object.

    Attributes:
        order (int): The maximum number of keys each node can hold. (aka branching factor)
        is_leaf (bool): Indicates if the node is a leaf.
        parent (Node): The parent of the current node.
        keys (list): List of keys held by this node.
        values (list): List of values or child nodes associated with the keys.
        uid (int): Unique identifier for each node, useful for debugging.
    """

    def __init__(self, order, is_leaf=False):
        self.is_leaf = is_leaf  # Indicates whether the node is a leaf node.
        self.order = order  # The maximum number of keys a node can hold.
        self.parent: Node = None  # Reference to the parent node.
        self.keys = []  # List of keys stored in the node.
        self.values = []  # List of values or children associated with the keys.

        # This is for Debugging purposes only - assigns a unique ID to each node.
        Node.uid_counter += 1
        self.uid = self.uid_counter

    def split(self) -> Node:  # Split a full Node into two new ones.
        # Create two new nodes that will hold the split keys and values.
        left = Node(self.order, is_leaf=self.is_leaf)
        right = Node(self.order, is_leaf=self.is_leaf)
        mid = int(self.order // 2)  # Determine the midpoint for the split.

        # Set the new nodes' parent to the current node (this node becomes the top node).
        left.parent = right.parent = self

        # Distribute keys and values between the left and right nodes.
        left.keys = self.keys[:mid]
        left.values = self.values[:mid + 1]

        right.keys = self.keys[mid + 1:]
        right.values = self.values[mid + 1:]

        # Set the current node's values to reference the new left and right nodes.
        self.values = [left, right]

        # The current node keeps only the middle key, which will be used for splitting.
        self.keys = [self.keys[mid]]

        # Update the parent reference for each child in the left and right nodes.
        for child in left.values:
            if isinstance(child, Node):
                child.parent = left

        for child in right.values:
            if isinstance(child, Node):
                child.parent = right

        return self  # Return the 'top node'

    def get_size(self) -> int:
        return len(self.keys)  # Returns the number of keys in the node.

    def is_empty(self) -> bool:
        return len(self.keys) == 0  # Check if the node has no keys.

    def is_full(self) -> bool:
        return len(self.keys) == self.order - 1  # Check if the node is full.

    def is_nearly_underflowed(self) -> bool:  # Check if the node is nearly underflowed.
        return len(self.keys) <= floor(self.order / 2)

    def is_underflowed(self) -> bool:  # Check if the node is underflowed.
        return len(self.keys) <= floor(self.order / 2) - 1

    def is_root(self) -> bool:
        return self.parent is None  # Check if the node is the root.


class LeafNode(Node):
    """
    Leaf node class, derived from Node.

    Attributes:
        prev_leaf (LeafNode): Pointer to the previous leaf node.
        next_leaf (LeafNode): Pointer to the next leaf node.
    """

    def __init__(self, order):
        super().__init__(order, is_leaf=True)  # Initialize the base node as a leaf.

        self.prev_leaf: LeafNode = None  # Pointer to the previous leaf node.
        self.next_leaf: LeafNode = None  # Pointer to the next leaf node.

    def add(self, key, value):  # Add key and value to the leaf node.
        if not self.keys:  # If no keys exist, add the key and value.
            self.keys.append(key)
            self.values.append([value])
            return

        # Insert the key in the correct position to maintain sorted order.
        for i, item in enumerate(self.keys):
            if key == item:  # Key already exists, append the value.
                self.values[i].append(value)
                break

            elif key < item:  # Key should be inserted before the current item.
                self.keys = self.keys[:i] + [key] + self.keys[i:]
                self.values = self.values[:i] + [[value]] + self.values[i:]
                break

            elif i + 1 == len(self.keys):  # Key should be appended at the end.
                self.keys.append(key)
                self.values.append([value])
                break

    def split(self) -> Node:  # Split a full leaf node.
        top = Node(self.order)  # Create a new top node to hold split nodes.
        right = LeafNode(self.order)  # Create the new right leaf node.
        mid = int(self.order // 2)  # Determine the midpoint for the split.

        # Set the new nodes' parent to the top node.
        self.parent = right.parent = top

        # Distribute keys and values between the current (left) and right nodes.
        right.keys = self.keys[mid:]
        right.values = self.values[mid:]
        right.prev_leaf = self  # Set the right node's previous leaf to the current node.
        right.next_leaf = self.next_leaf  # Set the right node's next leaf.

        if self.next_leaf:
            self.next_leaf.prev_leaf = right  # Update the next leaf's previous pointer.

        # Set the current node's next leaf to the right node.
        self.next_leaf = right

        # Set the top node's keys and values to reference the split nodes.
        top.keys = [right.keys[0]]
        top.values = [self, right]

        # Update the current node's keys and values to reflect the split.
        self.keys = self.keys[:mid]
        self.values = self.values[:mid]

        return top  # Return the 'top node'


class BPlusTree(object):
    def __init__(self, order=5):
        self.root: LeafNode = LeafNode(order)  # Initialize the root as a leaf node.
        self.order: int = order  # Set the order of the B+ Tree.

    @staticmethod
    def _find(node: Node, key):
        """
        Find the child node that should contain the given key.

        Args:
            node (Node): The current node to search within.
            key: The key to find.

        Returns:
            Tuple of (child node, index) where the key should be located.
        """
        for i, item in enumerate(node.keys):
            if key < item:
                return node.values[i], i
            elif i + 1 == len(node.keys):
                return node.values[i + 1], i + 1  # Return right-most child.

    @staticmethod
    def _merge_up(parent: Node, child: Node, index):
        """
        Merge a child node into its parent after a split.

        Args:
            parent (Node): The parent node.
            child (Node): The newly split child node.
            index (int): The index in the parent to insert the child.
        """
        parent.values.pop(index)  # Remove the old reference to the split child.
        pivot = child.keys[0]  # Use the first key of the split child as the pivot.

        # Update the parent reference for all children of the split node.
        for c in child.values:
            if isinstance(c, Node):
                c.parent = parent

        # Insert the pivot key and split child values into the parent node.
        for i, item in enumerate(parent.keys):
            if pivot < item:
                parent.keys = parent.keys[:i] + [pivot] + parent.keys[i:]
                parent.values = parent.values[:i] + child.values + parent.values[i:]
                break

            elif i + 1 == len(parent.keys):
                parent.keys += [pivot]
                parent.values += child.values
                break

    def insert(self, key, value):
        """
        Insert a key-value pair into the B+ Tree.

        Args:
            key: The key to insert.
            value: The value associated with the key.
        """
        node = self.root

        # Traverse down to find the correct leaf node.
        while not isinstance(node, LeafNode):
            node, index = self._find(node, key)

        # Add the key-value pair to the leaf node.
        node.add(key, value)

        # Handle splitting if the node is overfull.
        while len(node.keys) == node.order:  # Node is overfull.
            if not node.is_root():
                parent = node.parent
                node = node.split()  # Split the node.
                _, index = self._find(parent, node.keys[0])
                self._merge_up(parent, node, index)
                node = parent
            else:
                node = node.split()  # Split and set the new root.
                self.root = node

    def retrieve(self, key):
        """
        Retrieve the value associated with the given key.

        Args:
            key: The key to search for.

        Returns:
            The value associated with the key, or None if not found.
        """
        node = self.root

        # Traverse down to the correct leaf node.
        while not isinstance(node, LeafNode):
            node, index = self._find(node, key)

        # Search for the key in the leaf node.
        for i, item in enumerate(node.keys):
            if key == item:
                return node.values[i]

        return None  # Key not found.

    def delete(self, key):
        """
        Delete a key-value pair from the B+ Tree.

        Args:
            key: The key to delete.

        Returns:
            True if the key was successfully deleted, False otherwise.
        """
        node = self.root

        # Traverse down to the correct leaf node.
        while not isinstance(node, LeafNode):
            node, parent_index = self._find(node, key)

        # If the key is not found in the leaf node, return False.
        if key not in node.keys:
            return False

        # Remove the value associated with the key.
        index = node.keys.index(key)
        node.values[index].pop()  # Remove the last inserted data.

        # If the list of values is empty, remove the key and value entirely.
        if len(node.values[index]) == 0:
            node.values.pop(index)
            node.keys.pop(index)

            # Handle underflow if necessary.
            while node.is_underflowed() and not node.is_root():
                # Attempt to borrow from siblings or merge nodes.
                prev_sibling = BPlusTree.get_prev_sibling(node)
                next_sibling = BPlusTree.get_next_sibling(node)
                _, parent_index = self._find(node.parent, key)

                if prev_sibling and not prev_sibling.is_nearly_underflowed():
                    self._borrow_left(node, prev_sibling, parent_index)
                elif next_sibling and not next_sibling.is_nearly_underflowed():
                    self._borrow_right(node, next_sibling, parent_index)
                elif prev_sibling and prev_sibling.is_nearly_underflowed():
                    self._merge_on_delete(prev_sibling, node)
                elif next_sibling and next_sibling.is_nearly_underflowed():
                    self._merge_on_delete(node, next_sibling)

                node = node.parent

            # Update the root if necessary.
            if node.is_root() and not isinstance(node, LeafNode) and len(node.values) == 1:
                self.root = node.values[0]
                self.root.parent = None

        return True

    @staticmethod
    def _borrow_left(node: Node, sibling: Node, parent_index):
        """
        Borrow a key from the left sibling.

        Args:
            node (Node): The node that is underflowed.
            sibling (Node): The left sibling to borrow from.
            parent_index (int): The index in the parent node.
        """
        if isinstance(node, LeafNode):  # Leaf Redistribution
            key = sibling.keys.pop(-1)
            data = sibling.values.pop(-1)
            node.keys.insert(0, key)
            node.values.insert(0, data)

            # Update the parent key.
            node.parent.keys[parent_index - 1] = key
        else:  # Inner Node Redistribution (Push-Through)
            parent_key = node.parent.keys.pop(-1)
            sibling_key = sibling.keys.pop(-1)
            data: Node = sibling.values.pop(-1)
            data.parent = node

            node.parent.keys.insert(0, sibling_key)
            node.keys.insert(0, parent_key)
            node.values.insert(0, data)

    @staticmethod
    def _borrow_right(node: LeafNode, sibling: LeafNode, parent_index):
        """
        Borrow a key from the right sibling.

        Args:
            node (LeafNode): The node that is underflowed.
            sibling (LeafNode): The right sibling to borrow from.
            parent_index (int): The index in the parent node.
        """
        if isinstance(node, LeafNode):  # Leaf Redistribution
            key = sibling.keys.pop(0)
            data = sibling.values.pop(0)
            node.keys.append(key)
            node.values.append(data)

            # Update the parent key.
            node.parent.keys[parent_index] = sibling.keys[0]
        else:  # Inner Node Redistribution (Push-Through)
            parent_key = node.parent.keys.pop(0)
            sibling_key = sibling.keys.pop(0)
            data: Node = sibling.values.pop(0)
            data.parent = node

            node.parent.keys.append(sibling_key)
            node.keys.append(parent_key)
            node.values.append(data)

    @staticmethod
    def _merge_on_delete(l_node: Node, r_node: Node):
        """
        Merge two nodes after a deletion causes underflow.

        Args:
            l_node (Node): The left node to merge.
            r_node (Node): The right node to merge.
        """
        parent = l_node.parent

        # Find the index of the left node in the parent.
        _, index = BPlusTree._find(parent, l_node.keys[0])
        parent_key = parent.keys.pop(index)
        parent.values.pop(index)
        parent.values[index] = l_node

        if isinstance(l_node, LeafNode) and isinstance(r_node, LeafNode):
            l_node.next_leaf = r_node.next_leaf  # Update the next leaf pointer.
        else:
            l_node.keys.append(parent_key)  # Add the parent's key to the merged node.
            for r_node_child in r_node.values:
                r_node_child.parent = l_node

        # Combine keys and values of both nodes.
        l_node.keys += r_node.keys
        l_node.values += r_node.values

    @staticmethod
    def get_prev_sibling(node: Node) -> Node:
        """
        Get the previous sibling of a given node.

        Args:
            node (Node): The node whose previous sibling is to be found.

        Returns:
            The previous sibling node, or None if no sibling exists.
        """
        if node.is_root() or not node.keys:
            return None
        _, index = BPlusTree._find(node.parent, node.keys[0])
        return node.parent.values[index - 1] if index - 1 >= 0 else None

    @staticmethod
    def get_next_sibling(node: Node) -> Node:
        """
        Get the next sibling of a given node.

        Args:
            node (Node): The node whose next sibling is to be found.

        Returns:
            The next sibling node, or None if no sibling exists.
        """
        if node.is_root() or not node.keys:
            return None
        _, index = BPlusTree._find(node.parent, node.keys[0])

        return node.parent.values[index + 1] if index + 1 < len(node.parent.values) else None

    def show_bfs(self):
        """
        Display the B+ Tree level by level (Breadth-First Search).
        """
        if self.root.is_empty():
            print('The B+ Tree is empty!')
            return
        queue = [self.root, 0]  # Node, Height... Scrappy but it works

        while len(queue) > 0:
            node = queue.pop(0)
            height = queue.pop(0)

            if not isinstance(node, LeafNode):
                queue += self.intersperse(node.values, height + 1)
            print(height, '|'.join(map(str, node.keys)), '	', node.uid, '	 parent -> ',
                  node.parent.uid if node.parent else None)

    def get_leftmost_leaf(self):
        """
        Get the leftmost leaf node of the B+ Tree.

        Returns:
            The leftmost leaf node.
        """
        if not self.root:
            return None

        node = self.root
        while not isinstance(node, LeafNode):
            node = node.values[0]

        return node

    def get_rightmost_leaf(self):
        """
        Get the rightmost leaf node of the B+ Tree.

        Returns:
            The rightmost leaf node.
        """
        if not self.root:
            return None

        node = self.root
        while not isinstance(node, LeafNode):
            node = node.values[-1]

        return node

    def show_all_data(self):
        """
        Display all the data in the B+ Tree from leftmost to rightmost leaf.
        """
        node = self.get_leftmost_leaf()
        if not node:
            return None

        while node:
            for node_data in node.values:
                print('[{}]'.format(', '.join(map(str, node_data))), end=' -> ')

            node = node.next_leaf
        print('Last node')

    def show_all_data_reverse(self):
        """
        Display all the data in the B+ Tree from rightmost to leftmost leaf.

        This method starts from the rightmost leaf node and traverses the linked list of leaf nodes
        in reverse order, displaying each key-value pair.
        """
        node = self.get_rightmost_leaf()
        if not node:
            return None  # If the tree is empty, there is nothing to display.

        while node:
            # Iterate through the values in the current leaf node in reverse order.
            for node_data in reversed(node.values):
                print('[{}]'.format(', '.join(map(str, node_data))), end=' <- ')

            # Move to the previous leaf node in the linked list.
            node = node.prev_leaf
        print()  # Print a new line at the end.

    @staticmethod
    def intersperse(lst, item):
        """
        Intersperse an item between all elements of a list.

        Args:
            lst (list): The list of elements.
            item: The item to intersperse.

        Returns:
            A new list with the item interspersed between each element of the original list.
        """
        result = [item] * (len(lst) * 2)
        result[0::2] = lst
        return result

    def find_leaf(self, key):
        """
        Find the leaf node that should contain the given key.

        Args:
            key: The key to locate in the B+ Tree.

        Returns:
            The leaf node that either contains the key or where the key should be inserted.
        """
        # Start from the root of the B+ Tree.
        node = self.root

        # Traverse down the tree until a leaf node is reached.
        while not node.is_leaf:
            for i, item in enumerate(node.keys):
                # If the key is less than the current item, follow the corresponding child pointer.
                if key < item:
                    node = node.values[i]  # Go down the appropriate child node.
                    break
                # If we are at the last key and the key is greater, move to the right-most child.
                elif i + 1 == len(node.keys):
                    node = node.values[i + 1]
                    break

        # Return the leaf node that contains or should contain the key.
        return node

    def range_query(self, start_key, end_key, inclusive=True):
        """
        Perform a range query to find all keys within the specified range.

        Args:
            start_key: The start key of the range.
            end_key: The end key of the range.
            inclusive (bool): Whether to include the end key in the results.

        Returns:
            A list of values that fall within the specified key range.
        """
        results = []
        node = self.find_leaf(start_key)  # Start at the leaf node containing the start key.

        # Traverse the leaf nodes to collect all keys within the range.
        while node:
            for i, key in enumerate(node.keys):
                if start_key <= key <= end_key:
                    if key == end_key and not inclusive:
                        continue
                    results.extend(node.values[i])

                if key > end_key:
                    break

            # If the last key in the current node exceeds the end key, stop the traversal.
            if node.keys and node.keys[-1] > end_key:
                break
            node = node.next_leaf  # Move to the next leaf node.

        return results

    def range_sum(self, start_key, end_key, inclusive=True):
        """
        Calculate the sum of values within the specified key range.

        Args:
            start_key: The start key of the range.
            end_key: The end key of the range.
            inclusive (bool): Whether to include the end key in the results.

        Returns:
            The sum of values within the specified key range.
        """
        total = 0
        node = self.find_leaf(start_key)

        while node:
            for i, key in enumerate(node.keys):
                if start_key <= key <= end_key:
                    if key == end_key and not inclusive:
                        continue
                    total += sum(node.values[i])

                if key > end_key:
                    break

            if node.keys and node.keys[-1] > end_key:
                break
            node = node.next_leaf

        return total

    def range_avg(self, start_key, end_key, inclusive=True):
        """
        Calculate the average of values within the specified key range.

        Args:
            start_key: The start key of the range.
            end_key: The end key of the range.
            inclusive (bool): Whether to include the end key in the results.

        Returns:
            The average of values within the specified key range.
        """
        total = 0
        count = 0
        node = self.find_leaf(start_key)

        while node:
            for i, key in enumerate(node.keys):
                if start_key <= key <= end_key:
                    if key == end_key and not inclusive:
                        continue
                    total += sum(node.values[i])
                    count += len(node.values[i])

                if key > end_key:
                    break

            if node.keys and node.keys[-1] > end_key:
                break
            node = node.next_leaf

        return total / count if count > 0 else 0

    def range_min(self, start_key, end_key, inclusive=True):
        """
        Find the minimum value within the specified key range.

        Args:
            start_key: The start key of the range.
            end_key: The end key of the range.
            inclusive (bool): Whether to include the end key in the results.

        Returns:
            The minimum value within the specified key range.
        """
        min_value = None
        node = self.find_leaf(start_key)

        while node:
            for i, key in enumerate(node.keys):
                if start_key <= key <= end_key:
                    if key == end_key and not inclusive:
                        continue
                    current_min = min(node.values[i])
                    if min_value is None or current_min < min_value:
                        min_value = current_min

                if key > end_key:
                    break

            if node.keys and node.keys[-1] > end_key:
                break
            node = node.next_leaf

        return min_value

    def range_max(self, start_key, end_key, inclusive=True):
        """
        Find the maximum value within the specified key range.

        Args:
            start_key: The start key of the range.
            end_key: The end key of the range.
            inclusive (bool): Whether to include the end key in the results.

        Returns:
            The maximum value within the specified key range.
        """
        max_value = None
        node = self.find_leaf(start_key)

        while node:
            for i, key in enumerate(node.keys):
                if start_key <= key <= end_key:
                    if key == end_key and not inclusive:
                        continue
                    current_max = max(node.values[i])
                    if max_value is None or current_max > max_value:
                        max_value = current_max

                if key > end_key:
                    break

            if node.keys and node.keys[-1] > end_key:
                break
            node = node.next_leaf

        return max_value



# if __name__ == '__main__':
#     bplustree = BPlusTree(order=100)
#
#     csv_file = "dummy_data.csv"  # Ensure this file exists and matches your schema
#
#     with open(csv_file, mode="r") as file:
#         reader = csv.DictReader(file)
#         start_time = time.time()  # Start timing
#         for row in reader:
#             time_key = datetime.fromisoformat(row["timestamp"])
#             temperature = float(row["value"])
#             bplustree.insert(time_key, temperature)
#         end_time = time.time()  # End timing
#
#     print(f"\nB+: Added 100 000 entries in {end_time - start_time} seconds.\n")
#
#     # start = datetime(2024, 1, 1, 0, 0, 0)
#     # end = datetime(2025, 1, 1, 0, 15, 0)
#
#     start = "2026-01-01T00:00:00"
#     end = "2027-01-01T00:15:00"
#     test1 = datetime.fromisoformat(start)
#     test2 = datetime.fromisoformat(end)
#
#     s4 = time.perf_counter()
#     range_results2 = bplustree.range_query(test1, test2)
#     e4 = time.perf_counter()
#     print(f"B+: Found {len(range_results2)} entries from [{test1}] to [{test2}] in {e4 - s4:.6f} seconds. \n")
#
#     test = datetime(2024, 1, 1, 00, 49, 42)
#
#     s5 = time.perf_counter()
#     results3 = bplustree.retrieve(test)
#     e5 = time.perf_counter()
#     print(f"B+: Found value: {results3} for timestamp: [{test}] in {e5 - s5} seconds")



