import matplotlib.pyplot as plt
from collections import Counter
import io
import base64
from matplotlib.backends.backend_pdf import PdfPages  
from datetime import datetime as dt

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
    figs_forms = {}
    for form_id in group_data:
        current_form = group_data[form_id]
        #print("''", current_form)
        questions_dict = current_form['questions']
        
        for quest_id in questions_dict:
            question = current_form['questions'][quest_id]
            # datos para generar los graficos
            question_title = question['question_text']
            answers_counts = question['freqs']
            img_name = f'f{form_id}_q{quest_id}'

            fig = create_plot(answers_counts.keys(), answers_counts.values(), question_title)

            figures.update({img_name: fig})
            
            form_title = current_form['form_title']

            if form_title not in figs_forms:
                figs_forms[form_title] = [fig]
            else:
                figs_forms[form_title].append(fig)
            #fig.savefig(img_name)
    
    
    for name, fig in figures.items():
        figures_base64[name] = fig_to_base64(fig)
            
    return figures, figures_base64, figs_forms


def figs_to_pdf(figures, pdf_title="teacher_metrics.pdf", doc_title="Reporte de Métricas"):
    """
    figures: dict { nombre_formulario : figura_matplotlib }
    """
    with PdfPages(pdf_title, metadata={'Title': doc_title}) as pdf:

        # portada
        fig_portada = plt.figure(figsize=(8.27, 11.69))  # A4 size
        fig_portada.clf()

        fig_portada.text(
            0.5, 0.6,
            doc_title,
            ha='center', va='center',
            fontsize=28, weight='bold'
        )

        fig_portada.text(
            0.5, 0.45,
            "Evaluación Docente",
            ha='center', va='center',
            fontsize=14
        )

        now = dt.now()
        fecha = f'{now.day}/{now.month}/{now.year}. Hora: {now.hour}:{now.minute}'

        fig_portada.text(
            0.5, 0.25,
            f'Fecha de generación: {fecha}',
            ha='center', va='center',
            fontsize=14
        )

        pdf.savefig(fig_portada)
        plt.close(fig_portada)

        # graficos
        for form_name, _ in figures.items():
            for fig in figures[form_name]:
                fig_page = plt.figure(figsize=(8.27, 11.69))  
                fig_page.subplots_adjust(top=0.87) 

                fig_page.suptitle(
                    f"Resultados del formulario '{form_name}'",
                    fontsize=12,
                    weight="bold",
                    y=0.95
                )

                # subplot donde irá el gráfico
                ax = fig_page.add_subplot(111)


                for original_ax in fig.axes:
                    original_ax_fig = original_ax.get_figure()
                    original_ax_fig.canvas.draw()
                    img = original_ax_fig.canvas.buffer_rgba()

                    ax.imshow(img)
                    ax.axis("off")

                pdf.savefig(fig_page)
                plt.close(fig_page)