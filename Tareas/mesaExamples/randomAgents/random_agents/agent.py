from mesa.discrete_space import CellAgent, FixedAgent

class RandomAgent(CellAgent):
    """
    Agent that moves randomly.
    Attributes:
        unique_id: Agent's ID
        energy: Current battery level
        max_energy: Maximum battery capacity
        charging_station: Reference to assigned charging station
        is_charging: Whether the agent is currently charging
    """
    def __init__(self, model, energy=100, cell=None, charging_station=None):
        """
        Creates a new random agent.
        Args:
            model: Model reference for the agent
            cell: Reference to its position within the grid
            charging_station: Assigned charging station for this agent
        """
        super().__init__(model)
        self.max_energy = energy
        self.energy = energy
        self.charging_station = charging_station
        self.is_charging = False
        self.cell = cell
        
        # Nuevos atributos para las métricas
        self.trash_count = 0  # Cantidad de basura recolectada
        self.movement_count = 0  # Total de movimientos realizados

    def move(self):
        """
        Determines the next cell to move to. Prioritizes:
        1. Charging station if energy is low
        2. Cells with dirt
        3. Random empty cells
        """
        # If energy is low, go to charging station
        if self.energy <= 30 and self.charging_station:
            if self.cell == self.charging_station.cell:
                # Already at charging station
                self.is_charging = True
                return
            else:
                # Move towards charging station
                self.is_charging = False
                self.move_towards_target(self.charging_station.cell)
                self.movement_count += 1  # Incrementar contador
                return
        
        self.is_charging = False
        
        # Prefer cells with DirtAgent
        cells_with_dirt = self.cell.neighborhood.select(
            lambda cell: any(isinstance(obj, DirtAgent) for obj in cell.agents)
        )
        
        # If there are cells with dirt, move to one of them
        if len(cells_with_dirt) > 0:
            self.cell = cells_with_dirt.select_random_cell()
            self.movement_count += 1  # Incrementar contador
        else:
            # Otherwise, move to any empty cell
            next_moves = self.cell.neighborhood.select(lambda cell: cell.is_empty)
            if len(next_moves) > 0:
                self.cell = next_moves.select_random_cell()
                self.movement_count += 1 

    def move_towards_target(self, target_cell):
        """
        Moves one step towards the target cell (charging station)
        """
        current_x, current_y = self.cell.coordinate
        target_x, target_y = target_cell.coordinate
        
        # Calculate direction
        dx = target_x - current_x
        dy = target_y - current_y
        
        # Get possible moves in the neighborhood
        possible_moves = self.cell.neighborhood.select(
            lambda cell: not any(isinstance(obj, (ObstacleAgent, BorderAgent)) for obj in cell.agents)
        )
        
        if len(possible_moves) == 0:
            return
        
        # Find the cell that gets us closer to target
        best_cell = None
        best_distance = float('inf')
        
        for cell in possible_moves.cells:
            cell_x, cell_y = cell.coordinate
            distance = abs(target_x - cell_x) + abs(target_y - cell_y)
            if distance < best_distance:
                best_distance = distance
                best_cell = cell
        
        if best_cell:
            self.cell = best_cell

    def eat_dirt(self):
        """
        Eats dirt in the current cell if any exists
        """
        # Don't clean while charging
        if self.is_charging:
            return
            
        # Check if there's a DirtAgent in the current cell and eat it
        for agent in list(self.cell.agents):
            if isinstance(agent, DirtAgent):
                agent.clean()
                self.trash_count += 1 

    def charge(self):
        """
        Charges the battery when at charging station
        """
        if self.is_charging and self.charging_station and self.cell == self.charging_station.cell:
            charge_amount = 5  # Cantidad de energía recargada por step
            self.energy = min(self.energy + charge_amount, self.max_energy)
            
            # Si está completamente cargado, deja de cargar
            if self.energy >= self.max_energy:
                self.is_charging = False

    def step(self):
        """
        Determines the new direction it will take, then moves and eats dirt
        """
        if self.is_charging:
            # If charging, just charge and don't move
            self.charge()
        else:
            # Normal behavior: move and clean
            self.move()
            self.energy -= 1  # Reduce energy after moving
            self.eat_dirt()
        
        # Remove agent if energy depleted
        if self.energy <= 0:
            self.remove()


class BorderAgent(FixedAgent):
    """
    Border agent. Just to add borders to the grid.
    """
    def __init__(self, model, cell):
        super().__init__(model)
        self.cell = cell

    def step(self):
        pass


class ObstacleAgent(FixedAgent):
    """
    Obstacle agent. Just to add obstacles to the grid.
    """
    def __init__(self, model, cell):
        super().__init__(model)
        self.cell = cell

    def step(self):
        pass


class DirtAgent(FixedAgent):
    """
    Dirt agent. Just to add dirt to the grid.
    """
    def __init__(self, model, cell):
        super().__init__(model)
        self.cell = cell
        self._is_dirty = True
    
    @property
    def is_dirty(self):
        """Whether the cell is dirty/Dirt patch exists."""
        return self._is_dirty
    
    @is_dirty.setter
    def is_dirty(self, value: bool) -> None:
        """Set dirt state. When cleaned (False), remove from grid."""
        self._is_dirty = value

    def clean(self):
        self.is_dirty = False
        self.cell.remove_agent(self)

    def step(self):
        pass


class ChargingStationAgent(FixedAgent):
    """
    Charging Station agent. Recharges assigned robot.
    """
    def __init__(self, model, cell, assigned_robot=None):
        super().__init__(model)
        self.cell = cell
        self.assigned_robot = assigned_robot

    def step(self):
        pass