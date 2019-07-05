import datetime as dt

class DragonQueen:
    def __init__(self, state, player='W', countplies=1):
        if state is None:
            self.gameState = dict()
            for r in range(1, 6):
                for c in range(1, 6):
                    self.gameState[r, c] = '.'
            self.gameState[1, 3] = 'Q'
            for c in range(2, 5):
                self.gameState[2, c] = 'D'
            for c in range(1, 6):
                self.gameState[5, c] = 'W'
        else:
            self.gameState = state

        self.whoseTurn = player
        self.cachedWin = False
        self.cachedWinner = None
        self.countPlies = countplies

    def __str__(self):
        s = ""
        for r in range(1, 6):
            for c in range(1, 6):
                s += self.gameState[r, c]
        return s

    def str(self):
        return str(self)

    def isMinNode(self):
        return self.whoseTurn == 'D'

    def isMaxNode(self):
        return self.whoseTurn == 'W'

    def isTerminal(self):
        return self.winFor('W') or self.winFor('D') or self.draw()

    def successors(self):
        """
        Returns all successor states to the current one
        :return: list of DragonQueen objects or an empty list if this is a terminal node
        """
        if self.isTerminal():
            return list()
        all_pieces = self.all_pieces(self.whoseTurn)
        all_positions = list(self.gameState.keys())
        next_player = self.togglePlayer(self.whoseTurn)
        states = list()
        for p in all_pieces:
            for pos in all_positions:
                states.append(self.move(p, pos))
        states = filter((lambda s: s is not None), states)
        nodes = [DragonQueen(s, next_player, self.countPlies + 1) for s in states]
        return nodes

    def utility(self):
        """
        Returns the utility for a terminal node
        :return: +infinity if win for Dragon, -infinity if win for Wight, 0 if draw
        """
        if self.winFor('W'):
            return float('inf')
        elif self.winFor('D'):
            return -float('inf')
        else:
            return 0.0

    def heuristic(self):
        """
        Returns the estimate of utility for a non-terminal node
        :return: float in the range -10.0 to +10.0
        """
        h = 0.0
        for p in self.all_pieces('D'):
            r, c = p
            if self.gameState[p] == 'Q':
                # -2 points for queen piece on board plus -1 to -5 based on distance from goal
                h -= r +2
            else:
                # 1 point for each dragon piece on board
                h -= 1

        for p in self.all_pieces('W'):
            r, c = p
            # 1 point for each wight piece on the board
            h += 1
            # 1 to 5 based on distance from opposite home row
            h += (6.0 - r) / 5.0

        return h

    def winFor(self, player):
        """
        Checks if the current board state in a win for the given player
        :param player: 'D' or 'W'
        :return: boolean
        """
        if self.cachedWin is False:
            if player == 'D':
                won = any([self.gameState[5, c] == 'Q' for c in range(1, 6)])
            else:
                won = all([self.gameState[r, c] != 'Q' for r in range(1, 6) for c in range(1, 6)])
            if won:
                self.cachedWin = True
                self.cachedWinner = player
                return True
            else:
                return False
        else:
            return player == self.cachedWinner

    def draw(self):
        """
        Checks for a draw state.
        :return: boolean
        """
        if self.winFor('W') or self.winFor('D'):
            return False
        elif self.countPlies >= 50:
            return True
        elif len(self.all_pieces('W')) == 0:
            return True
        else:
            # TODO: check for other draw conditions
            # e.g., one Wight pinned in the corner by a Dragon and Queen, no other pieces on board.
            # Prefer to check empty successor function to ensure all draw states are covered.
            return False

    @staticmethod
    def togglePlayer(p):
        if p == 'D':
            return 'W'
        else:
            return 'D'

    def move(self, fromgrid, togrid):
        """
        Evaluates one potential move on the game board
        :param fromgrid: location of piece to move
        :param togrid:  location to move the piece to
        :return: state of board following the move or None if move is invalid
        """
        (r_from, c_from) = fromgrid
        (r_to, c_to) = togrid

        # Deal with some degenerate cases first
        # Out of bounds
        if r_from < 1 or r_from > 5 or c_from < 1 or c_from > 5:
            return None
        if r_to < 1 or r_to > 5 or c_to < 1 or c_to > 5:
            return None

        # Trying to move too far
        if abs(r_from - r_to) > 1 or abs(c_from - c_to) > 1:
            return None

        # Not moving
        if fromgrid == togrid:
            return None

        # Dragons' Turn
        if self.whoseTurn == 'D':
            if self.gameState[r_from, c_from] == 'D' or self.gameState[r_from, c_from] == 'Q':
                if self.gameState[r_to, c_to] == '.' or self.gameState[r_to, c_to] == 'W':
                    newstate = self.gameState.copy()
                    newstate[r_to, c_to] = newstate[r_from, c_from]
                    newstate[r_from, c_from] = '.'
                    return newstate

                # No empty space or hostile piece at To location
                else:
                    return None

            # No friendly piece at From location
            else:
                return None

        # Wights' turn
        else:
            if self.gameState[r_from, c_from] == 'W':
                # Hostile piece at To location -- capture
                if self.gameState[r_to, c_to] == 'D' or self.gameState[r_to, c_to] == 'Q':
                    # Diagonal move -- legal
                    if r_from != r_to and c_from != c_to:
                        newstate = self.gameState.copy()
                        newstate[r_to, c_to] = newstate[r_from, c_from]
                        newstate[r_from, c_from] = '.'
                        return newstate
                    # Straight move -- illegal
                    else:
                        return None

                # Open space at To location -- move
                elif self.gameState[r_to, c_to] == '.':
                    # Straight move -- legal
                    if r_from == r_to or c_from == c_to:
                        newstate = self.gameState.copy()
                        newstate[r_to, c_to] = newstate[r_from, c_from]
                        newstate[r_from, c_from] = '.'
                        return newstate
                    # Diagonal move -- illegal
                    else:
                        return None

                # No empty space or hostile piece at To location
                else:
                    return None

            # No friendly piece at From location
            else:
                return None

    def get_move(self):
        """
        Gets and validates input from user for human player move.
        :return: DragonQueen object with new board state after validated move
        """
        all_pieces = self.all_pieces(self.whoseTurn)
        while True:
            while True:
                try:
                    inputs = input("Enter coordinates of piece to move, example: -- 5,1 --  ").split(',')
                    print(inputs)
                    inputs = [int(d) for d in inputs]
                except ValueError:
                    print("Could not read coordinates, please try again.")
                    continue

                try:
                    piece = (inputs[0], inputs[1])
                    if piece not in all_pieces:
                        print("No friendly piece at " + str(piece) + "!")
                        continue
                    else:
                        break
                except ValueError:
                    print("Could not read coordinates, please try again.")
                    continue

            while True:
                try:
                    inputs = input("Enter coordinates of destination, input pattern: example: -- 5,1 -- ").split(',')
                    inputs = [int(d) for d in inputs]
                    dest = (inputs[0], inputs[1])
                    break
                except ValueError:
                    print("Could not read coordinates, please try again.")
                    continue

            try:
                new_move = self.move(piece, dest)
                if new_move is None:
                    print(str(piece) + " to " + str(dest) + " is not a valid move. Please try again.")
                    continue
                break
            except ValueError:
                print("Could not read input, please try again.")
                continue

        new_state = self.gameState.copy()
        new_state[dest] = new_state[piece]
        new_state[piece] = '.'

        new_move = DragonQueen(new_state, self.togglePlayer(self.whoseTurn), self.countPlies + 1)

        return new_move

    def all_pieces(self, player):
        """
        Gets the locations of all pieces for a given player
        :param player: the player
        :return: List of board positions containing friendly pieces
        """
        if player == 'W':
            return [v for v in self.gameState if self.gameState[v] == 'W']
        else:
            return [v for v in self.gameState if self.gameState[v] == 'D' or self.gameState[v] == 'Q']

    def queen_dist(self, pos):
        """
        Returns the Manhattan distance from the given board position to the queen piece
        :param pos: reference board position
        :return:
        """
        r, c = pos
        q_r, q_c = [v for v in self.gameState if self.gameState[v] == 'Q'][0]

        return float(abs(q_r - r) + abs(q_c - c))

    def display(self):
        """
        Prints the game state to the console in user-friendly format
        :return: None
        """
        print("    1   2   3   4   5 ")
        for r in range(1, 6):
            print("  +---+---+---+---+---+")
            line = "" + str(r) + " |"
            for c in range(1, 6):
                line += (" " + self.gameState[r, c] + " |")
            print(line)
        print("  +---+---+---+---+---+")
        print("Turn: " + self.whoseTurn + ", Ply: " + str(self.countPlies) + "\n")


def minimax_ab(node, maxdepth=1, ab_prune=True, telemetry=None):
    """
    minimax search with specified depth limit and optional alpha-beta pruning
    :param node:  a Game object responding to the following methods:
        str(): return a unique string describing the state of the game
            (for use in hash table)
        successors(): returns a list of all legal game states that extend
            this one by one move
        isMinNode(): returns True if the node represents a state in which
            Min is to move
        isMaxNode(): returns True if the node represents a state in which
            Max is to move
        utility(): returns the utility of a terminal node
        heuristic(): estimates the utility of an non-terminal node
    :param maxdepth: cutoff depth for search
    :param ab_prune: use alpha-beta pruning
    :param telemetry: a telemetry object with a log() function that accepts a node
    :return: the value of the game state, the game state
    """
    infinity = float('inf')

    def minimax_val_ab(node_v, alpha=-infinity, beta=infinity, maxdepth_v=(maxdepth-1)):
        """
        :param node_v: the root node for search
        :param alpha:
        :param beta:
        :param maxdepth_v: depth limit
        :return: value for minimax search
        """
        if telemetry is not None:
            telemetry.log(node)

        if maxdepth_v <= 0:
            return node_v.heuristic()

        successors = node_v.successors()
        if len(successors) <= 0:
            return node_v.utility()
        elif node_v.isMaxNode():
            if ab_prune:
                value = -infinity
                for state in successors:
                    value = max(value, minimax_val_ab(state, alpha, beta, maxdepth_v - 1))
                    if value >= beta:
                        return value
                    alpha = max(alpha, value)
                return value
            else:
                vs = [minimax_val_ab(c, maxdepth_v=(maxdepth_v - 1)) for c in successors]
                return max(vs)
        elif node_v.isMinNode():
            if ab_prune:
                value = infinity
                for state in successors:
                    value = min(value, minimax_val_ab(state, alpha, beta, maxdepth_v - 1))
                    if value <= alpha:
                        return value
                    beta = min(beta, value)
                return value
            else:
                vs = [minimax_val_ab(c, maxdepth_v=(maxdepth_v - 1)) for c in successors]
                return min(vs)
        else:
            print("Something went horribly wrong")
            exit(1)

    # Main body of minimax_ab starts here
    choices = [(minimax_val_ab(c), c) for c in node.successors()]
    
    if len(choices) <= 0:
        # No successors, this is a terminal node, return utility, None
        # None indicates no possible moves
        result = node.utility(), None
    elif node.isMaxNode():

        result = max(choices, key=lambda t: t[0])
    elif node.isMinNode():
        result = min(choices, key=lambda t: t[0])
    else:
        print("Something went horribly wrong")
        result = None
        exit(1)
    return result


def main():
    game = DragonQueen(None)
    path = list()
    path.append(game)

    print("Dragon Queen Game:")
    game.display()
    queen_computer = input("Dragon Queen: (t for computer, f for human) ").lower() == 't'
    wight_computer = input("Wights: (t for computer, f for human) ").lower() == 't'
    print("\n")

    start = dt.datetime.utcnow()
    while True:
        cur = path[-1]
        cur.display()
        if cur.whoseTurn == 'W' and not wight_computer:
            path.append(cur.get_move())
        elif cur.whoseTurn == 'D' and not queen_computer:
            path.append(cur.get_move())
        elif cur.isTerminal():
            break
        else:
            _, next_move = minimax_ab(cur, maxdepth=6, ab_prune=True)
            if next_move is None:
                break
            path.append(next_move)

    if cur.winFor('D'):
        print("Dragons Win!")
    elif cur.winFor('W'):
        print("Wights Win!")
    else:
        print("Draw.")

    endTime = dt.datetime.utcnow()

    duration = endTime - start

    print(duration)

if __name__ == "__main__":
    main()
