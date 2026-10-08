from collections import defaultdict
import heapq




















def parse_input(inputString):
    ship_graph = {}
    cost_lookup = defaultdict(lambda: float("inf"))
    routes = inputString.split(",")
    for route in routes:
        soucre_country, target_country, ship_method, cost = route.split(":")
        if soucre_country not in ship_graph:
            ship_graph[soucre_country] = []
        ship_graph[soucre_country].append((target_country, ship_method, int(cost)))

        cost_lookup[(soucre_country, target_country)] = int(cost)

    return ship_graph, cost_lookup


def travel_cost(inputString, soucre_country, target_country, method):
    ship_graph, cost_lookup = parse_input(inputString)
    if soucre_country not in ship_graph:
        # throw error
        return "soucre_country not in ship_graph"
    else:
        res = []
        for ship_detail in ship_graph[soucre_country]:
            ship_target_country, ship_method, cost = ship_detail
            if ship_target_country == target_country and ship_method == method:
                res.append(int(cost))

        if len(res) == 0:
            # throw error
            return "target_country or method not in ship_graph[soucre_country]"
        else:
            return res


def travel_route(inputString, soucre_country, target_country):
    ship_graph, cost_lookup = parse_input(inputString)
    if soucre_country not in ship_graph:
        # throw error
        return "soucre_country not in ship_graph"
    else:
        res = []
        for mid, mid_method, mid_cost in ship_graph[soucre_country]:
            if mid == target_country:
                res.append(
                    {
                        "route": [soucre_country, mid],
                        "method": [mid_method],
                        "cost": int(mid_cost),
                    }
                )
            if mid in ship_graph:
                for target, target_method, target_cost in ship_graph[mid]:
                    if target == target_country:
                        res.append(
                            {
                                "route": [soucre_country, mid, target_country],
                                "method": [mid_method, target_method],
                                "cost": int(mid_cost) + int(target_cost),
                            }
                        )

        if len(res) == 0:
            # throw error
            return "route not in ship_graph"
        else:
            return res


# def travel_cheapest(inputString, soucre_country, target_country):
#     routes = travel_route(inputString, soucre_country, target_country)


#     # catch errors
#     if isinstance(routes, str):
#         return routes
#     else:
#         min_cost_route = min(routes, key=lambda x: x["cost"])
#         return min_cost_route["cost"]
def travel_cheapest(inputString, soucre_country, target_country):
    ship_graph, cost_lookup = parse_input(inputString)
    if soucre_country not in ship_graph:
        # throw error
        return "soucre_country not in ship_graph"
    else:
        res = []
        for mid, mid_method, mid_cost in ship_graph[soucre_country]:
            if mid == target_country:
                cost_lookup[(soucre_country, target_country)] = min(
                    cost_lookup[(soucre_country, target_country)], int(mid_cost)
                )

            if mid in ship_graph:
                for target, target_method, target_cost in ship_graph[mid]:
                    if target == target_country:
                        total_cost = int(mid_cost) + int(target_cost)
                        cost_lookup[(soucre_country, target_country)] = min(
                            cost_lookup[(soucre_country, target_country)],
                            total_cost,
                        )

        if (soucre_country, target_country) not in cost_lookup:
            # throw error
            return "(soucre_country, target_country) not in cost_lookup"
        else:
            return cost_lookup[(soucre_country, target_country)]


# more than one transfers
def travel_cheapest_any_transfer(inputString, soucre_country, target_country):
    ship_graph, cost_lookup = parse_input(inputString)
    if soucre_country not in ship_graph:
        # throw error
        return "soucre_country not in ship_graph"
    else:
        heap = [(0, soucre_country, [soucre_country], [])]
        visited = set()
        while heap:
            cost, node, path, methods = heapq.heappop(heap)
            if node == target_country:
                return {"path": path, "method": methods, "cost": cost}
            if (node, len(path)) in visited:
                continue
            visited.add((node, len(path)))

            for next_node, next_method, next_cost in ship_graph[node]:
                if next_node in path:
                    continue
                heapq.heappush(
                    heap,
                    (
                        cost + next_cost,
                        next_node,
                        path + [next_node],
                        methods + [next_method],
                    ),
                )

        # throw error
        return "(soucre_country, target_country) not in cost_lookup"


if __name__ == "__main__":
    inputString = "US:UK:FEDEX:5,US:CA:UPS:1,CA:FR:DHL:3,UK:FR:DHL:2,US:FR:UPS:1"
    # 1. given a source country, target country, and method, return cost of traveling
    # Ex. travelCost(US, UK, FEDEX) => 5
    print("Q1:")
    print(travel_cost(inputString, "US", "UK", "FEDEX"))
    print(travel_cost(inputString, "CN", "UK", "FEDEX"))
    print(travel_cost(inputString, "US", "CN", "FEDEX"))
    print(travel_cost(inputString, "US", "UK", "CN"))

    # 2. given a source country and target country, return paths, method, and cost of traveling if one transfer can be made
    # Ex. travelRoute(US, FR) => {path: [US, UK, FR], method:[FEDEX, DHL], cost: 7}
    print("Q2:")
    print(travel_route(inputString, "US", "FR"))

    # 3. given a source country and target country, return path, methods, and cost of traveling of the cheapest route if one transfer can be made
    # Ex. travelCheapest(US, FR) => {path: [US, CA, FR], method:[UPS, DHL], cost: 4}
    print("Q3:")
    print(travel_cheapest(inputString, "US", "FR"))

    # 4. we can have more than one transfers
    print("Q4:")
    print(travel_cheapest_any_transfer(inputString, "US", "FR"))
    input_with_loop = "US:UK:FEDEX:5,UK:US:FEDEX:5,US:FR:UPS:8,FR:FR:DHL:1"
    print(travel_cheapest_any_transfer(input_with_loop, "US", "FR"))
