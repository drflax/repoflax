import json
import os
import datetime

# 1. Leer los datos del evento de GitHub Release
event_path = os.getenv('GITHUB_EVENT_PATH')
with open(event_path, 'r', encoding='utf-8') as f:
    event_data = json.load(f)

release = event_data.get('release', {})
tag_name = release.get('tag_name', '1.0.0')
release_name = release.get('name', tag_name) # Título del release o tag
assets = release.get('assets', [])

# 2. Buscar el archivo .ipa adjunto en el release
ipa_asset = next((a for a in assets if a['name'].endswith('.ipa')), None)
if not ipa_asset:
    print("No se encontró ningún archivo .ipa en este release.")
    exit(0)

download_url = ipa_asset['browser_download_url']
file_size = ipa_asset['size']
ipa_filename = ipa_asset['name']  # Ejemplo: "MiAppNueva.ipa"
version = tag_name.split('-')[-1].lstrip('v') # Extrae la versión (ej. v1.0.0 -> 1.0.0)

# Limpiar el nombre del archivo para usarlo de base si es nueva
app_name_inferred = ipa_filename.replace('.ipa', '').replace('-', ' ').replace('_', ' ').title()

# 3. Cargar el archivo apps.json existente
json_path = 'apps.json'
with open(json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Asegurarnos de que la estructura 'apps' existe
if 'apps' not in data:
    data['apps'] = []

# 4. Buscar si la aplicación ya existe en el JSON
app_encontrada = None
for app in data['apps']:
    # Comparamos si el nombre del IPA o el bundleID coincide de alguna forma
    bundle_id_short = app['bundleIdentifier'].split('.')[-1].lower()
    app_name_short = app['name'].replace(" ", "").lower()
    
    if bundle_id_short in ipa_filename.lower() or app_name_short in ipa_filename.lower():
        app_encontrada = app
        break

if app_encontrada:
    # Si ya existe, solo actualizamos sus datos
    app_encontrada['version'] = version
    app_encontrada['downloadURL'] = download_url
    app_encontrada['size'] = file_size
    app_encontrada['versionDate'] = datetime.date.today().isoformat()
    print(f"Aplicación existente '{app_encontrada['name']}' actualizada a la versión {version}.")
else:
    # Si NO existe, la creamos desde cero automáticamente como una nueva app
    nueva_app = {
        "name": app_name_inferred,
        "bundleIdentifier": f"com.repo.{app_name_inferred.lower().replace(' ', '')}",
        "developerName": "DrFlax",
        "version": version,
        "versionDate": datetime.date.today().isoformat(),
        "versionDescription": release_name if release_name else "Nueva aplicación añadida al repositorio.",
        "downloadURL": download_url,
        "localizedDescription": f"Aplicación {app_name_inferred} gestionada automáticamente por GitHub Actions.",
        "iconURL": f"https://raw.githubusercontent.com/drflax/repoflax/main/{app_name_inferred.lower().replace(' ', '')}.png",
        "size": file_size,
        "permissions": []
    }
    data['apps'].append(nueva_app)
    print(f"¡Nueva aplicación '{app_name_inferred}' detectada y añadida al apps.json con éxito!")

# 5. Guardar los cambios en el apps.json
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("apps.json guardado y actualizado correctamente.")
