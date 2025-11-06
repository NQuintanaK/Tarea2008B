# FixedAgent: Immobile agents permanently fixed to cells
from mesa.discrete_space import FixedAgent

class Cell(FixedAgent):
    """Represents a single ALIVE or DEAD cell in the simulation."""

    DEAD = 0
    ALIVE = 1

    @property
    def x(self):
        return self.cell.coordinate[0]

    @property
    def y(self):
        return self.cell.coordinate[1]

    @property
    def is_alive(self):
        return self.state == self.ALIVE

    @property
    def neighbors(self):
        return self.cell.neighborhood.agents
    
    # Constructor of Cell class
    def __init__(self, model, cell, init_state=DEAD):
        """Create a cell, in the given state, at the given x, y position."""
        super().__init__(model) # super = Calls the constructor of the parent class FixedAgent
        self.cell = cell
        self.pos = cell.coordinate
        self.state = init_state
        self._next_state = None

    # Identifies the next state based on the current state and neighbors
    def determine_state(self):
        """Compute if the cell will be dead or alive at the next tick.  This is
        based on the number of alive or dead neighbors.  The state is not
        changed here, but is just computed and stored in self._nextState,
        because our current state may still be necessary for our neighbors
        to calculate their next state.
        """

        live_neighbors = 0
        for n in self.neighbors:
            live_neighbors += n.is_alive

        # Get the neighbors and apply the rules on whether to be alive or dead
        # at the next tick.
        #live_neighbors = sum(neighbor.is_alive for neighbor in self.neighbors)

        # Assume nextState is unchanged, unless changed below.
        self._next_state = self.state

    # Calculate next state only from the 3 neighbors in the upper row
    def set_next_state(self, left_state, center_state, right_state):
        # Ensure values are 0 or 1 for simplicity
        a = 1 if left_state == self.ALIVE else 0
        b = 1 if center_state == self.ALIVE else 0
        c = 1 if right_state == self.ALIVE else 0
        pattern = f"{a}{b}{c}"

        if pattern in ["110", "100", "011", "001"]: # Alive patterns
            self._next_state = self.ALIVE
        else:
            self._next_state = self.DEAD

        self.state = self._next_state
        self._next_state = None

    # Updates the cell's state to the next computed state
    def assume_state(self):
        """Set the state to the new computed state -- computed in step()."""
        if self._next_state is not None:
            self.state = self._next_state
            self._next_state = None