import yaml
import os
from jinja2 import Environment, FileSystemLoader

# 1. Cargar datos
with open('data/info.yaml', 'r', encoding='utf-8') as f:
    yaml_content = f.read()

# --- ZONA DE SUSTITUCIÓN DE SECRETOS ---
# Buscamos la palabra clave en el texto y la cambiamos por la variable de entorno.

# Reemplazar teléfono
telefono_real = os.environ.get('MY_PHONE', 'Teléfono no disponible') 
yaml_content = yaml_content.replace('SECRET_PHONE', telefono_real)

# Convertirmos el YAML modificado a un diccionario
data = yaml.safe_load(yaml_content)
# ----------------------------------------

# Asegurar que existe carpeta output
os.makedirs('output', exist_ok=True)

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
# Cambiamos {{ }} por \VAR{ } para no romper LaTeX
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