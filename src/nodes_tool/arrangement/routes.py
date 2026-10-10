"""Create horizontal wire channels directly from the placed node bounds."""

from collections import defaultdict
from statistics import median


def _channel_height(preferred, intervals):
    candidates = [preferred]
    for top, bottom in intervals:
        candidates.extend((top - 1, bottom + 1))
    clear = [level for level in candidates
             if not any(top <= level <= bottom for top, bottom in intervals)]
    return min(clear, key=lambda level: (abs(level - preferred), level))


def _intersects(start, end, box):
    low, high = 0.0, 1.0
    for axis in (0, 1):
        delta = end[axis] - start[axis]
        minimum, maximum = box[axis], box[axis + 2]
        if abs(delta) < 1e-9:
            if not minimum <= start[axis] <= maximum:
                return False
            continue
        first, last = sorted(((minimum - start[axis]) / delta, (maximum - start[axis]) / delta))
        low, high = max(low, first), min(high, last)
        if low > high:
            return False
    return True


def plan_routes(endpoints, edge_nodes, ranks, columns, widths, boxes, sources, preferred):
    """Use one level per source channel, with two anchors on every long wire."""
    routes = {}
    channels = defaultdict(list)
    for edge, (a, b) in enumerate(edge_nodes):
        start, end = endpoints[edge]
        if ranks[b] > ranks[a] + 1:
            channels[sources[edge]].append(edge)
            continue
        routes[edge] = [start, end]
        if start[0] < columns[ranks[a]] + widths[ranks[a]]:
            routes[edge].insert(1, (columns[ranks[a]] + widths[ranks[a]] + 60, start[1]))

    occupied = []
    for edges in channels.values():
        a = edge_nodes[edges[0]][0]
        left = columns[ranks[a]] + widths[ranks[a]] + 60
        right = max(columns[ranks[edge_nodes[e][1]]] - 60 for e in edges)
        levels = [preferred.get(e, sum(point[1] for point in endpoints[e]) / 2) for e in edges]
        intervals = [(top - 24, bottom + 24) for x, top, end_x, bottom in boxes.values()
                     if x - 16 < right and end_x + 16 > left]
        intervals.extend((level - 24, level + 24) for x, end_x, level in occupied
                         if x < right and end_x > left)
        level = _channel_height(median(levels), intervals)
        occupied.append((left, right, level))
        for edge in edges:
            a, b = edge_nodes[edge]
            start, end = endpoints[edge]
            entry = columns[ranks[b]] - 60
            first, last = (left, level), (entry, level)
            path = [start]
            # Port leads are needed only when the bend would cross another node.
            if any(_intersects(start, first, box) for i, box in boxes.items() if i != a):
                path.append((left, start[1]))
            path.extend((first, last))
            if any(_intersects(last, end, box) for i, box in boxes.items() if i != b):
                path.append((entry, end[1]))
            path.append(end)
            routes[edge] = path
    return routes
