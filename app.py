from pyvis.network import Network
from geopy.distance import geodesic
import networkx as nx
import pandas as pd
import numpy as np
import constants
import time

def get_capitals(cities):
  capitals = cities.query("capital == 'primary'")
  capitals = capitals.reset_index()
  return capitals

def read_dataset():
  world_cities = pd.read_csv(constants.CSV_FILEPATH, usecols=['city_ascii', 'lat', 'lng', 'country', 'admin_name', 'capital'])
  some_cities = world_cities.loc[world_cities['country'].isin(constants.COUNTRIES)]
  some_cities = some_cities.fillna("")
  some_cities = some_cities.reset_index()
  print("\n\n\n")
  print(some_cities)
  print("\n\n\n")
  some_cities_without_capitals = some_cities.iloc[:, :-1]
  return some_cities_without_capitals, get_capitals(some_cities)

def build_city_identifier(city_name, admin_name):
  return ' - '.join([city_name, admin_name])

def build_graph(cities):
  graph = nx.Graph()

  for i, row_i in cities.iterrows():
    node_name = build_city_identifier(row_i['city_ascii'], row_i['admin_name'])
    graph.add_node(node_name, group=row_i['country'])

  seen = np.zeros((len(cities.index), len(cities.index)))

  for i, row_i in cities.iterrows():
    print(f"City {str(i + 1)} of {len(cities.index)} ({row_i['city_ascii']}, {row_i['country']})")
    
    for j, row_j in cities.iterrows():
      if i == j or seen[j][i] > 0:
        continue

      origin = (row_i['lat'], row_i['lng'])
      dest = (row_j['lat'], row_j['lng'])
      
      km_distance = geodesic(origin, dest).kilometers

      if km_distance < constants.MAX_DISTANCE:
        node_origin = build_city_identifier(row_i['city_ascii'], row_i['admin_name'])
        node_dest = build_city_identifier(row_j['city_ascii'], row_j['admin_name'])
        graph.add_edge(node_origin, node_dest)
      
      seen[i][j] = 1
  return graph

def build_network(graph):
  network = Network('960px')
  network.from_nx(graph)
  return network

def get_country_capital(capitals, country):
  filter = f"country == '{country}'"
  country_capital = capitals.query(filter)
  
  if len(country_capital) > 0:
    country_capital = country_capital.iloc[0]
    return build_city_identifier(country_capital['city_ascii'], country_capital['admin_name'])
  else:
    return ""

def display_network_html(network):
  network.show(constants.HTML_FILENAME)

def run_tests_dijkstra(graph, capital_one, capital_two, capital_three, print_debug=False):
  keep_one_to_two = []
  keep_one_to_three = []
  keep_two_to_three = []

  for i in range(0, constants.QUANTITY_OF_TESTS_ITERATIONS): 
    print(f"-- Dijkstra (iteration {str(i + 1)}) --\n")

    start_time = time.time()
    shortest_path = nx.dijkstra_path(graph, source=capital_one, target=capital_two)
    time_interval = time.time() - start_time
    keep_one_to_two.append(time_interval)
    print("Execution time: ", str(time_interval))
    if print_debug:
      print(f"Between ({capital_one}) and ({capital_two})")
      print("Shortest path: ", list(shortest_path))
      print("Shortest path length: ", len(list(shortest_path)))

    start_time = time.time()
    shortest_path = nx.dijkstra_path(graph, source=capital_one, target=capital_three)
    time_interval = time.time() - start_time
    keep_one_to_three.append(time_interval)
    print("Execution time: ", str(time_interval))
    if print_debug:
      print(f"Between ({capital_one}) and ({capital_three})")
      print("Shortest path: ", list(shortest_path))
      print("Shortest path length: ", len(list(shortest_path)))

    start_time = time.time()
    shortest_path = nx.dijkstra_path(graph, source=capital_two, target=capital_three)
    time_interval = time.time() - start_time
    keep_two_to_three.append(time_interval)
    print("Execution time: ", str(time_interval))
    if print_debug:
      print(f"Between ({capital_two}) and ({capital_three})")
      print("Shortest path: ", list(shortest_path))
      print("Shortest path length: ", len(list(shortest_path)))

  # print the averages
  print("\n-- Dijkstra (averages) --")
  print(f"From ({capital_one}) and ({capital_two}): ", str(sum(keep_one_to_two) / len(keep_one_to_two)))
  print(f"From ({capital_one}) and ({capital_three}): ", str(sum(keep_one_to_three) / len(keep_one_to_three)))
  print(f"From ({capital_two}) and ({capital_three}): ", str(sum(keep_two_to_three) / len(keep_two_to_three)))
  return

def run_tests_bellmanford(graph, capital_one, capital_two, capital_three, print_debug=False):
  keep_one_to_two = []
  keep_one_to_three = []
  keep_two_to_three = []

  for i in range(0, constants.QUANTITY_OF_TESTS_ITERATIONS): 
    print(f"-- Bellman-Ford (iteration {str(i + 1)}) --\n")

    start_time = time.time()
    shortest_path = nx.bellman_ford_path(graph, source=capital_one, target=capital_two)
    time_interval = time.time() - start_time
    keep_one_to_two.append(time_interval)
    print("Execution time: ", str(time_interval))
    if print_debug:
      print(f"From ({capital_one}) to ({capital_two})")
      print("Shortest path: ", list(shortest_path))
      print("Shortest path length: ", len(list(shortest_path)))

    start_time = time.time()
    shortest_path = nx.bellman_ford_path(graph, source=capital_one, target=capital_three)
    time_interval = time.time() - start_time
    keep_one_to_three.append(time_interval)
    print("Execution time: ", str(time_interval))
    if print_debug:
      print(f"From ({capital_one}) to ({capital_three})")
      print("Shortest path: ", list(shortest_path))
      print("Shortest path length: ", len(list(shortest_path)))

    start_time = time.time()
    shortest_path = nx.bellman_ford_path(graph, source=capital_two, target=capital_three)
    time_interval = time.time() - start_time
    keep_two_to_three.append(time_interval)
    print("Execution time: ", str(time_interval))
    if print_debug:
      print(f"From ({capital_two}) to ({capital_three})")
      print("Shortest path: ", list(shortest_path))
      print("Shortest path length: ", len(list(shortest_path)))

  # print the averages
  print("\n-- Bellman-Ford (averages) --")
  print(f"From ({capital_one}) and ({capital_two}): ", str(sum(keep_one_to_two) / len(keep_one_to_two)))
  print(f"From ({capital_one}) and ({capital_three}): ", str(sum(keep_one_to_three) / len(keep_one_to_three)))
  print(f"From ({capital_two}) and ({capital_three}): ", str(sum(keep_two_to_three) / len(keep_two_to_three)))
  return

# main function
# runs the tests by default
def main(should_run_tests=True):
  # network setup
  cities, capitals = read_dataset()
  graph = build_graph(cities)
  network = build_network(graph)

  # checks if tests should be executed
  if should_run_tests:
    # gets the node representation of the capitals that will be used on the tests
    try:
      capital_one = get_country_capital(capitals, constants.COUNTRIES_TO_GET_CAPITAL_FROM[0])
      capital_two = get_country_capital(capitals, constants.COUNTRIES_TO_GET_CAPITAL_FROM[1])
      capital_three = get_country_capital(capitals, constants.COUNTRIES_TO_GET_CAPITAL_FROM[2])
    except:
      print("Couldn't get the capital from the informed country.")

    # runs the tests for both dijkstra and bellman-ford algorithms
    try:
      run_tests_dijkstra(graph, capital_one, capital_two, capital_three)
      run_tests_bellmanford(graph, capital_one, capital_two, capital_three)
    except:
      print("An error happened when running the tests.")

  # generates and displays the graph network through an html page
  display_network_html(network)

# calling the main function
if __name__ == "__main__":
  main()


