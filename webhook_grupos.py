from flask import Flask, request, jsonify, render_template_string, abort
import threading
import unicodedata
from datetime import datetime
import pytesseract
from PIL import Image
import os
import json
from collections import OrderedDict

app = Flask(__name__)

import threading
import unicodedata
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
    "paolaandrea.hernandez@decathlon.com": "Tiburones",
    "guillem.subils@decathlon.com": "Tiburones",
    "adria.borrell@decathlon.com": "Tiburones",
    "carles.lopez@decathlon.com": "Tiburones",
    "tomas.favilla@decathlon.com": "Tiburones",
    "luzmaria.quiroz@decathlon.com": "Tiburones",
    "maria.soto@decathlon.com": "Tiburones",
    "joana.planas@decathlon.com": "Tiburones",
    "alex.sanchez@decathlon.com": "Tiburones",
    "ferran.puente@decathlon.com": "Tiburones",
    "adrian.portela@decathlon.com": "Tiburones",
    "agustin.gutierrez@decathlon.com": "Tiburones",
    "jordi.moline@decathlon.com": "Tiburones",
    "blanca.martinez@decathlon.com": "Tiburones",
    "abril.jofre@decathlon.com": "Tiburones",
    "eudald.blanch@decathlon.com": "Tiburones",
    "lesley.caicedo@decathlon.com": "Tiburones",
    "izan.soler@decathlon.com": "Tiburones",
    "pol.perarnau@decathlon.com": "Tiburones",
    # Elefantes
    "nerea.castillo@decathlon.com": "Elefantes",
    "arnau.costa@decathlon.com": "Elefantes",
    "marcos.garcia2@decathlon.com": "Elefantes",
    "david.ortiz@decathlon.com": "Elefantes",
    "enric.santacatalina@decathlon.com": "Elefantes",
    "marti.bague@decathlon.com": "Elefantes",
    "kevinadrian.pesantes@decathlon.com": "Elefantes",
    "paula.bachs@decathlon.com": "Elefantes",
    "sandra.soares@decathlon.com": "Elefantes",
    "manuela.vargas@decathlon.com": "Elefantes",
    "miriam.peña@decathlon.com": "Elefantes",
    "patricia.fenoll@decathlon.com": "Elefantes",
    "david.martinez@decathlon.com": "Elefantes",
    "francesc.sanz@decathlon.com": "Elefantes",
    "carlos.riquleme@decathlon.com": "Elefantes",
    "carme.pelaez@decathlon.com": "Elefantes",
    "aina.fuentes@decathlon.com": "Elefantes",
    # Dragones
    "visitacion.lopez@decathlon.com": "Dragones",
    "faina.valishina@decathlon.com": "Dragones",
    "anna.codina@decathlon.com": "Dragones",
    "alba.correal@decathlon.com": "Dragones",
    "julia.codina@decathlon.com": "Dragones",
    "said.zarouali@decathlon.com": "Dragones",
    "hamza.moussati@decathlon.com": "Dragones",
    "gabrielfernandu.suin@decathlon.com": "Dragones",
    "guillermo.sanchez@decathlon.com": "Dragones",
    "marcel.sales@decathlon.com": "Dragones",
    "margarita.marin@decathlon.com": "Dragones",
    "imane.elharachi@decathlon.com": "Dragones",
    "joan.castro@decathlon.com": "Dragones",
    "gabriel.morera@decathlon.com": "Dragones",
    "anna.morell@decathlon.com": "Dragones",
    "judit.frigola@decathlon.com": "Dragones",
    "esperanza.muntadas@decathlon.com": "Dragones",
    # Escorpiones
    "joanjosep.delapena@decathlon.com": "Escorpiones",
    "natalia.mancuso@decathlon.com": "Escorpiones",
    "carme.lobato@decathlon.com": "Escorpiones",
    "enrique.gomez@decathlon.com": "Escorpiones",
    "julia.jimenez@decathlon.com": "Escorpiones",
    "joel.lopez@decathlon.com": "Escorpiones",
    "mar.roura@decathlon.com": "Escorpiones",
    "jordi.mayo@decathlon.com": "Escorpiones",
    "marc.sanchez@decathlon.com": "Escorpiones",
    "arnau.lopez@decathlon.com": "Escorpiones",
    "alvaro.jimenez@decathlon.com": "Escorpiones",
    "francisco.fernandez@decathlon.com": "Escorpiones",
    "basma.bachiri@decathlon.com": "Escorpiones",
    "adam.aabachrim@decathlon.com": "Escorpiones"
}

# Diccionario auxiliar: correo -> nombre (generado automáticamente)
correos_a_nombres = {}
for correo in personas:
    partes = correo.split('@')[0].replace('.', ' ').split()
    nombre = ' '.join([p.capitalize() for p in partes])
    correos_a_nombres[correo] = nombre
# Corrección manual para Carlos Riquelme
correos_a_nombres["carlos.riquelme@decathlon.com"] = "Carlos Riquelme"

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
        "Tiburones": "paolaandrea.hernandez@decathlon.com",
        "Elefantes": "nerea.castillo@decathlon.com",
        "Dragones": "visitacion.lopez@decathlon.com",
        "Escorpiones": "joanjosep.delapena@decathlon.com"
    }
    miembros = [correo for correo, g in personas.items() if g == grupo]
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
            // Mostrar la sección de mejor vendedor después del splash
            var mejorVendedor = document.getElementById('mejor-vendedor');
            if(mejorVendedor) mejorVendedor.style.display = 'block';
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
            <div style="display:flex; justify-content:center; align-items:stretch; margin-bottom:22px; gap:18px;">
        <!-- MODAL DE COMENTARIOS -->
        <div id="comentarios-modal" style="display:none; position:fixed; top:0; left:0; width:100vw; height:100vh; background:rgba(0,0,0,0.35); z-index:3000; align-items:center; justify-content:center;">
            <div style="background:#fff; border-radius:18px; box-shadow:0 4px 24px #888; padding:40px 38px; min-width:400px; max-width:600px; width:90vw; max-height:90vh; overflow:auto; position:relative;">
                <span id="comentarios-modal-close" style="position:absolute; top:12px; right:18px; font-size:1.7em; color:#888; cursor:pointer;">&times;</span>
                <form id="comentario-form">
                    <div style="font-size:1.2em; color:#0d47a1; font-weight:bold; margin-bottom:12px;">Deja tu comentario</div>
                    <input id="comentario-nombre" type="text" placeholder="Tu nombre" style="width:100%; margin-bottom:10px; padding:8px; border-radius:6px; border:1px solid #bbb; font-size:1em;" required><br>
                    <textarea id="comentario-texto" placeholder="Escribe tu comentario..." style="width:100%; min-height:80px; margin-bottom:10px; padding:8px; border-radius:6px; border:1px solid #bbb; font-size:1em;" required></textarea><br>
                    <button type="button" id="comentario-enviar" style="background:#0d47a1; color:#fff; border:none; border-radius:8px; padding:10px 24px; font-weight:bold; cursor:pointer;">Enviar</button>
                    <div id="comentario-exito" style="display:none; color:green; margin-top:10px;">¡Comentario enviado!</div>
                </form>
            </div>
        </div>
                <div style="display:inline-block; background:#fff; color:#0d47a1; border-radius:14px; padding:14px 24px; box-shadow:0 1px 6px #bbb; max-width:600px; flex:1;">
                    <div style="font-size:1.2em; font-weight:bold; margin-bottom:6px;">¿Qué es el Ranking DIS?</div>
                    <div style="font-size:1em;">
                        Es una competencia en la que formarás parte de un equipo compuesto por colaboradores de distintos universos, unidos por un animal.<br>
                        ¡Sé el mejor y defiende el animal de tu equipo! Al final, habrá recompensa para los ganadores.
                    </div>
                </div>
                <div style="position:relative; display:flex; flex-direction:column; align-items:end; margin-left:auto; gap:10px;">
                    <div style="display:flex; gap:10px; align-items:end;">
                        <div id="equipos-btn" style="background:#0d47a1; color:#fff; border-radius:12px; padding:12px 24px; font-weight:bold; cursor:pointer; box-shadow:0 1px 6px #bbb; user-select:none; transition:background 0.2s;">Equipos</div>
                        <button id="comentarios-btn" style="background:#fff; color:#0d47a1; border:2px solid #0d47a1; border-radius:12px; padding:10px 22px; font-weight:bold; cursor:pointer; box-shadow:0 1px 6px #bbb;">Comentarios</button>
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
                        {% for correo in miembros %}
                            {% set nombre = correos_a_nombres.get(correo, correo) %}
                            {% if loop.index0 == 0 %}
                                <span class="destacado">{{ nombre }}</span><br>
                            {% else %}
                                {{ nombre }}<br>
                            {% endif %}
                        {% endfor %}
                    </div>
                </div>
            {% endfor %}
            </div>
            <div class="separador"></div>
            <h2 style="background:#fff; display:inline-block; padding:10px 32px; border-radius:14px; box-shadow:0 1px 6px #bbb; color:#0d47a1; font-weight:bold; margin-bottom:18px;">MARKET PLACE</h2>
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
        <!-- NUEVO: Mejor Vendedor de la semana (dentro de main-content) -->
        </div> <!-- Cierre de main-content -->

<!-- Nueva sección de equipos tipo página interna (fuera de main-content) -->
<div id="equipos-page" style="display:none; position:fixed; top:0; left:0; width:100vw; height:100vh; background:#f8fafc; z-index:2000; overflow:auto;">
    <div style="max-width:1200px; margin:40px auto; background:#fff; border-radius:18px; box-shadow:0 4px 24px #888; padding:32px 28px;">
        <button id="equipos-volver" style="background:#0d47a1; color:#fff; border:none; border-radius:8px; padding:10px 24px; font-weight:bold; margin-bottom:18px; cursor:pointer;">&larr; Volver</button>
        <h2 style="color:#0d47a1; text-align:center; font-size:2em; margin-bottom:18px; letter-spacing:1px;">Equipos</h2>
        <div class="grupos-flex">
        {% set max_puntos = puntos.values()|max %}
        {% for grupo, punto in puntos.items() %}
            <div class="grupo{% if punto == max_puntos and punto > 0 %} grupo-lider{% endif %}">
                <div class="grupo-nombre">
                    <img class="grupo-logo" src="/static/logos/{{ grupo|lower }}.png" alt="Logo {{ grupo }}" onerror="this.onerror=null;this.src='/static/logos/{{ grupo|lower }}.jpg';this.onerror=function(){this.src='/static/logos/{{ grupo|lower }}.jpeg';this.onerror=null;};this.style.display='inline-block'">
                    <b>{{ grupo }}</b>
                </div>
                <div class="personas">
                    {% set miembros = personas_ordenadas(grupo) %}
                    {% for correo in miembros %}
                        {% set nombre = correos_a_nombres.get(correo, correo) %}
                        {% if loop.index0 == 0 %}
                            <span class="destacado">{{ nombre }}</span><br>
                        {% else %}
                            {{ nombre }}<br>
                        {% endif %}
                    {% endfor %}
                </div>
            </div>
        {% endfor %}
        </div>
    </div>
</div>


<!-- ÚNICA sección de equipos tipo página interna (fuera de main-content) -->
<div id="equipos-page" style="display:none; position:fixed; top:0; left:0; width:100vw; height:100vh; background:#f8fafc; z-index:2000; overflow:auto;">
    <div style="max-width:1200px; margin:40px auto; background:#fff; border-radius:18px; box-shadow:0 4px 24px #888; padding:32px 28px;">
        <button id="equipos-volver" style="background:#0d47a1; color:#fff; border:none; border-radius:8px; padding:10px 24px; font-weight:bold; margin-bottom:18px; cursor:pointer;">&larr; Volver</button>
        <h2 style="color:#0d47a1; text-align:center; font-size:2em; margin-bottom:18px; letter-spacing:1px;">Equipos</h2>
        <div class="grupos-flex">
        {% set max_puntos = puntos.values()|max %}
        {% for grupo, punto in puntos.items() %}
            <div class="grupo{% if punto == max_puntos and punto > 0 %} grupo-lider{% endif %}">
                <div class="grupo-nombre">
                    <img class="grupo-logo" src="/static/logos/{{ grupo|lower }}.png" alt="Logo {{ grupo }}" onerror="this.onerror=null;this.src='/static/logos/{{ grupo|lower }}.jpg';this.onerror=function(){this.src='/static/logos/{{ grupo|lower }}.jpeg';this.onerror=null;};this.style.display='inline-block'">
                    <b>{{ grupo }}</b>
                </div>
                <div class="personas">
                    {% set miembros = personas_ordenadas(grupo) %}
                    {% for correo in miembros %}
                        {% set nombre = correos_a_nombres.get(correo, correo) %}
                        {% if loop.index0 == 0 %}
                            <span class="destacado">{{ nombre }}</span><br>
                        {% else %}
                            {{ nombre }}<br>
                        {% endif %}
                    {% endfor %}
                </div>
            </div>
        {% endfor %}
        </div>
    </div>
</div>
    <!-- Título fuera del recuadro blanco -->
<!-- Recuadro blanco unificado para el título y el ranking -->
<div id="mejor-vendedor" class="container" style="max-width: 700px; margin: 0 auto; margin-top: 30px; margin-bottom: 30px; background: #f8fafc; border-radius: 16px; box-shadow: 0 2px 12px #cce; padding: 28px 18px;">
    <h2 style="color:#0d47a1; text-align:center; font-size:2em; margin-top:0; margin-bottom:38px; letter-spacing:1px;">🏆 Mejor Vendedor de la semana</h2>
    {% set puntos_individuales = {} %}
    {% for correo, grupo in personas.items() %}
        {% set _ = puntos_individuales.update({correo: puntos_mp.get(grupo, 0) + puntos.get(grupo, 0)}) %}
    {% endfor %}
    {% set top3 = puntos_individuales.items()|sort(attribute=1, reverse=True) %}
    <div style="display:flex; justify-content:center; gap:32px; align-items:flex-end;">
        {% for correo, puntos_total in top3[:3] %}
            {% set nombre = correos_a_nombres.get(correo, correo) %}
            <div style="background:#fff; border-radius:16px; box-shadow:0 2px 10px #bbb; padding:18px 24px; min-width:160px; text-align:center; position:relative;">
                {% if loop.index == 1 %}
                    <div style="font-size:2.2em; color:gold; position:absolute; top:-32px; left:50%; transform:translateX(-50%);">🥇</div>
                {% elif loop.index == 2 %}
                    <div style="font-size:2em; color:#b0b0b0; position:absolute; top:-28px; left:50%; transform:translateX(-50%);">🥈</div>
                {% elif loop.index == 3 %}
                    <div style="font-size:1.8em; color:#cd7f32; position:absolute; top:-24px; left:50%; transform:translateX(-50%);">🥉</div>
                {% endif %}
                <div style="font-size:1.25em; font-weight:bold; color:#0d47a1; margin-bottom:8px;">{{ nombre }}</div>
                <div style="font-size:1.1em; color:#444;">Puntos: <b>{{ puntos_total }}</b></div>
                <div style="font-size:0.95em; color:#888; margin-top:6px;">{{ personas.get(correo, correo) }}</div>
            </div>
        {% endfor %}
    </div>
</div>

<!-- Nueva sección de equipos tipo página interna (fuera de main-content) -->
<div id="equipos-page" style="display:none; position:fixed; top:0; left:0; width:100vw; height:100vh; background:#f8fafc; z-index:2000; overflow:auto;">
    <div style="max-width:1200px; margin:40px auto; background:#fff; border-radius:18px; box-shadow:0 4px 24px #888; padding:32px 28px;">
        <button id="equipos-volver" style="background:#0d47a1; color:#fff; border:none; border-radius:8px; padding:10px 24px; font-weight:bold; margin-bottom:18px; cursor:pointer;">&larr; Volver</button>
        <h2 style="color:#0d47a1; text-align:center; font-size:2em; margin-bottom:18px; letter-spacing:1px;">Equipos</h2>
        <div class="grupos-flex">
        {% set max_puntos = puntos.values()|max %}
        {% for grupo, punto in puntos.items() %}
            <div class="grupo{% if punto == max_puntos and punto > 0 %} grupo-lider{% endif %}">
                <div class="grupo-nombre">
                    <img class="grupo-logo" src="/static/logos/{{ grupo|lower }}.png" alt="Logo {{ grupo }}" onerror="this.onerror=null;this.src='/static/logos/{{ grupo|lower }}.jpg';this.onerror=function(){this.src='/static/logos/{{ grupo|lower }}.jpeg';this.onerror=null;};this.style.display='inline-block'">
                    <b>{{ grupo }}</b>
                </div>
                <div class="personas">
                    {% set miembros = personas_ordenadas(grupo) %}
                    {% for correo in miembros %}
                        {% set nombre = correos_a_nombres.get(correo, correo) %}
                        {% if loop.index0 == 0 %}
                            <span class="destacado">{{ nombre }}</span><br>
                        {% else %}
                            {{ nombre }}<br>
                        {% endif %}
                    {% endfor %}
                </div>
            </div>
        {% endfor %}
        </div>
    </div>
</div>
    </div>
    <script>
        // Comentarios modal
        document.addEventListener('DOMContentLoaded', function() {
            const comentariosBtn = document.getElementById('comentarios-btn');
            const comentariosModal = document.getElementById('comentarios-modal');
            const comentariosModalClose = document.getElementById('comentarios-modal-close');
            const comentarioForm = document.getElementById('comentario-form');
            const comentarioExito = document.getElementById('comentario-exito');
            const comentarioEnviar = document.getElementById('comentario-enviar');
            if(comentariosBtn) comentariosBtn.onclick = () => { comentariosModal.style.display = 'flex'; };
            if(comentariosModalClose) comentariosModalClose.onclick = () => { comentariosModal.style.display = 'none'; };
            if(comentariosModal) comentariosModal.onclick = (e) => { if(e.target === comentariosModal) comentariosModal.style.display = 'none'; };
            if(comentarioEnviar) comentarioEnviar.onclick = function(e) {
                const nombre = document.getElementById('comentario-nombre').value;
                const comentario = document.getElementById('comentario-texto').value;
                if (!nombre.trim() || !comentario.trim()) return;
                fetch('/comentario', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ nombre, comentario })
                }).then(r => r.json()).then(data => {
                    if(data.ok) {
                        comentarioExito.style.display = 'block';
                        comentarioForm.reset();
                        setTimeout(()=>{comentariosModal.style.display='none'; comentarioExito.style.display='none';}, 1500);
                    }
                });
            };
            // Nueva lógica para equipos como página interna
            const equiposBtn = document.getElementById('equipos-btn');
            const equiposPage = document.getElementById('equipos-page');
            const mainContent = document.getElementById('main-content');
            const equiposVolver = document.getElementById('equipos-volver');
            if(equiposBtn && equiposPage && mainContent) {
                equiposBtn.onclick = function() {
                    mainContent.style.display = 'none';
                    equiposPage.style.display = 'block';
                };
            }
            if(equiposVolver && equiposPage && mainContent) {
                equiposVolver.onclick = function() {
                    equiposPage.style.display = 'none';
                    mainContent.style.display = 'block';
                };
            }
        });
</script>
</body>
</html>
'''

app = Flask(__name__)

@app.route("/")
def index():
    return render_template_string(template, puntos=puntos, personas=personas, puntos_mp=puntos_mp, personas_ordenadas=personas_ordenadas, correos_a_nombres=correos_a_nombres)

@app.route("/webhook", methods=["POST"])

def normalizar(texto):
    return ''.join(c for c in unicodedata.normalize('NFD', texto.lower()) if unicodedata.category(c) != 'Mn')

def buscar_persona(user_email):
    # El email ya viene en minúsculas, pero aseguramos
    user_email = user_email.strip().lower()
    if user_email in personas:
        return user_email
    return None

def webhook():
    data = request.json
    print('Webhook recibido:', data)  # <-- Esto mostrará el JSON recibido en la consola
    user_email = data.get("user", {}).get("email", "")
    text = data.get("text", "")
    print(f"Email recibido: {user_email}")
    print(f"Texto recibido: {text}")
    respuesta = "Mensaje recibido."
    hoy = datetime.now()
    inicio = datetime(hoy.year, 9, 1)
    persona_encontrada = buscar_persona(user_email)
    print(f"Persona encontrada: {persona_encontrada}")
    if hoy < inicio:
        respuesta = "La competición empieza el 01/09. Los puntos aún no se pueden sumar."
    else:
        if "+1 mp" in text.lower() and persona_encontrada:
            equipo = personas[persona_encontrada]
            puntos_mp[equipo] += 1
            guardar_puntos_mp()
            respuesta = f"¡Punto MP para {equipo}! Total: {puntos_mp[equipo]}"
            print(f"Sumado punto MP a {equipo}. Total: {puntos_mp[equipo]}")
        elif "+1" in text.lower() and persona_encontrada:
            equipo = personas[persona_encontrada]
            puntos[equipo] += 1
            guardar_puntos()
            respuesta = f"¡Punto para {equipo}! Total: {puntos[equipo]}"
            print(f"Sumado punto a {equipo}. Total: {puntos[equipo]}")
        else:
            print("No se sumó punto: condición no cumplida o persona no encontrada.")
    return jsonify({"text": respuesta})

import smtplib
from email.mime.text import MIMEText

@app.route("/comentario", methods=["POST"])
def comentario():
    data = request.get_json()
    nombre = data.get("nombre", "").strip()
    email = data.get("email", "").strip()
    comentario = data.get("comentario", "").strip()
    if nombre and comentario:
        with open("comentarios.txt", "a", encoding="utf-8") as f:
            f.write(f"{nombre}: {comentario}\n")
            # Enviar correo al admin
            try:
                remitente = "perarnaupol@gmail.com"  # Cambia esto
                destinatario = "perarnaupol@gmail.com"  # Cambia esto
                password = "polp2005"  # Cambia esto
                cuerpo = f"Nombre: {nombre}\nCorreo: {email}\nComentario: {comentario}"
                msg = MIMEText(cuerpo)
                msg["Subject"] = "Nuevo comentario recibido"
                msg["From"] = remitente
                msg["To"] = destinatario
                with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                    server.login(remitente, password)
                    server.sendmail(remitente, destinatario, msg.as_string())
            except Exception as e:
                print("Error enviando correo:", e)
        return jsonify({"ok": True})
    return jsonify({"ok": False}), 400

@app.route("/comentarios_raw")
def comentarios_raw():
    try:
        with open("comentarios.txt", "r", encoding="utf-8") as f:
            return "<pre>" + f.read() + "</pre>"
    except FileNotFoundError:
        return "No hay comentarios aún."

from flask import request, Response

@app.route("/admin_comentarios")
def admin_comentarios():
    password = request.args.get("password", "")
    if password != "admin123":
        return '''<form method="get">Contraseña: <input type="password" name="password"><input type="submit" value="Entrar"></form>'''
    try:
        with open("comentarios.txt", "r", encoding="utf-8") as f:
            comentarios = f.read()
        return f"<h2>Comentarios recibidos</h2><pre>{comentarios}</pre>"
    except FileNotFoundError:
        return "No hay comentarios aún."

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)