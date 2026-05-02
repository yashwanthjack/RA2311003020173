import heapq
from datetime import datetime

# Define weights for each type
WEIGHTS = {
    "Placement": 3,
    "Result": 2,
    "Event": 1
}

class PriorityInbox:
    def __init__(self, max_size=10):
        self.max_size = max_size
        self.min_heap = []
        
    def add_notification(self, notification):
        """
        Maintains the top 10 notifications efficiently using a Min-Heap.
        Time Complexity: O(log K) where K is max_size (10)
        """
        n_type = notification.get("Type", "Event")
        weight = WEIGHTS.get(n_type, 0)
        
        # Convert timestamp string to datetime object for correct comparison
        # Example timestamp: "2026-04-22 17:51:30"
        try:
            time_obj = datetime.strptime(notification["Timestamp"], "%Y-%m-%d %H:%M:%S")
        except ValueError:
            time_obj = datetime.min
            
        # Tuple format: (weight, time_obj, unique_id, raw_notification)
        # We include ID to break ties if weight and time are identical
        heap_item = (weight, time_obj, notification.get("ID", ""), notification)
        
        if len(self.min_heap) < self.max_size:
            heapq.heappush(self.min_heap, heap_item)
        else:
            # If the new item is larger than the smallest item in the heap, push it and pop the smallest
            heapq.heappushpop(self.min_heap, heap_item)
            
    def get_top_notifications(self):
        """Returns the notifications sorted from highest priority to lowest"""
        # The heap elements are ascending (min-heap). We sort descending to get highest first.
        sorted_items = sorted(self.min_heap, key=lambda x: (x[0], x[1]), reverse=True)
        return [item[3] for item in sorted_items]

