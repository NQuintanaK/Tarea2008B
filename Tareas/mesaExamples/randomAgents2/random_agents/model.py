from mesa import Model
from mesa.discrete_space import OrthogonalMooreGrid
from mesa.datacollection import DataCollector

from .agent import RandomAgent, ObstacleAgent, DirtAgent, BorderAgent, ChargingStationAgent

class RandomModel(Model):
    """
    Creates a new model with random agents.
    Args:
        num_agents: Number of agents in the simulation
        height, width: The size of the grid to model
    """
    def __init__(self, num_agents=10, width=8, height=8, seed=42):

        super().__init__(seed=seed)
        self.num_agents = num_agents
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

        # Crear estaciones de carga PRIMERO (una por robot)
        charging_cells = self.random.choices(self.grid.empties.cells, k=self.num_agents)
        charging_stations = []
        
        for cell in charging_cells:
            station = ChargingStationAgent(self, cell=cell)
            self.agents.add(station)
            charging_stations.append(station)

        # Crear robots EN LA MISMA POSICIÓN que sus estaciones de carga
        for i in range(self.num_agents):
            robot = RandomAgent(
                self, 
                energy=100,
                cell=charging_stations[i].cell,
                charging_station=charging_stations[i]
            )
            self.agents.add(robot)
            # Vincular estación a robot
            charging_stations[i].assigned_robot = robot

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
                "Energia promedio": get_avg_energy,
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
    """Retorna la basura total recolectada por todos los robots"""
    agents = [a for a in model.agents if isinstance(a, RandomAgent)]
    if not agents:
        return 0
    return sum(agent.trash_count for agent in agents)


def get_avg_energy(model):
    """Calcula el promedio de energía de los robots"""
    agents = [a for a in model.agents if isinstance(a, RandomAgent)]
    if not agents:
        return 0
    return sum(agent.energy for agent in agents) / len(agents)


def get_percentage_clean_cells(model):
    """Calcula el porcentaje de celdas limpias (sin basura)"""
    trash_agents = [a for a in model.agents if isinstance(a, DirtAgent)]
    total_cells = model.width * model.height
    cells_with_trash = len(trash_agents)
    clean_cells = total_cells - cells_with_trash
    return (clean_cells / total_cells) * 100


def get_total_movements(model):
    """Suma todos los movimientos realizados por todos los agentes"""
    agents = [a for a in model.agents if isinstance(a, RandomAgent)]
    if not agents:
        return 0
    return sum(agent.movement_count for agent in agents)