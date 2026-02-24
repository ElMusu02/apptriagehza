from flask import Flask, render_template, request

app = Flask(__name__)

# Sección 2: parámetros con puntaje según grado
SECCION2_PARAMS = [
    'traumatismo', 'herida', 'aumento_trabajo_respiratorio', 'cianosis',
    'palidez', 'hemorragia', 'dolor', 'intoxicacion_auto_dano',
    'convulsiones', 'glasgow', 'deshidratacion', 'psicosis_agitacion_violencia'
]

# Funciones auxiliares para Sección 3
def puntaje_frecuencia_cardiaca(fc):
    if fc < 40: return 10
    elif 40 <= fc <= 59: return 5
    elif 60 <= fc <= 100: return 0
    elif 101 <= fc <= 140: return 5
    else: return 10

def puntaje_temperatura(temp):
    if temp < 34.5: return 10
    elif 34.5 <= temp <= 35.9: return 5
    elif 36 <= temp <= 37: return 0
    elif 37.1 <= temp <= 39: return 5
    else: return 10

def puntaje_frecuencia_respiratoria(fr):
    if fr < 8: return 10
    elif 8 <= fr <= 12: return 5
    elif 13 <= fr <= 18: return 0
    elif 19 <= fr <= 25: return 5
    else: return 10

def puntaje_tension_arterial(tension):
    # espera formato "sistolica/diastolica"
    try:
        s, d = map(int, tension.split('/'))
    except:
        return 0
    if s < 70 or d < 50: return 10
    elif 70 <= s <= 90 or 50 <= d <= 60: return 5
    elif 91 <= s <= 120 or 61 <= d <= 80: return 0
    elif 121 <= s <= 160 or 81 <= d <= 110: return 5
    else: return 10

def puntaje_glucemia(g):
    if g < 40: return 10
    elif 40 <= g <= 70: return 5
    elif 71 <= g <= 140: return 0
    elif 141 <= g <= 400: return 5
    else: return 10

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        form = request.form
        total = 0

        # =========================
        # Sección 1: criterios críticos
        # =========================
        criterios_criticos = []
        if form.get('perdida_estado_alerta'):
            total += 31
            criterios_criticos.append('Pérdida del estado de alerta')
        if form.get('apnea'):
            total += 31
            criterios_criticos.append('Apnea')
        if form.get('ausencia_pulso_fc_menor_40'):
            total += 31
            criterios_criticos.append('Ausencia de pulso / FC<40')
        if form.get('angor_dolor_precordial_toracico'):
            total += 31
            criterios_criticos.append('Angor / dolor torácico')

        # =========================
        # Sección 2: síntomas con puntaje según grado
        # =========================
        detalle_seccion2 = {}
        for p in SECCION2_PARAMS:
            try:
                valor = int(form.get(p, 0))
            except:
                valor = 0
            detalle_seccion2[p] = valor
            total += valor

        # =========================
        # Sección 3: signos vitales
        # =========================
        fc = int(form.get('frecuencia_cardiaca', 0))
        temp = float(form.get('temperatura', 0))
        fr = int(form.get('frecuencia_respiratoria', 0))
        tension = form.get('tension_arterial', '0/0')
        glucemia = int(form.get('glucemia', 0))

        total += puntaje_frecuencia_cardiaca(fc)
        total += puntaje_temperatura(temp)
        total += puntaje_frecuencia_respiratoria(fr)
        total += puntaje_tension_arterial(tension)
        total += puntaje_glucemia(glucemia)

        detalle = {
            'Seccion1': sum([31 for _ in criterios_criticos]),
            'Seccion2': sum(detalle_seccion2.values()),
            'FrecuenciaCardiaca': puntaje_frecuencia_cardiaca(fc),
            'Temperatura': puntaje_temperatura(temp),
            'FrecuenciaRespiratoria': puntaje_frecuencia_respiratoria(fr),
            'TensionArterial': puntaje_tension_arterial(tension),
            'Glucemia': puntaje_glucemia(glucemia)
        }

        # =========================
        # Nivel de emergencia
        # =========================
        if total > 30:
            nivel = 'Nivel 1: reanimación inmediata'
            color = 'danger'
        elif total > 20:
            nivel = 'Nivel 2: emergencias 10 minutos'
            color = 'warning'
        elif total > 10:
            nivel = 'Nivel 3: urgencias hasta 60 minutos'
            color = 'info'
        elif total > 5:
            nivel = 'Nivel 4: urgencia menor hasta 120 minutos'
            color = 'secondary'
        else:
            nivel = 'Nivel 5: sin urgencia hasta 240 minutos'
            color = 'success'

        return render_template(
            'resultado.html',
            total=total,
            nivel=nivel,
            mensaje=nivel,
            color=color,
            detalle=detalle,
            form=form,
            seccion2=SECCION2_PARAMS,
            criterios_criticos=criterios_criticos
        )

    return render_template('index.html', seccion2=SECCION2_PARAMS)


if __name__ == '__main__':
    app.run(debug=True)
