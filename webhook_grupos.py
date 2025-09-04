from flask import Flask, request, jsonify, render_template_string
import threading
from datetime import datetime
import pytesseract
from PIL import Image
import os
import json
from collections import OrderedDict

# Configuración de Tesseract (ajusta la ruta si es necesario)
pytesseract.pytesseract.tesseract_cmd = r'C:/Users/Usuario/Desktop/python/tesseract.exe'
os.environ['TESSDATA_PREFIX'] = r'C:/Users/Usuario/Desktop/python/tessdata'

# Leer grupos desde la imagen al iniciar
GRUPOS_IMG = 'grupos.png'
def leer_grupos_desde_imagen(img_path):
    img = Image.open(img_path)
    texto = pytesseract.image_to_string(img, lang='spa')
    personas = {}
    for linea in texto.split('\n'):
        if not linea.strip():
            continue
        partes = linea.split()
        if len(partes) >= 2:
            nombre = partes[0].strip()
            equipo = partes[1].strip()
            personas[nombre] = equipo
    return personas

personas = {
    # Tiburones
    "Paola Andrea HERNANDEZ": "Tiburones",
    "Guillem SUBILS": "Tiburones",
    "Adria BORRELL": "Tiburones",
    "Carles LOPEZ": "Tiburones",
    "Tomas FAVILLA": "Tiburones",
    "Luz QUIROZ": "Tiburones",
    "Maria Jose SOTO": "Tiburones",
    "Joana PLANAS": "Tiburones",
    "Alex SANCHEZ": "Tiburones",
    "Ferran PUENTE": "Tiburones",
    "Adrian PORTELA": "Tiburones",
    "Agustin GUTIERREZ": "Tiburones",
    "Jordi MOLINE": "Tiburones",
    "Blanca MARTINEZ": "Tiburones",
    "Abril JOFRE": "Tiburones",
    "Eudald BLANCH": "Tiburones",
    "Lesley Caicedo": "Tiburones",
    "Izan SOLER": "Tiburones",
    "Pol PERARNAU": "Tiburones",
    # Elefantes
    "Nerea Castillo": "Elefantes",
    "Arnau COSTA": "Elefantes",
    "Aina FUENTES": "Elefantes",
    "Estell COLLADO": "Elefantes",
    "Gemma MARTI": "Elefantes",
    "Marcos Garcia": "Elefantes",
    "David ORTIZ": "Elefantes",
    "Enric SANTACATALINA": "Elefantes",
    "Marti BAGUE": "Elefantes",
    "Kevin Adrian PESANTES": "Elefantes",
    "Aya": "Elefantes",
    "Paula BASH": "Elefantes",
    "Sandra SOARES": "Elefantes",
    "Manuela VARGAS": "Elefantes",
    "Miriam PEÑA": "Elefantes",
    "Patricia FENOLL": "Elefantes",
    "David MARTINEZ": "Elefantes",
    "Francesc SANZ": "Elefantes",
    # Dragones
    "Visi LOPEZ": "Dragones",
    "Faina VALISHINA": "Dragones",
    "Anna CODINA": "Dragones",
    "Alba CORREAL": "Dragones",
    "Julia CODINA": "Dragones",
    "Said ZAROUALI": "Dragones",
    "Hamza MOUSSATI": "Dragones",
    "Roger BLANCAFORT": "Dragones",
    "Gabriel Fernando SUIN": "Dragones",
    "Guillermo SANCHEZ": "Dragones",
    "Marcel SALES": "Dragones",
    "Margarita MARIN": "Dragones",
    "Imane EL HARACHI": "Dragones",
    "Joan CASTRO": "Dragones",
    "Gabriel MORERA": "Dragones",
    "Anna MORELL": "Dragones",
    "Judit FRIGOLA": "Dragones",
    "Esperanza Maria MUNTADAS": "Dragones",
    # Escorpiones
    "Jota ZAMORA": "Escorpiones",
    "Natalia MANCUSO": "Escorpiones",
    "Miguel LOPEZ": "Escorpiones",
    "Carme LOBATO": "Escorpiones",
    "Enrique GOMEZ": "Escorpiones",
    "Julia JIMENEZ": "Escorpiones",
    "Joel LOPEZ": "Escorpiones",
    "Roc CAMPS": "Escorpiones",
    "Mar Roura": "Escorpiones",
    "Nill OLLER": "Escorpiones",
    "JORDI MAYO": "Escorpiones",
    "Marc SANCHEZ": "Escorpiones",
    "Carme PELAEZ": "Escorpiones",
    "Arnau LOPEZ": "Escorpiones",
    "Álvaro Jiménez": "Escorpiones",
    "Francisco FERNÁNDEZ": "Escorpiones",
    "Basma BACHIRI": "Escorpiones",
    "Adam AABACHRIM": "Escorpiones"
}

# Cargar puntos desde archivo si existe
PUNTOS_FILE = "puntos.json"
def cargar_puntos():
    if os.path.exists(PUNTOS_FILE):
        with open(PUNTOS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return {equipo: 0 for equipo in set(personas.values())}

def guardar_puntos():
    with open(PUNTOS_FILE, "w", encoding="utf-8") as f:
        json.dump(puntos, f, ensure_ascii=False, indent=2)

puntos = cargar_puntos()

# Cargar puntos mp desde archivo si existe
PUNTOS_MP_FILE = "puntos_mp.json"
def cargar_puntos_mp():
    if os.path.exists(PUNTOS_MP_FILE):
        with open(PUNTOS_MP_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return {equipo: 0 for equipo in set(personas.values())}

def guardar_puntos_mp():
    with open(PUNTOS_MP_FILE, "w", encoding="utf-8") as f:
        json.dump(puntos_mp, f, ensure_ascii=False, indent=2)

puntos_mp = cargar_puntos_mp()

# Ordenar los grupos para que siempre aparezcan igual
orden_grupos = ["Tiburones", "Elefantes", "Dragones", "Escorpiones"]
def ordenar_diccionario(dic):
    return OrderedDict((g, dic.get(g, 0)) for g in orden_grupos)

puntos = ordenar_diccionario(puntos)
puntos_mp = ordenar_diccionario(puntos_mp)

def personas_ordenadas(grupo):
    destacados = {
        "Tiburones": "Paola Hernandez",
        "Elefantes": "Nerea Castillo",
        "Dragones": "Visi Lopez",
        "Escorpiones": "Jota Zamora"
    }
    # Poner el destacado primero y el resto después
    miembros = [p for p, g in personas.items() if g == grupo]
    primero = destacados.get(grupo)
    if primero in miembros:
        miembros.remove(primero)
        return [primero] + miembros
    return miembros

template = '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Marcador de Grupos</title>
    <meta http-equiv="refresh" content="60">
    <style>
        body { font-family: Arial, sans-serif; background: #f4f4f4; }
        body::before {
            content: "";
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: url('/static/fotos/decathlon2.jpg') no-repeat center center fixed;
            background-size: cover;
            opacity: 0.45;
            z-index: -1;
        }
        .container { max-width: 1200px; margin: 40px auto; background: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px #ccc; }
        .grupos-flex { display: flex; flex-wrap: wrap; justify-content: space-around; }
        .grupo { flex: 1 1 250px; min-width: 250px; max-width: 300px; margin: 10px; background: #e9f5ff; border-radius: 8px; padding: 15px; box-shadow: 0 0 5px #bbb; position: relative; }
        .grupo-lider { border: 3px solid gold; box-shadow: 0 0 18px #ffd700; }
        .grupo-nombre { font-size: 1.3em; color: #333; margin-bottom: 5px; text-align: center; display: flex; align-items: center; justify-content: center; gap: 8px; }
        .grupo-logo { width: 36px; height: 36px; object-fit: contain; border-radius: 50%; background: #fff; border: 1px solid #ccc; margin-right: 4px; }
        .personas { margin-left: 10px; color: #555; text-align: left; }
        .destacado { font-size: 1.15em; font-weight: bold; color: #1a237e; }
        .separador { border-top: 2px solid #aaa; margin: 30px 0 20px 0; }
        .splash { display: flex; align-items: center; justify-content: center; height: 90vh; }
        .splash img { max-width: 80vw; max-height: 80vh; border-radius: 16px; box-shadow: 0 0 20px #888; }
        @media (max-width: 900px) {
            .container { max-width: 98vw; padding: 6px; }
            .grupos-flex { flex-direction: column; align-items: center; }
            .grupo { max-width: 98vw; min-width: 220px; }
        }
        @media (max-width: 600px) {
            .grupo-nombre { font-size: 1.1em; }
            .grupo-logo { width: 28px; height: 28px; }
        }
    </style>
    <script>
        function hideSplash() {
            document.getElementById('splash').style.display = 'none';
            document.getElementById('main-content').style.display = 'block';
            // Guardar en localStorage que ya se mostró el splash
            localStorage.setItem('splashShown', '1');
        }
        window.onload = function() {
            // Solo mostrar splash si no se ha mostrado en este navegador
            if (!localStorage.getItem('splashShown')) {
                setTimeout(hideSplash, 3000);
            } else {
                hideSplash();
            }
        };
    </script>
</head>
<body>
    <div id="splash" class="splash">
        <img src="/static/fotos/decathlon1.jpg" alt="Decathlon" />
    </div>
    <div id="main-content" style="display:none;">
        <div class="container">
            <div style="width:100%; display:flex; flex-direction:row; align-items:center; justify-content:space-between; margin-bottom: 18px; gap: 0;">
                <div style="flex:0 0 auto; display:flex; align-items:center;">
                    <img src="/static/fotos/decathlon3.jpg" alt="Decathlon 3" style="width: 220px; max-width: 40vw; height: auto; border-radius: 18px; box-shadow: 0 4px 18px #888; background: #fff; padding: 6px; margin-right: 0;">
                </div>
                <div style="flex:1 1 0; display:flex; flex-direction:column; align-items:center; justify-content:center; min-width:0;">
                    <h1 style="font-size:2.3em; color:#0d47a1; margin-bottom: 8px; margin-top: 0; text-align:center; width:100%;">Decathlon Girona</h1>
                    <div style="font-size:1.05em; color:#fff; background:#0d47a1; display:inline-block; padding:5px 14px; border-radius:14px; font-weight:bold; box-shadow:0 2px 8px #888; text-align:center; max-width:320px; width:auto;">4 equipos, 1 solo objetivo</div>
                </div>
                <div style="flex:0 0 auto; display:flex; align-items:flex-start; padding-top:8px;">
                    <div style="font-size: 1.05em; color: #0d47a1; background: #fff; padding: 5px 14px; border-radius: 0 0 0 14px; font-weight: bold; box-shadow: 0 2px 8px #bbb; white-space:nowrap;">Del 01/09 al 31/12</div>
                </div>
            </div>
            <div style="text-align:center; margin-bottom: 22px;">
                <div style="display:inline-block; background:#fff; color:#0d47a1; border-radius:14px; padding:14px 24px; box-shadow:0 1px 6px #bbb; max-width:600px;">
                    <div style="font-size:1.2em; font-weight:bold; margin-bottom:6px;">¿Qué es el Ranking DIS?</div>
                    <div style="font-size:1em;">
                        Es una competencia en la que formarás parte de un equipo compuesto por colaboradores de distintos universos, unidos por un animal.<br>
                        ¡Sé el mejor y defiende el animal de tu equipo! Al final, habrá recompensa para los ganadores.
                    </div>
                </div>
            </div>
            <div class="grupos-flex">
            {% set max_puntos = puntos.values()|max %}
            {% for grupo, punto in puntos.items() %}
                <div class="grupo{% if punto == max_puntos and punto > 0 %} grupo-lider{% endif %}">
                    <div class="grupo-nombre">
                        <img class="grupo-logo" src="/static/logos/{{ grupo|lower }}.png" alt="Logo {{ grupo }}" onerror="this.onerror=null;this.src='/static/logos/{{ grupo|lower }}.jpg';this.onerror=function(){this.src='/static/logos/{{ grupo|lower }}.jpeg';this.onerror=null;};this.style.display='inline-block'">
                        <b>{{ grupo }}:</b> {{ punto }}
                        {% if punto == max_puntos and punto > 0 %}
                            <span title="Líder" style="margin-left:6px; color:gold; font-size:1.2em;">&#x1F451;</span>
                        {% endif %}
                    </div>
                    <div class="personas">
                        {% set miembros = personas_ordenadas(grupo) %}
                        {% for persona in miembros %}
                            {% if persona == 'Adam AABACHRIM' %}
                                {% set nombre_formateado = 'Adam Aabachrim' %}
                            {% else %}
                                {% set partes = persona.split() %}
                                {% set nombre_formateado = partes | map('lower') | map('capitalize') | join(' ') %}
                            {% endif %}
                            {% if loop.index0 == 0 %}
                                <span class="destacado">{{ nombre_formateado }}</span><br>
                            {% else %}
                                {{ nombre_formateado }}<br>
                            {% endif %}
                        {% endfor %}
                    </div>
                </div>
            {% endfor %}
            </div>
            <div class="separador"></div>
            <h2>MARKET PLACE</h2>
            <div style="text-align:center; margin-bottom: 16px;">
                <span style="font-size:1.15em; color:#0d47a1; background:#fff; display:inline-block; padding:6px 18px; border-radius:14px; font-weight:bold; box-shadow:0 1px 4px #bbb;">Nuestro objetivo: ser número uno de Market Place en tiendas Decathlon España.</span>
            </div>
            <div class="grupos-flex">
            {% set max_puntos_mp = puntos_mp.values()|max %}
            {% for grupo, punto in puntos_mp.items() %}
                <div class="grupo{% if punto == max_puntos_mp and punto > 0 %} grupo-lider{% endif %}">
                    <div class="grupo-nombre">
                        <img class="grupo-logo" src="/static/logos/{{ grupo|lower }}.png" alt="Logo {{ grupo }}" onerror="this.onerror=null;this.src='/static/logos/{{ grupo|lower }}.jpg';this.onerror=function(){this.src='/static/logos/{{ grupo|lower }}.jpeg';this.onerror=null;};this.style.display='inline-block'">
                        <b>{{ grupo }}:</b> {{ punto }}
                        {% if punto == max_puntos_mp and punto > 0 %}
                            <span title="Líder" style="margin-left:6px; color:gold; font-size:1.2em;">&#x1F451;</span>
                        {% endif %}
                    </div>
                </div>
            {% endfor %}
            </div>
            <p style="text-align:center;color:#888;">Actualiza cada 60 segundos</p>
        </div>
    </div>
</body>
</html>
'''

app = Flask(__name__)

@app.route("/")
def index():
    return render_template_string(template, puntos=puntos, personas=personas, puntos_mp=puntos_mp, personas_ordenadas=personas_ordenadas)

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    user_name = data.get("user", {}).get("displayName", "")
    text = data.get("text", "")
    respuesta = "Mensaje recibido."
    # Solo sumar puntos si la fecha es igual o posterior al 01/09
    hoy = datetime.now()
    inicio = datetime(hoy.year, 9, 1)
    if hoy < inicio:
        respuesta = "La competición empieza el 01/09. Los puntos aún no se pueden sumar."
    else:
        # Permitir coincidencia parcial de '+1' y '+1 mp' en cualquier parte del texto
        if "+1 mp" in text.lower() and user_name in personas:
            equipo = personas[user_name]
            puntos_mp[equipo] += 1
            guardar_puntos_mp()
            respuesta = f"¡Punto MP para {equipo}! Total: {puntos_mp[equipo]}"
        elif "+1" in text.lower() and user_name in personas:
            equipo = personas[user_name]
            puntos[equipo] += 1
            guardar_puntos()
            respuesta = f"¡Punto para {equipo}! Total: {puntos[equipo]}"
    return jsonify({"text": respuesta})

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)