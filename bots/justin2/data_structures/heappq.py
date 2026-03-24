from heapq import heappush, heappop

from cambc import Position

REMOVED = Position(-1, -1)

class HeapPQ:
    def __init__(self):
        self._heap = []
        self._payload_map = {}

    def top(self):
        while self._heap and self._heap[0][1] is REMOVED:
            heappop(self._heap) # cleanup
        return self._heap[0]
    
    def top_key(self):
        while self._heap and self._heap[0][1] is REMOVED:
            heappop(self._heap)
        return self._heap[0][0]
    
    def pop(self):
        while self._heap:
            key, item = heappop(self._heap)
            if item is not REMOVED:
                del self._payload_map[item]
                return key, item

    def insert(self, key, item):
        entry = [key, item]
        self._payload_map[item] = entry
        heappush(self._heap, entry)

    def remove(self, item):
        entry = self._payload_map.pop(item)
        entry[1] = REMOVED  # Mark as removed

    def is_member(self, item):
        return item in self._payload_map

if __name__ == "__main__":
    pq = HeapPQ()
    pq.insert(5, "a")
    pq.insert(3, "b")
    pq.insert(4, "c")
    print(pq.top()) # should be (3, "b")
    pq.insert(2, "a")
    print(pq.top()) # should be (2, "a")
    pq.remove("a")
    print(pq.top()) # should be (3, "b")