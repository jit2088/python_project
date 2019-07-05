import DragonQueen5 as DragonQueen
import datetime as dt
import copy
from sys import argv


class Telemetry:
    def __init__(self, description="Telemetry"):
        self.description = description
        self.start_time = dt.datetime.utcnow()
        self.stop_time = 0
        self.total_time = 0
        self.path = None
        self.nodes_visited = 0
        self.depth_reached = 0
        self.max_queue_size = 0
        self.sum_queue_size = 0
        self.mean_queue_size = 0
        self.plies_played = 0
        self.avg_time_per_ply = 0
        self.winner = None

    def log(self, node):
        self.nodes_visited += 1
        self.depth_reached = max(self.depth_reached, node.countPlies)
        num_successors = len(node.successors())
        self.max_queue_size = max(self.max_queue_size, num_successors)
        self.sum_queue_size += num_successors

    def stop(self, path):
        self.stop_time = dt.datetime.utcnow()
        self.total_time = (self.stop_time - self.start_time)
        self.path = copy.deepcopy(path)
        last_node = self.path[-1]
        self.mean_queue_size = self.sum_queue_size / self.nodes_visited
        self.plies_played = last_node.countPlies
        self.avg_time_per_ply = self.total_time / self.plies_played

        if last_node.winFor('D'):
            self.winner = "Dragons"
        elif last_node.winFor('W'):
            self.winner = "Wights"
        else:
            self.winner = "Draw"

    def __str__(self):
        s = "Telemetry:"
        s += "\n\tDescription:       \t" + self.description
        s += "\n\tNodes Visited:     \t" + str(self.nodes_visited)
        s += "\n\tDepth Reached:     \t" + str(self.depth_reached)
        s += "\n\tMax. Queue Size:   \t" + str(self.max_queue_size)
        s += "\n\tMean Queue Size:   \t" + str(self.mean_queue_size)
        s += "\n\tTotal Time     :   \t" + str(self.total_time)
        s += "\n\tPlies Played:      \t" + str(self.plies_played)
        s += "\n\tAvg. Time Per Ply: \t" + str(self.avg_time_per_ply)
        s += "\n\tWinner:            \t" + str(self.winner)
        return s

    def to_csv(self):
        s = ""
        s += self.description + ","
        s += str(self.nodes_visited) + ","
        s += str(self.depth_reached) + ","
        s += str(self.max_queue_size) + ","
        s += str(self.mean_queue_size) + ","
        s += str(self.total_time) + ","
        s += str(self.plies_played) + ","
        s += str(self.avg_time_per_ply) + ","
        s += str(self.winner)
        return s

    @staticmethod
    def csv_headers():
        s = ""
        s += "Description" + ","
        s += "Nodes Visited" + ","
        s += "Depth Reached" + ","
        s += "Max. Queue Size" + ","
        s += "Mean Queue Size" + ","
        s += "Total Time" + ","
        s += "Plies Played" + ","
        s += "Avg. Time Per Ply" + ","
        s += "Winner"
        return s


def main():
    if len(argv) == 1:
        print("Dragon Queen Game Testing:")
        min_depth = int(input("Input minimum search depth: "))
        max_depth = int(input("Input maximum search depth: "))
        if max_depth < min_depth:
            print("max_depth less than min_depth. Aborting.")
            exit(1)
        num_runs = int(input("Input number of runs per config: "))
        total_num_runs = 2 * (max_depth + 1 - min_depth) * num_runs
        if input("This will result in " + str(total_num_runs) + " games. Continue? (y/n): ").lower() != 'y':
            print("Aborting.")
            exit(0)
        file_name = input("Enter output file name: ")
        if file_name[-4:] != ".csv":
            file_name = file_name + ".csv"

    elif len(argv) == 4:
        min_depth = int(argv[1])
        max_depth = int(argv[2])
        if max_depth < min_depth:
            print("max_depth less than min_depth. Aborting.")
            exit(1)
        num_runs = int(argv[3])
        file_name = "output.csv"

    elif len(argv) == 5:
        min_depth = int(argv[1])
        max_depth = int(argv[2])
        if max_depth < min_depth:
            print("max_depth less than min_depth. Aborting.")
            exit(1)
        num_runs = int(argv[3])
        file_name = argv[4]
        if file_name[-4:] != ".csv":
            file_name = file_name + ".csv"

    else:
        print("Usage: python " + str(argv[0]) + " [min_depth max_depth num_runs [output_file_name]]")
        exit(1)
        return

    count_runs = 0
    f = open(file_name, "w")
    f.write("Run No.,Depth,Pruning," + Telemetry.csv_headers() + "\n")
    for pruning in [True, True]:
        for depth in range(min_depth, max_depth + 1):
            for i in range(0, num_runs):
                count_runs += 1
                tel = Telemetry("Pruning = " + str(pruning) + " Depth = " + str(depth))
                game = DragonQueen.DragonQueen(None)
                path = list()
                path.append(game)
                while True:
                    cur = path[-1]
                    if cur.isTerminal():
                        break
                    else:
                        _, next_move = DragonQueen.minimax_ab(cur, maxdepth=depth, ab_prune=pruning, telemetry=tel)
                                                              # ab_prune=pruning, telemetry=tel)
                        if next_move is None:
                            break
                        path.append(next_move)
                tel.stop(path)
                print("Run " + str(count_runs) + ":")
                print(tel)
                f.write(str(count_runs) + "," + str(depth) + "," + str(pruning) + "," + tel.to_csv() + "\n")

    f.close()


if __name__ == "__main__":
    main()
