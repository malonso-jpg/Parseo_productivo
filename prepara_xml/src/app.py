from descargarZips import descargarZips
from subirCFDIS import subirCFDIS
from mensajesSQS import mensajesSQS
import os, json
from concurrent.futures import ThreadPoolExecutor, wait
import concurrent.futures

def lambda_handler(event, context):
    ruta_global = '/tmp/cfdis/'
    datos = []
    for record in event['Records']:
        descarga = descargarZips()
        mensajes = mensajesSQS()
        data = json.loads(record['body'])
        caracter = (data["EmitidoORecibido"]).upper()
        rfc = data["rfc"]
        arn_zip = data["Archivo"]
        msg = {"arn": arn_zip, "rfc": rfc}
        mensajes.envia_msg(json.dumps(msg), 'orden_nombres_zips')
        nombre_archivo = os.path.basename(arn_zip)
        ruta_archivo = f'{ruta_global}/{rfc}/{nombre_archivo.replace(".zip", "")}/{caracter}/{nombre_archivo}'
        crear_carpetas(ruta_archivo)
        datos.append([ruta_archivo, arn_zip])
    with ThreadPoolExecutor() as executor:
        [executor.submit(descarga.descargar_zips, ruta_archivo, arn_zip) for ruta_archivo, arn_zip in datos]

    subir = subirCFDIS(ruta_global, 'tmp')
    con = 0
    while(True):
        subir.subir()
        file_names = [os.path.join(carpeta, file) for carpeta, _, archivos in os.walk(ruta_global) for file in archivos if file.endswith('.xml')]
        if(len(file_names) == 0 or con == 5):
            break
        con += 1
    subir.enviar_mensajes_carga()

def crear_carpetas(carpeta):
    try:
        if(not os.path.exists(os.path.dirname(carpeta))):
            os.makedirs(os.path.dirname(carpeta))
    except Exception:
        pass
def main():

    lambda_handler(None, None)

if __name__ == "__main__":
    main()