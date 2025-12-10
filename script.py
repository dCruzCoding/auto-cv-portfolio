import yaml
import os
import shutil
from jinja2 import Environment, FileSystemLoader

# 1. Cargar datos
with open('data/info.yaml', 'r', encoding='utf-8') as f:
    yaml_content = f.read()

# --- ZONA DE SUSTITUCIÓN DE SECRETOS ---
# Reemplazar teléfono
telefono_real = os.environ.get('MY_PHONE', 'Teléfono no disponible') 
yaml_content = yaml_content.replace('SECRET_PHONE', telefono_real)

# Convertirmos el YAML modificado a un diccionario
data = yaml.safe_load(yaml_content)
# ----------------------------------------

# Asegurar que existe carpeta output
os.makedirs('output', exist_ok=True)

# ---------------------------------------------------------
# COPIAR LA FOTO 📸
# ---------------------------------------------------------
if 'config' in data and 'foto' in data['config'] and data['config']['foto']:
    nombre_foto = data['config']['foto']
    ruta_origen = os.path.join('data', nombre_foto)
    ruta_destino = os.path.join('output', nombre_foto)
    
    # Solo copiamos si el archivo existe en 'data/'
    if os.path.exists(ruta_origen):
        shutil.copy(ruta_origen, ruta_destino)
        print(f"📸 Foto '{nombre_foto}' copiada a la carpeta output.")
    else:
        print(f"⚠️ ADVERTENCIA: En el YAML pides '{nombre_foto}', pero no está en la carpeta data/.")

# ---------------------------------------------------------
# CONFIGURACIÓN PARA HTML (Jinja estándar: {{ variable }})
# ---------------------------------------------------------
env_html = Environment(loader=FileSystemLoader('templates'))
template_html = env_html.get_template('portfolio.html')

# Renderizar HTML
html_output = template_html.render(data)
with open('output/index.html', 'w', encoding='utf-8') as f:
    f.write(html_output)
print("✅ HTML generado correctamente.")

# ---------------------------------------------------------
# CONFIGURACIÓN PARA LATEX (Jinja modificado)
# ---------------------------------------------------------
env_latex = Environment(
    loader=FileSystemLoader('templates'),
    block_start_string='\\BLOCK{',
    block_end_string='}',
    variable_start_string='\\VAR{',
    variable_end_string='}',
    comment_start_string='\\#{',
    comment_end_string='}',
    line_statement_prefix='%%',
    line_comment_prefix='%#',
    trim_blocks=True,
    autoescape=False,
)

# Añadimos un filtro para escapar caracteres especiales de LaTeX
def escape_latex(text):
    if not isinstance(text, str):
        return text
    replacements = {
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
        '^': r'\textasciicircum{}'
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text

# Registrar el filtro
env_latex.filters['escape_tex'] = escape_latex
env_latex.filters['upper'] = lambda x: x.upper() if isinstance(x, str) else x

template_latex = env_latex.get_template('cv_template.tex')

# Definimos los perfiles que queremos generar
# Clave: Nombre del archivo final
# Valor: Etiqueta requerida (o None para incluir todo)
perfiles = {
    "cv_programacion": "programacion",
    "cv_investigacion": "investigacion",
    "cv_atencion": "atencion_cliente",
    "cv_general": None  # Este incluirá todo
}

for nombre_archivo, etiqueta_filtro in perfiles.items():
    datos_render = data.copy() # Copia superficial (cuidado con listas anidadas)
    
    if etiqueta_filtro:
        # 1. Filtrar Experiencia
        datos_render['experiencia'] = [
            i for i in data['experiencia'] if etiqueta_filtro in i.get('tags', [])
        ]
        # 2. Filtrar Formación
        datos_render['formacion'] = [
            i for i in data['formacion'] if etiqueta_filtro in i.get('tags', []) or 'general' in i.get('tags', [])
        ]
        # 3. Filtrar Habilidades
        datos_render['habilidades'] = [
            i for i in data['habilidades'] if etiqueta_filtro in i.get('tags', []) or 'general' in i.get('tags', [])
        ]

    # Renderizar...
    # Renderizamos la plantilla con los datos (filtrados o no)
    latex_output = template_latex.render(datos_render)
    
    # Guardamos el archivo específico
    with open(f'output/{nombre_archivo}.tex', 'w', encoding='utf-8') as f:
        f.write(latex_output)
    
    print(f"✅ Generado: {nombre_archivo}.tex ({len(datos_render['experiencia'])} experiencias)")