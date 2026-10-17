# Servidor MCP en Python 🚀

Este proyecto es un servidor funcional construido sobre el estándar **Model Context Protocol (MCP)** usando **FastMCP** (del SDK oficial de Python). Permite que un modelo de lenguaje o asistente interactúe con el entorno local (cálculos, conteo de texto, fecha del sistema) y consuma información en tiempo real desde APIs públicas de internet sin necesidad de registrar claves ni pagar nada.

---

## 🛠️ ¿Qué puede hacer este servidor?

### 1. Herramientas Locales (Tools)
* **Calculadora (`calculadora`)**: Realiza operaciones aritméticas básicas (`suma`, `resta`, `multiplicacion`, `division`) controlando divisiones por cero.
* **Contador de texto (`contador_texto`)**: Analiza cualquier texto y entrega métricas como número de palabras, letras, vocales, consonantes y caracteres totales.
* **Fecha y hora del sistema (`obtener_fecha_sistema`)**: Devuelve la fecha actual, la hora, el día de la semana y el formato legible en español.

### 2. Consultas en vivo a Internet (APIs sin API Key)
* **Datos de Pokémon (`consultar_pokemon`)**: Conexión con PokéAPI para consultar stats, tipos, habilidades, altura, peso y sprite de cualquier Pokémon por nombre o ID.
* **Clima actual (`consultar_clima`)**: Conexión con Open-Meteo. No necesitas saber coordenadas: buscas por ciudad (ej. *Medellin*, *Bogota*, *Buenos Aires*), el servidor resuelve la ubicación y te entrega temperatura, sensación térmica, viento y humedad.

### 3. Recursos de Contexto (Resources)
Textos fijos que el modelo puede leer como referencia cuando lo necesite:
* `rules://reglas-uso`: Directrices de comportamiento y honestidad en las respuestas.
* `info://desarrollador`: Metadatos y versiones del servidor.
* `glossary://terminos`: Breve glosario sobre qué es una tool, un resource y un prompt en MCP.

### 4. Plantillas de Ayuda (Prompts)
Plantillas preconfiguradas para que el agente sepa exactamente cómo llamar a las APIs y qué datos resaltar al usuario:
* `guia_consulta_pokemon`: Instrucción paso a paso para procesar consultas sobre Pokémon.
* `guia_consulta_clima`: Plantilla para armar reportes meteorológicos con recomendaciones prácticas.

---

## 📋 Requisitos

* **Python 3.10** o superior instalado en tu máquina.
* **Node.js y npm** (opcional, solo si quieres usar el inspector visual para probarlo).

---

## 💻 Instalación y puesta en marcha

### 1. Clona o entra a la carpeta del proyecto
```bash
cd AGENT
```

### 2. Crea un entorno virtual (recomendado)
```bash
# En Windows (PowerShell)
python -m venv venv
.\venv\Scripts\activate

# En Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Instala las dependencias
```bash
pip install -r requirements.txt
```

### 4. Ejecuta el servidor
Para arrancar el servidor directamente en modo `stdio`:
```bash
python index.py
```
*(Nota: Al usar el transporte stdio, el servidor queda escuchando entradas por consola. No verás una página web en el navegador con este comando, está diseñado para comunicarse con un cliente MCP).*

---

## 🔍 ¿Cómo probarlo fácilmente?

La forma más rápida y visual de interactuar con las herramientas, recursos y prompts es con el **MCP Inspector**:

```bash
npx @modelcontextprotocol/inspector python index.py
```

Esto abrirá automáticamente una interfaz web en tu navegador (`http://localhost:5173` o similar) donde podrás:
1. Probar cada herramienta con tus propios parámetros (por ejemplo, buscar `pikachu` o consultar el clima de `Madrid`).
2. Inspeccionar los recursos estáticos.
3. Probar la generación de los prompts.

---

## 🤖 Conectar a clientes (ej. Claude Desktop o Cursor)

Si deseas usarlo con un cliente compatible con MCP (como Claude Desktop), agrega la siguiente configuración en tu archivo `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "servidor-riwi": {
      "command": "python",
      "args": [
        "C:\\Users\\luuca\\Desktop\\Riwi\\AGENT\\index.py"
      ]
    }
  }
}
```
*(Asegúrate de ajustar la ruta al ejecutable de Python o a tu script si usas un entorno virtual).*

---

## 📁 Estructura del proyecto

```text
AGENT/
│
├── index.py           # Código principal del servidor FastMCP
├── requirements.txt   # Dependencias mínimas (mcp, httpx)
└── README.md          # Esta guía de uso y documentación
```
