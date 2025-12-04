import yaml
import os
from jinja2 import Environment, FileSystemLoader

# 1. Cargar datos
with open('data/info.yaml', 'r', encoding='utf-8') as f:
    data = yaml.safe_load(f)

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
    
    # Creamos una copia de los datos para no modificar el original
    datos_para_renderizar = data.copy()
    
    if etiqueta_filtro:
        # FILTRADO: Nos quedamos solo con las experiencias que tengan esa etiqueta
        experiencia_filtrada = [
            item for item in data['experiencia'] 
            if etiqueta_filtro in item['tags']
        ]
        datos_para_renderizar['experiencia'] = experiencia_filtrada
    
    # Renderizamos la plantilla con los datos (filtrados o no)
    latex_output = template_latex.render(datos_para_renderizar)
    
    # Guardamos el archivo específico
    with open(f'output/{nombre_archivo}.tex', 'w', encoding='utf-8') as f:
        f.write(latex_output)
    
    print(f"✅ Generado: {nombre_archivo}.tex ({len(datos_para_renderizar['experiencia'])} experiencias)")