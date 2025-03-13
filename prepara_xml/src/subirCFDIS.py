from awsS3 import awsS3
import os, time
from mensajesSQS import mensajesSQS
from concurrent.futures import ThreadPoolExecutor
class subirCFDIS(awsS3, mensajesSQS):
    
   def __init__(self, ruta, prefijo):
      super().__init__()
      self._ruta = ruta
      self._prefijo = prefijo
      self._mensajes_listo_xml = []
      self._mensajes_listo_xml1_7 = []
      self._mensajes_listo_xml7_n = []
   def obtener_tamano_archivo(self, ruta_archivo):
    if os.path.exists(ruta_archivo):
        tamano_bytes = os.path.getsize(ruta_archivo)
        tamano_mb = tamano_bytes / (1024 * 1024)
        return tamano_mb
    else:
        return 0
   def subir_xmls(self, ruta_cfdi, s3_key):
      if(self.subir_archivo(ruta_cfdi, s3_key)):
            partes = s3_key.split("/")
            rfc = partes[1]
            caracter = partes[3]
            carpeta = partes[2]
            msg = {"arn": s3_key, "rfc": rfc, "caracter": caracter, "carpeta_nombre_zip": carpeta}
            tamano_archivo = self.obtener_tamano_archivo(ruta_cfdi)
            if(tamano_archivo > 2 and tamano_archivo < 7):
               self._mensajes_listo_xml1_7.append(msg)
            elif(tamano_archivo >= 7):
               self._mensajes_listo_xml7_n.append(msg)
            else:
               self._mensajes_listo_xml.append(msg)
            try:
               os.remove(ruta_cfdi)
            except Exception:
               pass
   def subir(self):
      futures = []
      with ThreadPoolExecutor() as executor:
         futures = []
         for root, dirs, files in os.walk(self._ruta):
               for file in files:
                  if(file.endswith('.xml')):
                     ruta_cfdi = os.path.join(root, file)
                     relative_path = os.path.relpath(ruta_cfdi, self._ruta)
                     s3_key = os.path.join(self._prefijo, relative_path)
                     s3_key = s3_key.replace(os.path.sep, "/")
                     futures.append(executor.submit(self.subir_xmls, ruta_cfdi, s3_key))
         for future in futures:
            future.result()
   def enviar_mensajes_carga(self):
      #Enviar mensajes
      if(self._mensajes_listo_xml):
         self.envia_muchos_msg(self._mensajes_listo_xml, 'listoXml')
      if(self._mensajes_listo_xml1_7):
         self.envia_muchos_msg(self._mensajes_listo_xml1_7, 'parseo_listoXml1_7')
      if(self._mensajes_listo_xml7_n):
         self.envia_muchos_msg(self._mensajes_listo_xml7_n, 'parseo_listoXml7_n')
      
