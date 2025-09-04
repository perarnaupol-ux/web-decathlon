from flask import Flask, request, jsonify, render_template_string
import threading
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
    "Guillem Subils": "Tiburones",
    "Adria Borrell": "Tiburones",
    "Carles Lopez": "Tiburones",
    "Tomas Favilla": "Tiburones",
    "Luz Quiroz": "Tiburones",
    "Maria jose soto": "Tiburones",
    "Joana Planas": "Tiburones",
    "Alex Sanchez": "Tiburones",
    "Ferran puente": "Tiburones",
    "Adrian Portela": "Tiburones",
    "Agustin gutierrez": "Tiburones",
    "Jordi Moline": "Tiburones",
    "Blanca martinez": "Tiburones",
    "Abril Jofre": "Tiburones",
    "Eudald Blanch": "Tiburones",
    "Lesley Caicedo": "Tiburones",
    "Izan soler": "Tiburones",
    "Pol Perarnau": "Tiburones",
    "Paola Hernandez": "Tiburones",
    # Elefantes
    "Arnau costa": "Elefantes",
    "Aina Fuentes": "Elefantes",
    "Estell Collado": "Elefantes",
    "Gemma marti": "Elefantes",
    "Marcos Garcia": "Elefantes",
    "David Ortiz": "Elefantes",
    "Enric Santacatalina": "Elefantes",
    "Marti Bague": "Elefantes",
    "Kevin Adrian": "Elefantes",
    "Aya": "Elefantes",
    "Paula Bash": "Elefantes",
    "Sandra Soares": "Elefantes",
    "Manuela Vargas": "Elefantes",
    "Miriam Peña": "Elefantes",
    "Patricia Fenoll": "Elefantes",
    "David Martinez": "Elefantes",
    "Francesc Sanz": "Elefantes",
    "Nerea Castillo": "Elefantes",
    # Dragones
    "Faina valishina": "Dragones",
    "Anna Codina": "Dragones",
    "Alba correal": "Dragones",
    "Julia Codina": "Dragones",
    "Said Zarouali": "Dragones",
    "Hamza Moussati": "Dragones",
    "Roger Blancafort": "Dragones",
    "Gabriel Fernando Suin": "Dragones",
    "Guillermo Sanchez": "Dragones",
    "Marcel Sales": "Dragones",
    "Margarita marin": "Dragones",
    "Imane el Harachi": "Dragones",
    "Joan Castro": "Dragones",
    "Gabriel Morera": "Dragones",
    "Anna Morell": "Dragones",
    "Judit Frigola": "Dragones",
    "Esperanza Maria Muntadas": "Dragones",
    "Visi Lopez": "Dragones",
    # Escorpiones
    "Jota Zamora": "Escorpiones",
    "Natalia Mancuso": "Escorpiones",
    "Miguel Lopez": "Escorpiones",
    "Carme Lobato": "Escorpiones",
    "Enrique gomez": "Escorpiones",
    "Julia Jimenez": "Escorpiones",
    "Joel Lopez": "Escorpiones",
    "Roc Camps": "Escorpiones",
    "Mar Roura": "Escorpiones",
    "Nill Oller": "Escorpiones",
    "Jordi mayo": "Escorpiones",
    "Marc sanchez": "Escorpiones",
    "Carme pelaez": "Escorpiones",
    "Arnau lopez": "Escorpiones",
    "Alvaro Jimenez": "Escorpiones",
    "Francisco Fermandez": "Escorpiones",
    "Basma Bachiri": "Escorpiones",
    "Adam Khali": "Escorpiones"
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
    <meta http-equiv="refresh" content="20">
    <style>
        body { font-family: Arial, sans-serif; background: #f4f4f4; }
        .container { max-width: 1200px; margin: 40px auto; background: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px #ccc; }
        h2 { text-align: center; }
        .grupos-flex { display: flex; flex-wrap: wrap; justify-content: space-around; }
        .grupo { flex: 1 1 250px; min-width: 250px; max-width: 300px; margin: 10px; background: #e9f5ff; border-radius: 8px; padding: 15px; box-shadow: 0 0 5px #bbb; }
        .grupo-nombre { font-size: 1.3em; color: #333; margin-bottom: 5px; text-align: center; }
        .personas { margin-left: 10px; color: #555; text-align: left; }
        .destacado { font-size: 1.15em; font-weight: bold; color: #1a237e; }
        .separador { border-top: 2px solid #aaa; margin: 30px 0 20px 0; }
    </style>
</head>
<body>
    <div class="container">
        <h2>Marcador de Grupos</h2>
        <div class="grupos-flex">
        {% for grupo, punto in puntos.items() %}
            <div class="grupo">
                <div class="grupo-nombre"><b>{{ grupo }}:</b> {{ punto }}</div>
                <div class="personas">
                    {% set miembros = personas_ordenadas(grupo) %}
                    {% for persona in miembros %}
                        {% if loop.index0 == 0 %}
                            <span class="destacado">{{ persona }}</span><br>
                        {% else %}
                            {{ persona }}<br>
                        {% endif %}
                    {% endfor %}
                </div>
            </div>
        {% endfor %}
        </div>
        <div class="separador"></div>
        <h2>MARKET PLACE</h2>
        <div class="grupos-flex">
        {% for grupo, punto in puntos_mp.items() %}
            <div class="grupo">
                <div class="grupo-nombre"><b>{{ grupo }}:</b> {{ punto }}</div>
            </div>
        {% endfor %}
        </div>
        <p style="text-align:center;color:#888;">Actualiza cada 20 segundos</p>
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
    if "+1 mp" in text and user_name in personas:
        equipo = personas[user_name]
        puntos_mp[equipo] += 1
        guardar_puntos_mp()
        respuesta = f"¡Punto MP para {equipo}! Total: {puntos_mp[equipo]}"
    elif "+1" in text and user_name in personas:
        equipo = personas[user_name]
        puntos[equipo] += 1
        guardar_puntos()
        respuesta = f"¡Punto para {equipo}! Total: {puntos[equipo]}"
    return jsonify({"text": respuesta})

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)