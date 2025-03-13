from awsS3 import awsS3
import os
import zipfile
class descargarZips(awsS3):
    
    def extraer_zips(self, ruta_extraer, archivo):
        resp = False
        try:
            if not os.path.exists(ruta_extraer):
                os.mkdir(ruta_extraer)
            with zipfile.ZipFile(archivo, 'r') as zip_ref:
                zip_ref.extractall(ruta_extraer)
            resp = True
        except Exception as e:
            resp = False
        return resp
    def descargar_zips(self, ruta_archivo, arn_archivo):
        self.descargar_archivo(arn_archivo, ruta_archivo)
        if(os.path.exists(ruta_archivo)):
            extrae = self.extraer_zips(os.path.dirname(ruta_archivo), ruta_archivo)
            os.remove(ruta_archivo)
            return extrae
        