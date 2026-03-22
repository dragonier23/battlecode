from data_structures.mutable_heap import MutableHeap

class PriorityQueue:
    def __init__(self):
        self._heap = MutableHeap()
        self._payload_map = {}  # item -> key
    
    def top(self):
        return self._heap.top()
    
    def top_key(self):
        return self._heap.top()[0]
    
    def pop(self):
        key, item = self._heap.pop()
        del self._payload_map[item]
        return key, item

    def insert(self, key, item):
        self._heap.push((key, item))
        self._payload_map[item] = key

    def update(self, item, new_key):
        self._heap.remove((self._payload_map[item], item))
        self._heap.push((new_key, item))
        self._payload_map[item] = new_key

    def remove(self, item):
        self._heap.remove((self._payload_map[item], item))
        del self._payload_map[item]

    def is_member(self, item):
        return item in self._payload_map
    
    def __bool__(self):
        return bool(self._heap._heap)
    
if __name__ == "__main__":
    pq = PriorityQueue()
    pq.insert(5, "a")
    pq.insert(3, "b")
    pq.insert(4, "c")
    print(pq.top()) # should be (3, "b")
    pq.update("a", 2)
    print(pq.top()) # should be (2, "a")
    pq.remove("a")
    print(pq.top()) # should be (3, "b")