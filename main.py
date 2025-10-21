from decoding import flows, UAV_list, M, N, T
from algorithm import UAVNetwork


network = UAVNetwork(M, N, UAV_list, flows, T)
network.schedule_flows()
scores = network.compute_score()
print(scores)