class MutableHeap:
    def __init__(self):
        self._heap = []
        self._index_map = {}  # item -> index

    def push(self, item):
        if item in self._index_map:
            raise ValueError("item already in heap")
        idx = len(self._heap)
        self._heap.append(item)
        self._index_map[item] = idx
        self._sift_up(idx)

    def top(self):
        if not self._heap:
            raise IndexError("top from empty heap")
        return self._heap[0]

    def pop(self):
        if not self._heap:
            raise IndexError("pop from empty heap")
        item = self._heap[0]
        self._index_map.pop(item)
        self._remove_at_index(0)
        return item

    def remove(self, item):
        idx = self._index_map.pop(item)
        self._remove_at_index(idx)

    def _remove_at_index(self, idx):
        # Swap with last, then pop
        last = self._heap[-1]
        self._heap[idx] = last
        self._heap.pop() # remove last element
        if idx < len(self._heap):
            self._index_map[last] = idx
            if idx > 0 and self._heap[idx] < self._heap[(idx - 1) // 2]:
                self._sift_up(idx)
            else:
                self._sift_down(idx)

    def _sift_up(self, idx):
        while idx > 0:
            parent = (idx - 1) // 2
            if self._heap[idx] >= self._heap[parent]:
                break
            self._heap[idx], self._heap[parent] = self._heap[parent], self._heap[idx]
            self._index_map[self._heap[idx]] = idx
            self._index_map[self._heap[parent]] = parent
            idx = parent

    def _sift_down(self, idx):
        n = len(self._heap)
        while True:
            smallest = idx
            left = 2 * idx + 1
            right = 2 * idx + 2
            if left < n and self._heap[left] < self._heap[smallest]:
                smallest = left
            if right < n and self._heap[right] < self._heap[smallest]:
                smallest = right
            if smallest == idx:
                break
            self._heap[idx], self._heap[smallest] = self._heap[smallest], self._heap[idx]
            self._index_map[self._heap[idx]] = idx
            self._index_map[self._heap[smallest]] = smallest
            idx = smallest

    def __len__(self):
        return len(self._heap)

    def __contains__(self, item):
        return item in self._index_map
    
if __name__ == "__main__":
    h = MutableHeap()
    h.push(5)
    h.push(3)
    h.push(8)
    print(h.pop())  # 3
    h.push(1)
    print(h.pop())  # 1
    h.remove(5)
    print(h.pop())  # 8