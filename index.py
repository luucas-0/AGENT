"""
Servidor MCP (Model Context Protocol) en Python
Implementado con FastMCP del SDK oficial de MCP.

Incluye:
- 3 Herramientas locales (cálculo, métricas de texto, fecha del sistema)
- 2 Herramientas de Internet con httpx (PokéAPI y Open-Meteo)
- 3 Recursos estáticos (reglas de uso, info de desarrollador, glosario)
- 2 Prompts de integración para guiar al modelo
"""

from datetime import datetime
import httpx
from mcp.server.mcpserver import MCPServer

# Inicialización del servidor MCP
mcp = MCPServer("Servidor-MCP-Riwi")


# ==========================================
# 1. HERRAMIENTAS LOCALES (3 TOOLS)
# ==========================================

@mcp.tool()
def calculadora(operacion: str, a: float, b: float) -> dict:
    """
    Realiza operaciones aritméticas básicas entre dos números.
    
    Args:
        operacion: Tipo de operación ('suma', 'resta', 'multiplicacion', 'division').
        a: Primer operando numérico.
        b: Segundo operando numérico.
    """
    op = operacion.lower().strip()
    if op in ["suma", "sumar", "+"]:
        resultado = a + b
    elif op in ["resta", "restar", "-"]:
        resultado = a - b
    elif op in ["multiplicacion", "multiplicar", "*"]:
        resultado = a * b
    elif op in ["division", "dividir", "/"]:
        if b == 0:
            return {"error": "División por cero no permitida.", "exito": False}
        resultado = a / b
    else:
        return {
            "error": f"Operación '{operacion}' no reconocida. Usa: suma, resta, multiplicacion o division.",
            "exito": False
        }

    return {
        "operacion": op,
        "a": a,
        "b": b,
        "resultado": resultado,
        "exito": True
    }


@mcp.tool()
def contador_texto(texto: str) -> dict:
    """
    Analiza un texto y cuenta letras, vocales, consonantes, palabras y caracteres totales.
    
    Args:
        texto: Cadena de texto a analizar.
    """
    vocales = "aeiouáéíóúü"
    total_caracteres = len(texto)
    caracteres_sin_espacios = len(texto.replace(" ", ""))
    palabras = len(texto.split()) if texto.strip() else 0

    num_vocales = sum(1 for c in texto.lower() if c in vocales)
    num_letras = sum(1 for c in texto if c.isalpha())
    num_consonantes = num_letras - num_vocales
    num_digitos = sum(1 for c in texto if c.isdigit())

    return {
        "total_caracteres": total_caracteres,
        "caracteres_sin_espacios": caracteres_sin_espacios,
        "total_palabras": palabras,
        "total_letras": num_letras,
        "vocales": num_vocales,
        "consonantes": num_consonantes,
        "digitos": num_digitos
    }


@mcp.tool()
def obtener_fecha_sistema() -> dict:
    """
    Obtiene la fecha, hora actual y día de la semana del sistema local.
    """
    ahora = datetime.now()
    dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    meses = [
        "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
        "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
    ]

    return {
        "fecha": ahora.strftime("%Y-%m-%d"),
        "hora": ahora.strftime("%H:%M:%S"),
        "dia_semana": dias[ahora.weekday()],
        "mes": meses[ahora.month - 1],
        "año": ahora.year,
        "formato_humano": f"{dias[ahora.weekday()]}, {ahora.day} de {meses[ahora.month - 1]} de {ahora.year} - {ahora.strftime('%H:%M:%S')}"
    }


# ==========================================
# 2. HERRAMIENTAS DE INTERNET / APIS (2 TOOLS)
# ==========================================

@mcp.tool()
async def consultar_pokemon(nombre_o_id: str) -> dict:
    """
    Consulta información detallada de un Pokémon mediante la API pública de PokéAPI.
    
    Args:
        nombre_o_id: Nombre (en inglés o estándar, ej. 'pikachu', 'charizard') o ID numérico del Pokémon.
    """
    query = str(nombre_o_id).strip().lower()
    url = f"https://pokeapi.co/api/v2/pokemon/{query}"

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            respuesta = await client.get(url)

            if respuesta.status_code == 404:
                return {
                    "error": f"Pokémon '{nombre_o_id}' no encontrado en PokéAPI.",
                    "exito": False
                }
            respuesta.raise_for_status()
            data = respuesta.json()

            # Extraemos los datos más relevantes
            tipos = [t["type"]["name"] for t in data.get("types", [])]
            habilidades = [h["ability"]["name"] for h in data.get("abilities", [])]
            estadisticas = {
                s["stat"]["name"]: s["base_stat"] for s in data.get("stats", [])
            }

            return {
                "exito": True,
                "id": data.get("id"),
                "nombre": data.get("name"),
                "altura_decimetros": data.get("height"),
                "peso_hectogramos": data.get("weight"),
                "tipos": tipos,
                "habilidades": habilidades,
                "estadisticas_base": estadisticas,
                "sprite_frontal": data.get("sprites", {}).get("front_default")
            }

    except httpx.RequestError as exc:
        return {
            "error": f"Error de conexión al consultar PokéAPI: {str(exc)}",
            "exito": False
        }


@mcp.tool()
async def consultar_clima(ciudad: str) -> dict:
    """
    Obtiene el clima actual para una ciudad usando la API pública y sin clave de Open-Meteo.
    
    Args:
        ciudad: Nombre de la ciudad a consultar (ej. 'Bogota', 'Madrid', 'Medellin').
    """
    ciudad_limpia = ciudad.strip()
    geocoding_url = "https://geocoding-api.open-meteo.com/v1/search"

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # 1. Geocodificación para obtener latitud y longitud
            geo_resp = await client.get(
                geocoding_url,
                params={"name": ciudad_limpia, "count": 1, "language": "es", "format": "json"}
            )
            geo_resp.raise_for_status()
            geo_data = geo_resp.json()

            resultados = geo_data.get("results")
            if not resultados:
                return {
                    "error": f"No se encontraron coordenadas para la ciudad '{ciudad}'.",
                    "exito": False
                }

            loc = resultados[0]
            lat = loc["latitude"]
            lon = loc["longitude"]
            nombre_oficial = f"{loc.get('name')}, {loc.get('country', '')}"

            # 2. Consulta de clima actual
            weather_url = "https://api.open-meteo.com/v1/forecast"
            params = {
                "latitude": lat,
                "longitude": lon,
                "current": [
                    "temperature_2m",
                    "relative_humidity_2m",
                    "apparent_temperature",
                    "precipitation",
                    "wind_speed_10m"
                ],
                "timezone": "auto"
            }

            w_resp = await client.get(weather_url, params=params)
            w_resp.raise_for_status()
            w_data = w_resp.json()

            current = w_data.get("current", {})
            current_units = w_data.get("current_units", {})

            return {
                "exito": True,
                "ubicacion": nombre_oficial,
                "latitud": lat,
                "longitud": lon,
                "zona_horaria": w_data.get("timezone"),
                "temperatura": f"{current.get('temperature_2m')} {current_units.get('temperature_2m', '°C')}",
                "sensacion_termica": f"{current.get('apparent_temperature')} {current_units.get('apparent_temperature', '°C')}",
                "humedad_relativa": f"{current.get('relative_humidity_2m')} {current_units.get('relative_humidity_2m', '%')}",
                "precipitacion": f"{current.get('precipitation')} {current_units.get('precipitation', 'mm')}",
                "velocidad_viento": f"{current.get('wind_speed_10m')} {current_units.get('wind_speed_10m', 'km/h')}"
            }

    except httpx.RequestError as exc:
        return {
            "error": f"Error de conexión al consultar Open-Meteo: {str(exc)}",
            "exito": False
        }


# ==========================================
# 3. RECURSOS ESTÁTICOS (3 RESOURCES)
# ==========================================

@mcp.resource("rules://reglas-uso")
def reglas_de_uso() -> str:
    """Reglas y políticas de operación del asistente y servidor MCP."""
    return """# REGLAS DE OPERACIÓN DEL SISTEMA
1. Decisión Autónoma: Evalúa las herramientas antes de elaborar respuestas finales.
2. Integridad de Datos: Nunca alucines datos provenientes de APIs externas; si una API falla, reporta el error técnico.
3. Formato Claro: Presenta las respuestas al usuario en lenguaje natural amigable y estructurado.
4. Uso Local: Para cálculos, conteo de texto o fechas del sistema, utiliza siempre las herramientas locales.
5. Eficiencia: Consulta recursos y herramientas solo cuando sea necesario para resolver la solicitud."""


@mcp.resource("info://desarrollador")
def info_desarrollador() -> str:
    """Información del desarrollador y metadatos del servidor."""
    return """# INFORMACIÓN DEL SERVIDOR Y DESARROLLADOR
- Servidor: Servidor MCP Riwi
- Versión: 1.0.0
- Protocolo: Model Context Protocol (MCP)
- Framework: FastMCP (Python)
- Cliente HTTP: httpx (asíncrono)
- Propósito: Exponer herramientas locales, APIs públicas de clima y Pokémon, recursos y prompts."""


@mcp.resource("glossary://terminos")
def glosario_terminos() -> str:
    """Glosario de términos clave de la arquitectura MCP."""
    return """# GLOSARIO DE TÉRMINOS MCP
- MCP (Model Context Protocol): Protocolo abierto que estandariza cómo los LLMs interactúan con herramientas y fuentes de contexto.
- Tool (Herramienta): Función ejecutable por el servidor a petición del modelo (ej. cálculos, consultas API).
- Resource (Recurso): Fuente pasiva de datos (archivos, texto, esquemas) que el modelo puede leer como contexto.
- Prompt (Plantilla): Plantilla parametrizada definida en el servidor para guiar al modelo en flujos de trabajo específicos.
- Stdio Transport: Mecanismo de comunicación basado en entrada/salida estándar entre el cliente y el servidor MCP."""


# ==========================================
# 4. PROMPTS DE INTEGRACIÓN (2 PROMPTS)
# ==========================================

@mcp.prompt()
def guia_consulta_pokemon(nombre_pokemon: str) -> str:
    """
    Plantilla de integración para guiar al agente en la consulta de Pokémon.
    """
    return f"""Instrucción para el Asistente:
El usuario desea consultar información sobre el Pokémon: '{nombre_pokemon}'.

Pasos a seguir:
1. Invoca la herramienta 'consultar_pokemon' pasando el argumento nombre_o_id='{nombre_pokemon}'.
2. Espera la respuesta JSON. Si 'exito' es falso o hay error, infórmale respetuosamente al usuario que el Pokémon no fue encontrado o hubo un error técnico.
3. Si la respuesta es exitosa, extrae y presenta claramente al usuario:
   - Nombre y número de Pokédex (#ID).
   - Tipos elementales (ej. Eléctrico, Fuego, etc.).
   - Habilidades principales.
   - Estadísticas base destacadas (HP, Ataque, Defensa, Velocidad).
   - Altura y peso en unidades convencionales.
4. Responde en tono amigable y en español."""


@mcp.prompt()
def guia_consulta_clima(ciudad: str) -> str:
    """
    Plantilla de integración para guiar al agente en la consulta de clima.
    """
    return f"""Instrucción para el Asistente:
El usuario solicita el clima actual para la ciudad: '{ciudad}'.

Pasos a seguir:
1. Invoca la herramienta 'consultar_clima' con el argumento ciudad='{ciudad}'.
2. Analiza el JSON devuelto. Si ocurrió un error de geocodificación o conexión, explícaselo al usuario de forma clara sin inventar datos.
3. Si la consulta es exitosa, redacta un reporte meteorológico estructurado con:
   - Ubicación exacta detectada.
   - Temperatura actual y sensación térmica.
   - Humedad relativa y velocidad del viento.
   - Nivel de precipitación.
4. Agrega una breve recomendación práctica según el clima (por ejemplo, si llueve o hace frío, abrigarse o llevar paraguas)."""


# ==========================================
# PUNTO DE ENTRADA PRINCIPAL
# ==========================================

if __name__ == "__main__":
    # Ejecuta el servidor MCP sobre transporte estándar stdio
    mcp.run()
