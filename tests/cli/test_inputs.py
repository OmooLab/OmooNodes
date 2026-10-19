from omoonodes.arrangement.arrange import _input_regions
from omoonodes.arrangement.dimensions import NodeDimensions


def test_input_reads_share_a_compact_region_but_not_other_columns_or_distant_rows():
    positions = {0: (400, 0), 1: (400, 164), 2: (400, 700), 3: (800, 0)}
    sizes = {i: NodeDimensions(180, 100, {}) for i in positions}
    assert _input_regions(set(positions), positions, sizes) == [[0, 1], [2], [3]]


def test_adjacent_consumers_do_not_chain_into_an_unbounded_input_region():
    positions = {i: (400, i * 164) for i in range(4)}
    sizes = {i: NodeDimensions(180, 100, {}) for i in positions}
    assert _input_regions(set(positions), positions, sizes) == [[0, 1], [2, 3]]
    assert _input_regions(set(), positions, sizes) == []


def test_a_tall_consumer_keeps_its_own_read():
    positions = {0: (400, 0), 1: (400, 564)}
    sizes = {0: NodeDimensions(180, 500, {}), 1: NodeDimensions(180, 100, {})}
    assert _input_regions({0, 1}, positions, sizes) == [[0], [1]]
