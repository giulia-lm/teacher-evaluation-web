import matplotlib.pyplot as plt
import numpy as np

data = [{'pregunta': 'El docente explica los conceptos claramente.', 
         'respuesta': 'De acuerdo', 
         'materia': None}, 
         {'pregunta': 'El docente fomenta la participación.', 
          'respuesta': 'En desacuerdo', 
          'materia': None}, 
        {'pregunta': 'El docente domina el contenido.', 
         'respuesta': 'De acuerdo', 
         'materia': None}, 
        {'pregunta': 'Los recursos son adecuados.', 
         'respuesta': 'En desacuerdo', 
         'materia': None}, 
         {'pregunta': 'El docente muestra interés por el aprendizaje.', 
          'respuesta': 'En desacuerdo', 
          'materia': None}, 
          {'pregunta': 'Comentarios adicionales (texto libre).', 
           'respuesta': 'test', 
           'materia': None}]
def create_plot(xvalues, yvalues, title, xlabel="", ylabel=""):
    fig, ax = plt.subplots()
    ax.plot(xvalues, yvalues)
    ax.set_title(title)
    if xlabel:
        ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel)
    return fig

x = np.linspace(0, 10, 100)
y = np.sin(x)

fig = create_plot(x, y, "test1")
fig.savefig("test_plot1.png")