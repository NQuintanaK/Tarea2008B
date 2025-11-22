from random_agents.agent import BorderAgent, ChargingStationAgent, DirtAgent, RandomAgent, ObstacleAgent
from random_agents.model import RandomModel

from mesa.visualization import (
    Slider,
    SolaraViz,
    make_space_component,
    make_plot_component,
)

from mesa.visualization.components import AgentPortrayalStyle

def random_portrayal(agent):
    if agent is None:
        return

    portrayal = AgentPortrayalStyle(
        size=50,
        marker="o",
    )

    if isinstance(agent, RandomAgent):
        portrayal.color = "red"
    elif isinstance(agent, ObstacleAgent):
        portrayal.color = "gray"
        portrayal.marker = "s"
        portrayal.size = 100
    elif isinstance(agent, DirtAgent):
        portrayal.color = "brown"
        portrayal.marker = "d"
        portrayal.size = 50
    elif isinstance(agent, BorderAgent):
        portrayal.color = "black"
        portrayal.marker = "s"
        portrayal.size = 100
    elif isinstance(agent, ChargingStationAgent):
        portrayal.color = "blue"
        portrayal.marker = "P"
        portrayal.size = 70

    return portrayal

def post_process(ax):
    ax.set_aspect("equal")

model_params = {
    "seed": {
        "type": "InputText",
        "value": 42,
        "label": "Random Seed",
    },
    "num_agents": Slider("Number of agents", 10, 1, 50),
    "width": Slider("Grid width", 28, 1, 50),
    "height": Slider("Grid height", 28, 1, 50),
}

# Create the model using the initial parameters from the settings
model = RandomModel(
    num_agents=model_params["num_agents"].value,
    width=model_params["width"].value,
    height=model_params["height"].value,
    seed=model_params["seed"]["value"]
)

space_component = make_space_component(
        random_portrayal,
        draw_grid = False,
        post_process=post_process
)

# Crear componentes de gráficas
plot_component = make_plot_component(
    {"Basura Recolectada": "blue", "Energia promedio": "red"},
)

plot_component3 = make_plot_component(
    {"Movimientos Totales": "orange"}
)

page = SolaraViz(
    model,
    components=[space_component, plot_component, plot_component3],
    model_params=model_params,
    name="Random Model",
)