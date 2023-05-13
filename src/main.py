from typing import Optional
from fastapi import FastAPI, HTTPException
import requests
import json
import zipfile
from io import BytesIO

app = FastAPI()

@app.get("/rick-and-morty-api-public/")
async def consume_api(name: Optional[str] = None, gender: Optional[str] = None, specie: Optional[str] = None, download_zip: Optional[bool] = False):
    # Hacemos una solicitud HTTP GET a la API pública
    response = requests.get('https://rickandmortyapi.com/api/character')

    # Verificamos que la solicitud fue exitosa
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Error al obtener datos de la API")

    # Convertimos la respuesta a un objeto JSON
    data = json.loads(response.content)
    
    # Aplicamos los filtros, si es que se proporcionaron
    if name:
        data = [item for item in data['results'] if item.get(name)]
    if gender:
        data = [item for item in data['results'] if item.get(gender)]
    if specie:
        data = [item for item in data['results'] if item.get(specie)]
        

    if download_zip:
        # Creamos un archivo zip que contenga el archivo JSON
        bytes_io = BytesIO()
        with zipfile.ZipFile(bytes_io, mode='w', compression=zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("data.json", json.dumps(data))

        # Enviamos el archivo zip como una respuesta HTTP
        bytes_io.seek(0)
        headers = {
            'Content-Disposition': 'attachment; filename=data.zip'
        }
        return bytes_io.getvalue(), headers

    # Retornamos la lista de datos filtrados
    return data
