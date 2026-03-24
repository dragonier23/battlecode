class PriorityQueue:
    def __init__(self):
        self._heap = []
        self._item_map = {}  # item -> index
    
    def top(self):
        return self._heap[0]
    
    def top_key(self):
        return self._heap[0][0]
    
    def pop(self):
        key, item = self._heap[0]
        del self._item_map[item]
        self._remove_at_index(0)
        return key, item

    def insert(self, key, item):
        self._heap.append((key, item))
        self._item_map[item] = len(self._heap) - 1
        self._sift_up(self._item_map[item])

    def update(self, item, new_key):
        idx = self._item_map[item]
        old_key, _ = self._heap[idx]
        self._heap[idx] = (new_key, item)
        if new_key < old_key:
            self._sift_up(idx)
        else:
            self._sift_down(idx)

    def remove(self, item):
        self._remove_at_index(self._item_map.pop(item))

    def _sift_up(self, idx):
        while idx > 0:
            parent = (idx - 1) // 2
            if self._heap[idx][0] >= self._heap[parent][0]:
                break
            self._heap[idx], self._heap[parent] = self._heap[parent], self._heap[idx]
            self._item_map[self._heap[idx][1]] = idx
            self._item_map[self._heap[parent][1]] = parent
            idx = parent

    def _sift_down(self, idx):
        n = len(self._heap)
        while True:
            smallest = idx
            left = 2 * idx + 1
            right = 2 * idx + 2
            if left < n and self._heap[left][0] < self._heap[smallest][0]:
                smallest = left
            if right < n and self._heap[right][0] < self._heap[smallest][0]:
                smallest = right
            if smallest == idx:
                break
            self._heap[idx], self._heap[smallest] = self._heap[smallest], self._heap[idx]
            self._item_map[self._heap[idx][1]] = idx
            self._item_map[self._heap[smallest][1]] = smallest
            idx = smallest

    def _remove_at_index(self, idx):
        # Swap with last, then pop
        last = self._heap[-1]
        self._heap[idx] = last
        self._heap.pop() # remove last element
        if idx < len(self._heap):
            self._item_map[last[1]] = idx
            if idx > 0 and self._heap[idx][0] < self._heap[(idx - 1) // 2][0]: # key smaller than parent
                self._sift_up(idx)
            else:
                self._sift_down(idx)

    def is_member(self, item):
        return item in self._item_map
    
    def __bool__(self):
        return bool(self._heap)
    
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