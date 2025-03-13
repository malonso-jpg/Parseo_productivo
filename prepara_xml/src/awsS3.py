import os
import boto3

class awsS3:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.s3 = cls._instance.conexion_s3()
            cls._instance.bucket_name = os.environ.get("NOMBRE_BUCKET")
        return cls._instance
    def conexion_s3(self):
        return boto3.client('s3')
    
    def subir_archivo(self, ruta_cfdi, s3_key):
        try:
            self.s3.upload_file(ruta_cfdi, self.bucket_name, s3_key)
            return True
        except Exception as e:
            return False
    def descargar_archivo(self, s3_key, archivo_local):
        try:
            self.s3.download_file(self.bucket_name, s3_key, archivo_local)
            return True
        except Exception:
            return False
    def elimina_archivo(self, s3_key):
        try:
            self.s3.delete_object(Bucket=self.bucket_name, Key=s3_key)
            return True
        except Exception:
            return False
