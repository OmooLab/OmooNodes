from tools.nodes.arrangement.routes import plan_routes


def test_long_wire_uses_two_horizontal_anchors_around_obstacles():
    routes = plan_routes(
        [((100, 50), (800, 150))], [(0, 1)], {0: 0, 1: 3},
        {0: 0, 3: 800}, {0: 100, 3: 100},
        {0: (0, 0, 100, 90), 1: (800, 100, 900, 190), 2: (300, 40, 420, 160)},
        [(0, "value")], {0: 100},
    )
    assert routes[0] == [(100, 50), (160, 15), (740, 15), (800, 150)]


def test_shared_source_uses_one_horizontal_channel_for_multiple_destinations():
    routes = plan_routes(
        [((100, 50), (800, 100)), ((100, 50), (1200, 300))],
        [(0, 1), (0, 2)], {0: 0, 1: 3, 2: 5},
        {0: 0, 3: 800, 5: 1200}, {0: 100, 3: 100, 5: 100}, {},
        [(0, "geometry"), (0, "geometry")], {0: 200, 1: 200},
    )
    assert routes[0][1] == routes[1][1] == (160, 200)
    assert routes[0][2] == (740, 200)
    assert routes[1][2] == (1140, 200)


def test_blocked_port_bend_gets_a_short_lead_without_tilting_the_channel():
    routes = plan_routes(
        [((100, 50), (800, 150))], [(0, 1)], {0: 0, 1: 3},
        {0: 0, 3: 800}, {0: 200, 3: 100},
        {0: (0, 0, 100, 60), 1: (800, 100, 900, 190), 2: (130, 70, 200, 180)},
        [(0, "geometry")], {0: 200},
    )
    assert routes[0] == [(100, 50), (260, 50), (260, 200), (740, 200), (800, 150)]


def test_distinct_sources_receive_separate_levels_and_short_links_stay_direct():
    routes = plan_routes(
        [((100, 50), (800, 100)), ((100, 70), (800, 120)), ((100, 50), (300, 50))],
        [(0, 1), (0, 1), (0, 2)], {0: 0, 1: 3, 2: 1},
        {0: 0, 1: 300, 3: 800}, {0: 100, 1: 100, 3: 100}, {},
        [(0, "a"), (0, "b"), (0, "a")], {0: 0, 1: 0},
    )
    assert routes[0][1][1] == routes[0][2][1]
    assert routes[1][1][1] == routes[1][2][1]
    assert abs(routes[0][1][1] - routes[1][1][1]) >= 25
    assert routes[2] == [(100, 50), (300, 50)]
