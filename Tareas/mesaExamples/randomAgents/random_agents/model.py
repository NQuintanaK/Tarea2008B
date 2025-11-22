from mesa import Model
from mesa.discrete_space import OrthogonalMooreGrid
from mesa.datacollection import DataCollector

from .agent import RandomAgent, ObstacleAgent, DirtAgent, BorderAgent, ChargingStationAgent

class RandomModel(Model):
    """
    Creates a new model with a single roomba agent.
    Args:
        width, height: The size of the grid to model
        seed: Random seed
    """
    def __init__(self, width=28, height=28, seed=42):

        super().__init__(seed=seed)
        self.num_agents = 1
        self.seed = seed
        self.width = width
        self.height = height

        self.grid = OrthogonalMooreGrid([width, height], torus=False)
        
        # Identificar las coordenadas del borde de la grilla
        border = [(x,y)
                for y in range(height)
                for x in range(width)
                if y in [0, height-1] or x in [0, width - 1]]
                

        # Crear las celdas del borde
        for _, cell in enumerate(self.grid):
            if cell.coordinate in border:
                obstacle = BorderAgent(self, cell=cell)
                self.agents.add(obstacle)

        # Obtener la celda en coordenada (1,1)
        start_cell = None
        for cell in self.grid:
            if cell.coordinate == (1, 1):
                start_cell = cell
                break

        # Crear estación de carga en (1,1)
        station = ChargingStationAgent(self, cell=start_cell)
        self.agents.add(station)

        # Crear un único robot en (1,1)
        robot = RandomAgent(
            self, 
            energy=100,
            cell=start_cell,
            charging_station=station
        )
        self.agents.add(robot)
        # Vincular estación a robot
        station.assigned_robot = robot

        # Crear suciedad
        dirt_count = int(self.width * self.height * 0.1)
        DirtAgent.create_agents(
            self,
            dirt_count,
            cell=self.random.choices(self.grid.empties.cells, k=dirt_count)
        )

        # Crear obstáculos
        ObstacleAgent.create_agents(
            self,
            int(self.width * self.height * 0.1),
            cell=self.random.choices(self.grid.empties.cells, k=int(self.width * self.height * 0.1))
        )

        # Configurar DataCollector con funciones externas
        self.datacollector = DataCollector(
            model_reporters={
                "Basura Recolectada": get_total_trash_collected,
                "Energia": get_avg_energy,
                "Porcentaje Limpio": get_percentage_clean_cells,
                "Movimientos Totales": get_total_movements,
            }
        )

        self.running = True

    def step(self):
        '''Advance the model by one step.'''
        self.agents.shuffle_do("step")
        self.datacollector.collect(self)


# Funciones para recolectar datos
def get_total_trash_collected(model):
    """Retorna la basura total recolectada por el robot"""
    agents = [a for a in model.agents if isinstance(a, RandomAgent)]
    if not agents:
        return 0
    return sum(agent.trash_count for agent in agents)


def get_avg_energy(model):
    """Retorna la energía del robot"""
    agents = [a for a in model.agents if isinstance(a, RandomAgent)]
    if not agents:
        return 0
    return agents[0].energy


def get_percentage_clean_cells(model):
    """Calcula el porcentaje de celdas limpias (sin basura)"""
    trash_agents = [a for a in model.agents if isinstance(a, DirtAgent)]
    total_cells = model.width * model.height
    cells_with_trash = len(trash_agents)
    clean_cells = total_cells - cells_with_trash
    return (clean_cells / total_cells) * 100


def get_total_movements(model):
    """Suma todos los movimientos realizados por el robot"""
    agents = [a for a in model.agents if isinstance(a, RandomAgent)]
    if not agents:
        return 0
    return sum(agent.movement_count for agent in agents)