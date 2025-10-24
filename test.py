from werkzeug.datastructures import ImmutableMultiDict

multidict = ImmutableMultiDict([('survey_type', 'materia'), ('q43', '142'), ('q44', '147'), ('q45', '150'), ('q46', '155'), ('q47', '158'), ('q48_comments', 'siii me gustoo')])


for key, value in multidict.items():
    if key.startswith('q'):
        question_id = key.lstrip('q')

        if key.endswith('_comments'):
            texto_respuesta = value
            question_id = question_id.replace('_comments', '')
            print("text: ", texto_respuesta)
        else:
            choice_id = value
            print("choice: ", choice_id)
        
        print("ID: ", question_id)