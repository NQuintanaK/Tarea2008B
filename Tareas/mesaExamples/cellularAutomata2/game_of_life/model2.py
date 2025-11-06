from mesa import Model
from mesa.discrete_space import OrthogonalMooreGrid
from .agent import Cell


class ConwaysGameOfLife(Model):
    """Represents the 2-dimensional array of cells in an Elementary Cellular Automaton."""

    def __init__(self, width=50, height=50, initial_fraction_alive=0.2, seed=None):
        """Create a new playing area of (width, height) cells."""
        super().__init__(seed=seed)

        """Grid where cells are connected to their 8 neighbors.

        Example for two dimensions:
        directions = [
            (-1, -1), (-1, 0), (-1, 1),
            ( 0, -1),          ( 0, 1),
            ( 1, -1), ( 1, 0), ( 1, 1),
        ]
        """
        self.grid = OrthogonalMooreGrid((width, height), capacity=1, torus=True)
        # Torus means that the edges are connected so they always have 8 neighbors

        # Maintain references to agents by position for direct access
        self.cell_grid = {}

        # Initialize cells in all rows with random states
        for cell in self.grid.all_cells:
            x, y = cell.coordinate
            init_state = (
                Cell.ALIVE
                if self.random.random() < initial_fraction_alive
                else Cell.DEAD
            )
            self.cell_grid[(x, y)] = Cell(
                self,  
                cell,  
                init_state=init_state,
            )

        self.running = True

    def step(self):
        """Updates all cells simultaneously based on their 3 neighbors (left, center, right).
        This runs infinitely until the simulation is paused.
        
        Main Rule (Where 1 = Alive, 0 = Dead):
        Each cell's next state is determined by its left neighbor, itself, and right neighbor.
        """
        # Get grid dimensions so that it doesn't spawn outside the grid
        width = self.grid.width
        height = self.grid.height

        # Calculate next states for ALL cells based on current states
        for y in range(height):
            for x in range(width):
                left_position = ((x - 1) % width, y)
                center_position = (x, y)
                right_position = ((x + 1) % width, y)

                left_agent = self.cell_grid[left_position]
                center_agent = self.cell_grid[center_position]
                right_agent = self.cell_grid[right_position]

                # Calculate next state for this/exact cell
                center_agent.set_next_state(
                    left_agent.state,
                    center_agent.state,
                    right_agent.state,
                )
        
        # Apply all next_state changes simultaneously to all cells
        for y in range(height):
            for x in range(width):
                agent = self.cell_grid[(x, y)]
                agent.assume_state()