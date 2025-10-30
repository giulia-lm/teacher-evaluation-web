import matplotlib.pyplot as plt
import numpy as np
from collections import Counter
import io
import base64

data = [{'form_id': 3, 'form_title': 'Materia: Ingeniería de Software', 'materia': 'Ingeniería de Software', 'question_id': 13, 'question_text': 'El profesor explica los conceptos claramente.', 'answer_id': 24, 'answer_text': 'Muy de acuerdo'},
        {'form_id': 3, 'form_title': 'Materia: Ingeniería de Software', 'materia': 'Ingeniería de Software', 'question_id': 14, 'question_text': 'El profesor fomenta la participación.', 'answer_id': 25, 'answer_text': 'En desacuerdo'}, 
        {'form_id': 3, 'form_title': 'Materia: Ingeniería de Software', 'materia': 'Ingeniería de Software', 'question_id': 15, 'question_text': 'El material y prácticas están relacionados con la materia.', 'answer_id': 26, 'answer_text': 'De acuerdo'}, 
        {'form_id': 3, 'form_title': 'Materia: Ingeniería de Software', 'materia': 'Ingeniería de Software', 'question_id': 16, 'question_text': 'La evaluación refleja lo visto en clase.', 'answer_id': 27, 'answer_text': 'Muy en desacuerdo'}, 
        {'form_id': 3, 'form_title': 'Materia: Ingeniería de Software', 'materia': 'Ingeniería de Software', 'question_id': 17, 'question_text': 'El profesor muestra interés por el aprendizaje del alumnado.', 'answer_id': 28, 'answer_text': 'De acuerdo'}, 
        {'form_id': 3, 'form_title': 'Materia: Ingeniería de Software', 'materia': 'Ingeniería de Software', 'question_id': 18, 'question_text': 'Comentarios adicionales (texto libre).', 'answer_id': 29, 'answer_text': 'Está padre'}, 
        {'form_id': 8, 'form_title': 'Docente: Montserrat Mariscal', 'materia': None, 'question_id': 43, 'question_text': 'El docente explica los conceptos claramente.', 'answer_id': 30, 'answer_text': 'De acuerdo'}, 
        {'form_id': 8, 'form_title': 'Docente: Montserrat Mariscal', 'materia': None, 'question_id': 44, 'question_text': 'El docente fomenta la participación.', 'answer_id': 31, 'answer_text': 'En desacuerdo'}, 
        {'form_id': 8, 'form_title': 'Docente: Montserrat Mariscal', 'materia': None, 'question_id': 45, 'question_text': 'El docente domina el contenido.', 'answer_id': 32, 'answer_text': 'De acuerdo'}, 
        {'form_id': 8, 'form_title': 'Docente: Montserrat Mariscal', 'materia': None, 'question_id': 46, 'question_text': 'Los recursos son adecuados.', 'answer_id': 33, 'answer_text': 'En desacuerdo'}, 
        {'form_id': 8, 'form_title': 'Docente: Montserrat Mariscal', 'materia': None, 'question_id': 47, 'question_text': 'El docente muestra interés por el aprendizaje.', 'answer_id': 34, 'answer_text': 'En desacuerdo'}, 
        {'form_id': 8, 'form_title': 'Docente: Montserrat Mariscal', 'materia': None, 'question_id': 48, 'question_text': 'Comentarios adicionales (texto libre).', 'answer_id': 35, 'answer_text': 'test'}]

def group(data):
    group_data={}

    for answer in data:
        if answer['form_id'] not in group_data:
            group_data.update({
                answer['form_id']: {
                    'form_title': answer['form_title'],
                    'questions':{}
                    }})
        
        current_form = group_data[answer['form_id']]

        if answer['question_id'] not in current_form['questions']:
            current_form['questions'].update({
                    answer['question_id']: {
                        'question_text': answer['question_text'],
                        'answers': []
                    }})
        
        current_question = current_form['questions'][answer['question_id']]
        current_question['answers'].append(answer['answer_text'])

    for form_id in group_data:
        current_form = group_data[form_id]
        questions_dict = current_form['questions']
        for quest_id in questions_dict:
            #print("q_id:",quest_id)
            question = current_form['questions'][quest_id]
            #print(Counter(question['answers']))
            question.update({
                'freqs': Counter(question['answers'])
            })

    return group_data

def create_plot(xvalues, yvalues, title, xlabel="Respuestas", ylabel="Frecuencia"):
    fig, ax = plt.subplots()
    ax.bar(xvalues, yvalues, color=['orange', 'saddlebrown', 'gold'])
    ax.set_title(title)
    if xlabel:
        ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel)
    return fig

def fig_to_base64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    return f"data:image/png;base64,{img_base64}"

def generate_graphics(data):
    group_data = group(data)

    figures = {}
    figures_base64 = {}
    for form_id in group_data:
        current_form = group_data[form_id]
        questions_dict = current_form['questions']
        
        for quest_id in questions_dict:
            question = current_form['questions'][quest_id]
            # datos para generar los graficos
            question_title = question['question_text']
            answers_counts = question['freqs']
            img_name = f'f{form_id}_q{quest_id}'

            fig = create_plot(answers_counts.keys(), answers_counts.values(), question_title)

            figures.update({img_name: fig})
            #fig.savefig(img_name)
    
    
    for name, fig in figures.items():
        figures_base64[name] = fig_to_base64(fig)
            

    return figures_base64, group_data