import random as r
import copy
import asyncio.queues as q
import datetime

# Defines a coordinate of arbitrary dimensions
class Coordinate:
    def __init__(self, coords = [0]):
        self.dims = coords.__len__()
        self.coords = []
        for i in range(0, self.dims):
            self.coords.append(coords[i])

    #Define equality
    def __eq__(self, other):
        if self.dims != other.dims:
            return False
        for i in range(0, self.dims):
            if self.coords[i] != other.coords[i]:
                return False
        return True

    # Not Equals
    def __ne__(self, other):
        return not self.__eq__(other)

    # Like toString() in Java
    def __str__(self):
        return str(self.coords)

    #Duplicating itself
    def copy(self):
        c = Coordinate(self.coords)
        return c

    # Manhattan Distance between two coordinates
    def dist(self, other):
        if not self.dims == other.dims: raise Exception("Coordinates must have the same dimension.")
        sum = 0
        for c in range(self.dims):
            sum += abs(self.coords[c] - other.coords[c])
        return sum

    # Coordinates of Origin in given dimension
    @staticmethod
    def origin(y):
        c = []
        for j in range(y):
            c.append(0)
        return Coordinate(c)


# Class Package -- Represents one package
class Package:
    def __init__(self, origin, destination):
        # Input Checking
        if not isinstance(origin, Coordinate): raise Exception("origin must be a Coordinate")
        self.origin = origin
        if not isinstance(destination, Coordinate): raise Exception("origin must be a Coordinate")
        self.destination = destination  # Destination of the Package
        self.location = origin.copy()   # Current Location of the Package
        self.is_carried = False         # Is the Package being carried by a Truck
        self.id = r.getrandbits(32)     # (Probably) Unique ID for the Package

    # Define Equality
    def __eq__(self, other):
        if self.id != other.id or self.location != other.location or self.destination != other.destination \
                or self.origin != other.origin:
            return False
        else:
            return True
    # Not Equals
    def __ne__(self, other):
        return not self.__eq__(other)

    # Like toString() in Java
    def __str__(self):
        return "Package: (Origin: " + str(self.origin) + ", Destination: " + str(self.destination) + \
               ", Carried: " + str(self.is_carried) + ", Location: " + str(self.location) + ")"


# Class Truck -- Represents one Truck in the Problem
class Truck:
    def __init__(self, location, max_packages=1):
        # Input Checking
        if not isinstance(location, Coordinate): raise Exception("location must be a Coordinate")
        self.location = location          # Current Location of Truck
        self.max_packages = max_packages  # Maximum Package capacity
        self.packages = []                # The Packages being carried (initially none)
        self.id = r.getrandbits(32)       # (Probably) Unique ID for the Truck

    #define Equality
    def __eq__(self, other):
        if self.id != other.id or self.location != other.location or self.max_packages != other.max_packages \
                or self.packages != other.packages:
            return False
        else:
            return True

    # Not Equals
    def __ne__(self, other):
        return not self.__eq__(other)

    # Like toString()
    def __str__(self):
        return "Truck ID " + str(self.id) + ": (Location: " + str(self.location) + ", Packages: " + str(self.packages.__len__()) + ")"


# Class ProblemState -- Represents an instantaneous state of the problem
class ProblemState:
    def __init__(self, m, n, k, y, size, garage):
        self.m = m        # Number of Trucks
        self.n = n        # Number of Packages
        self.k = k        # Truck Capacity
        self.y = y        # Dimensions
        self.size = size  # Size of City (leave at 1)
        self.cost = 0     # Cost so far in reaching this state

        # Location of Garage (don't change from Origin)
        if not isinstance(garage, Coordinate): raise Exception("garage must be a Coordinate")
        self.garage = garage

        # All Trucks -- they all start at the Garage
        self.trucks = []
        for i in range(m):
            self.trucks.append(Truck(self.garage.copy(), self.k))

        # All Packages -- The have random distinct origin and destination
        self.packages = []
        for i in range(n):
            c1 = self.new_random_coordinate()
            c2 = self.new_random_coordinate()
            while c1 == c2:
                c2 = self.new_random_coordinate()
            self.packages.append(Package(c1, c2))

    # Generates a new random coordinate in y dimensions
    def new_random_coordinate(self):
        c = []
        for j in range(self.y):
            c.append(r.randrange(0, self.size + 1, 1))
        return Coordinate(c)

    # Define Equality - All fields must be equal
    def __eq__(self, other):
        if self.m != other.m or self.n != other.n or self.k != other.k or self.y != other.y or self.size != other.size\
                or self.garage != other.garage:
            return False
        for i in range(self.m):
            if self.trucks[i] != other.trucks[i]:
                return False
        for i in range(self.n):
            if self.packages[i] != other.packages[i]:
                return False
        return True

    # Not Equal
    def __ne__(self, other):
        return not self.__eq__(other)

    # Less Than -- Must be defined for the Priority Queue to work
    # Based only on cost, could be improved
    def __lt__(self, other):
        if self.cost < other.cost:
            return True
        else:
            return False
    # Less Than or Equal
    def __le__(self, other):
        return self.__lt__(other) or self.__eq__(other)

    # Greater Than
    def __gt__(self, other):
        return not self.__le__(other)

    # Greater Than or Equal
    def __ge__(self, other):
        return not self.__lt__(other)

    # Like toString()
    def __str__(self):
        s = "m=" + str(self.m) + ", n=" + str(self.n) + ", k=" + str(self.k) + ", y=" + str(self.y) + ", size="
        s+= str(self.size) + ", cost=" + str(self.cost) + ", h(x)=" + str(self.heuristic())
        s+= "\nTruck(s):"
        for t in self.trucks:
            s+= "\n\t" + str(t)
        s+= "\nPackage(s):"
        for p in self.packages:
            s+= "\n\t" + str(p)
        return s

    # The Successor Function
    # Generates all possible successor states from this state
    def successors(self):
        # a new empty list of ProblemState Objects
        succ = list()

        for i in range(len(self.trucks)):
            # each truck can move to a new position (only 1 at a time)
            # for each coordinate 0 - y
            for c in range(self.y):
                cc = self.trucks[i].location.coords[c]
                # move up if it's not at the upper end of that coordinate
                if cc < self.size:
                    # make a new state, copying the current one
                    new_state = copy.deepcopy(self)
                    # increase cost by 1
                    new_state.cost += 1
                    # move the truck in the new state
                    new_state.trucks[i].location.coords[c] += 1
                    # if the truck is carrying packages, move those too
                    for p in new_state.trucks[i].packages:
                        p.location.coords[c] += 1
                    # append new state to list of successor states
                    succ.append(new_state)
                # move down if it's not at the lower end of that coordinate
                # Similar to above
                if cc > 0:
                    new_state = copy.deepcopy(self)
                    new_state.cost += 1
                    new_state.trucks[i].location.coords[c] -= 1
                    for p in new_state.trucks[i].packages:
                        p.location.coords[c] -= 1
                    succ.append(new_state)

            # If the truck is carrying a package it can drop it off (one at a time)
            for p_idx in range(len(self.trucks[i].packages)):
                # make a new state, copying the current one
                new_state = copy.deepcopy(self)
                # increase cost by 1
                new_state.cost += 1
                # drop off the package
                p = new_state.trucks[i].packages[p_idx]
                p.carried = False
                new_state.trucks[i].packages.remove(p)
                # append new state to list of successor states
                succ.append(new_state)

            # if the truck has room to pickup a new package, check if there is one at it's current location
            # and pick it up
            if len(self.trucks[i].packages) < self.k:
                for p_idx in range(len(self.packages)):
                    # look for packages at the current location
                    if self.packages[p_idx].location == self.trucks[i].location:
                        # make a new state, copying the current one
                        new_state = copy.deepcopy(self)
                        # increase cost by 1
                        new_state.cost += 1
                        # pick up the package
                        p = new_state.packages[p_idx]
                        p.carried = True
                        new_state.trucks[i].packages.append(p)
                        # append new state to list of successor states
                        succ.append(new_state)

        # return list of successor states
        return succ

    # Heuristic Function
    def heuristic(self):
        h = 0

        for t in self.trucks:
            for p in self.packages:
                # add distance from package location to destination
                d1 = p.location.dist(p.destination)
                h += d1
                # if package is not at destination and not carried
                if d1 > 0 and not p.is_carried:
                    # add distance from truck to package
                    h += t.location.dist(p.location)
            # add distance from truck to garage
            h += t.location.dist(self.garage)

        # return heuristic value
        return h


class Problem:
    # Initialize
    def __init__(self, m=1, n=2, k=1, y=2, size=1):
        # Create Initial State based on parameters
        self.initial_state = ProblemState(m, n, k, y, size, Coordinate.origin(y))
        # Current State is a copy of Initial state at the beginning
        self.current_state = copy.deepcopy(self.initial_state)
        # Goal State has all packages at destinations and all trucks at garage
        self.goal_state = copy.deepcopy(self.initial_state)
        for p in self.goal_state.packages:
            p.location = p.destination.copy()

    # isGoal
    # Check to see if a state matches the goal state
    def is_goal(self, state):
        return state == self.goal_state

    # Successors
    # Call successor function for given state
    @staticmethod
    def successors(state):
        return state.successors()


# Implements a queue based on the builtin library asyncio.queues
# https://docs.python.org/3/library/asyncio-queue.html
class StateQueue:
    # initialize the queue
    def __init__(self):
        self.queue = q.Queue(maxsize=0)

    # add a state to the queue
    def add(self, state):
        self.queue.put_nowait(state)

    # Remove an item from the queue
    def remove(self):
        return self.queue.get_nowait()

    # Check if queue is empty
    def empty(self):
        return self.queue.empty()


# Implements a stack based on the builtin library asyncio.queues
# https://docs.python.org/3/library/asyncio-queue.html
class StateStack:
    # initialize the stack
    def __init__(self):
        self.stack = q.LifoQueue(maxsize=0)

    # add a state to the stack
    def add(self, state):
        self.stack.put_nowait(state)

    # Remove an item from the stack
    def remove(self):
        return self.stack.get_nowait()

    # Check if stack is empty
    def empty(self):
        return self.stack.empty()


# Implements a priority queue based on the builtin library asyncio.queues
# https://docs.python.org/3/library/asyncio-queue.html
class StatePriorityQueue:
    # initialize the queue
    def __init__(self):
        self.queue = q.PriorityQueue(maxsize=0)

    # add a state to the queue
    # priority is cost + heuristic function
    def add(self, state):
        priority = state.cost + state.heuristic()
        self.queue.put_nowait((priority, state))

    # Remove an item from the queue
    def remove(self):
        (_, item) = self.queue.get_nowait()
        return item

    # Check if queue is empty
    def empty(self):
        return self.queue.empty()


# Search Class
class Search:
    # Call the specified search method
    @staticmethod
    def search(problem, initial_state, mode = "bfs"):
        # Breadth-first Search
        if mode == "bfs":
            ds = StateQueue()
            return Search.search_basic(problem, initial_state, ds)
        # Depth-first Search
        elif mode == "dfs":
            ds = StateStack()
            return Search.search_basic(problem, initial_state, ds, 100000)
        # Iterative Deepening Search
        elif mode == "ids":
            ds = StateStack()
            return Search.search_ids(problem, initial_state, ds, 100)
        # A* Search
        elif mode == "astar":
            ds = StatePriorityQueue()
            return Search.search_astar(problem, initial_state, ds)
        else:
            raise Exception("Unknown Search Mode")

    # For DFS, BFS, depending on the type of data structure
    # As per pseudocode provided
    @staticmethod
    def search_basic(problem, initial_state, queue, timeout=0):
        queue.add(initial_state)
        steps = 0
        while not queue.empty():
            here = queue.remove()
            # print(here)
            if problem.is_goal(here):
                return here
            else:
                next_states = problem.successors(here)
                for s in next_states:
                    queue.add(s)
            steps += 1
            if timeout > 0 and steps > timeout:
                return "Search timed out after " + str(timeout) + " steps."

        return "Unsuccessful Search"

    # IDS  -- Iterative Deepening Search
    # Based on provided pseudocode with modifications for depth limit
    @staticmethod
    def search_ids(problem, initial_state, queue, maxdepth=100):
        for thisdepth in range(1,maxdepth):
            queue.add((initial_state, 0))
            while not queue.empty():
                here, curdepth = queue.remove()
                curdepth += 1
                # print(here)
                if problem.is_goal(here):
                    return here
                # Only Continue if Depth Limit has not been reached
                elif curdepth < thisdepth:
                    next_states = problem.successors(here)
                    for s in next_states:
                        queue.add((s, curdepth))

        return "Unsuccessful Search"

    # A* Search
    # Similar to basic search but with Priority Queue
    @staticmethod
    def search_astar(problem, initial_state, queue):
        queue.add(initial_state)
        while not queue.empty():
            here = queue.remove()
            # print(here)
            if problem.is_goal(here):
                return here
            else:
                next_states = problem.successors(here)
                for s in next_states:
                    queue.add(s)

        return "Unsuccessful Search"

def main():
    # Set number of runs
    num_runs = 1000
    # Log the start time
    start_time = datetime.datetime.utcnow()
    # Set Up the Problem
    problem = Problem(m=1, n=2, k=1, y=2, size=1)

    # Run num_runs times to get a sense of performance
    for i in range(num_runs):
        Search.search(problem, problem.initial_state, "astar")

    # Log end time
    end_time = datetime.datetime.utcnow()

    # Output results
    print("\n*****\nTOTAL TIME: " + str((end_time - start_time).total_seconds()) +
          "\nAVG. TIME: " + str((end_time - start_time).total_seconds() / num_runs) +
          "\nNumber of Runs: " + str(num_runs))


if __name__ == "__main__":
    main()