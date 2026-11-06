import json
import os
import datetime

# Leer los datos del evento de GitHub Release
event_path = os.getenv('GITHUB_EVENT_PATH')
with open(event_path, 'r', encoding='utf-8') as f:
    event_data = json.load(f)

release = event_data.get('release', {})
tag_name = release.get('tag_name', '1.0.0')
assets = release.get('assets', [])

# Buscar el archivo .ipa adjunto en el release
ipa_asset = next((a for a in assets if a['name'].endswith('.ipa')), None)
if not ipa_asset:
    print("No se encontró ningún archivo .ipa en este release.")
    exit(0)

download_url = ipa_asset['browser_download_url']
file_size = ipa_asset['size']
version = tag_name.lstrip('v') # Limpia la 'v' si la etiqueta es v1.0.0

# Cargar el archivo apps.json existente
json_path = 'apps.json'
with open(json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Actualizar los datos de la primera aplicación del JSON
if data.get('apps'):
    app = data['apps'][0] 
    app['version'] = version
    app['downloadURL'] = download_url
    app['size'] = file_size
    app['versionDate'] = datetime.date.today().isoformat()

# Guardar los cambios en el apps.json
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"apps.json actualizado con éxito para la versión {version} (Tamaño: {file_size} bytes).")
