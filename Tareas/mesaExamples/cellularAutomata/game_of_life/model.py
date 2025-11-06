from mesa import Model
from mesa.discrete_space import OrthogonalMooreGrid
from .agent import Cell


class ConwaysGameOfLife(Model):
    """Represents the 2-dimensional array of cells in Conway's Game of Life."""

    def __init__(self, width=50, height=50, initial_fraction_alive=0.2, seed=None):
        """Create a new playing area of (width, height) cells."""
        super().__init__(seed=seed) # seed es para la aleatoridad pero se dice desde donde de la secuencial se empieza

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

        # The row that has already been updated (height-1 = top row already initialized)
        self.current_row = height - 1

        # Initialize cells in the top row (height-1)
        for cell in self.grid.all_cells:
            x, y = cell.coordinate
            init_state = (
                Cell.ALIVE
                if (y == self.current_row and self.random.random() < initial_fraction_alive)
                else Cell.DEAD
            )
            self.cell_grid[(x, y)] = Cell(
                self,  
                cell,  
                init_state=init_state,
            )

        self.running = True

    def step(self):
        """ Moves a row for every step. Each step updates the next row based on
        los 3 vecinos de la fila anterior usando la tabla de reglas dada.

        Main Rule (Where 1 = Alive, 0 = Dead):
        It stops when the last row is reached (height = 0).
        """
        # Get grid dimensions so that it doesn't spawn outside the grid
        width = self.grid.width

        # Si ya actualizamos hasta la última fila (fila 0 en el bottom), detenemos la simulación.
        if self.current_row <= 0:
            self.running = False
            return

        prev_row = self.current_row
        next_row = prev_row - 1

        # Para cada columna calculamos el estado de la celda en la fila siguiente
        for x in range(width):
            left_position = ((x - 1) % width, prev_row)
            center_position = (x, prev_row)
            right_position = ((x + 1) % width, prev_row)

            left_agent = self.cell_grid[left_position]
            center_agent = self.cell_grid[center_position]
            right_agent = self.cell_grid[right_position]

            # We pass the state (0 or 1) of the three neighbors above to determine if the cell is alive or dead
            next_position = (x, next_row)
            next_agent = self.cell_grid[next_position]

            next_agent.set_next_state(
                left_agent.state,
                center_agent.state,
                right_agent.state,
            )
        
        # Ahora aplicamos los next_state en la fila siguiente
        for x in range(width):
            next_agent = self.cell_grid[(x, next_row)]
            next_agent.assume_state()

        # Mark the next row as the current row
        self.current_row = next_row