import os
import boto3, json

class awsS3:
    def __init__(self):
        self.s3 = self.conexion_s3()
        self.bucket_name = os.environ["NOMBRE_BUCKET"]
    def conexion_s3(self):
        return boto3.client('s3')
    def subir_archivo(self, ruta_cfdi, s3_key):
        try:
            self.s3.upload_file(ruta_cfdi, self.bucket_name, s3_key)
            return True
        except Exception as e:
            return str(type(e).__name__)
    def descargar_archivo(self, s3_key, archivo_local):
        try:
            self.s3.download_file(self.bucket_name, s3_key, archivo_local)
            return True
        except Exception as e:
            if e.response['Error']['Code'] == "404":
                return False
            if e.response['Error']['Code'] == "503":
                return '503'
            else:
                print("Error al descargar xml:", e)
                return json.dumps(e.response['Error'])
    def obtener_tamano_archivo(self, s3_key):
        try:
            response = self.s3.head_object(Bucket=self.bucket_name, Key=s3_key)
            file_size = response['ContentLength']
            return int(round(file_size / (1024 * 1024)))
        except Exception as e:
            if e.response['Error']['Code'] == "404":
                return 0
            else:
                return False

    def elimina_archivo(self, s3_key):
        try:
            self.s3.delete_object(Bucket=self.bucket_name, Key=s3_key)
            return True
        except Exception as e:
            return False