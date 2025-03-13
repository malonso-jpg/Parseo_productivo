import os
import boto3
import json
from concurrent.futures import ThreadPoolExecutor
import traceback

class mensajesSQS:
    
    def conexion_sqs(self, region):
        return boto3.client('sqs', region_name=region)
    
    def consumes_msg_prueba(self, nombre_sqs):
        datos_cola = os.environ['SQS_PARSEO'].split('||')
        for datos in datos_cola:
            name_sqs, region = datos.split("=")
            if nombre_sqs == name_sqs:
                id_sqs = os.environ['ID_SQS']
                sqs = self.conexion_sqs(region)
                url_sqs = f"https://sqs.{region}.amazonaws.com/{id_sqs}/{name_sqs}"
                datos_mensajes = []
                while len(datos_mensajes) < 50:
                    response = sqs.receive_message(
                        QueueUrl=url_sqs,
                        MaxNumberOfMessages=10,
                    )

                    if 'Messages' in response:
                        for message in response['Messages']:
                            body_strc = json.loads(message['Body'])
                            body_strc['id_elimina'] = message["ReceiptHandle"]
                            datos_mensajes.append(body_strc)
                            if len(datos_mensajes) >= 50:
                                break
                    if 'Messages' not in response or len(response['Messages']) == 0:
                        break
                return datos_mensajes
    def envia_msg(self, texto_msg, nombre_sqs):
        datos_cola = os.environ['SQS_PARSEO'].split('||')
        for datos in datos_cola:
            name_sqs, region = datos.split("=")
            if(nombre_sqs == name_sqs):
                id_sqs = os.environ['ID_SQS']
                sqs = self.conexion_sqs(region)
                url_sqs = f"https://sqs.{region}.amazonaws.com/{id_sqs}/{name_sqs}"
                try:
                    sqs.send_message(
                        QueueUrl=url_sqs,
                        MessageBody=texto_msg
                    )
                    return True
                except Exception as e:
                    error_info = traceback.format_exc()
                    print(error_info, texto_msg, nombre_sqs)
                    return str(error_info) 
    def eliminar_msg(self, id_elimina, nombre_sqs):
        datos_cola = os.environ['SQS_PARSEO'].split('||')
        for datos in datos_cola:
            name_sqs, region = datos.split("=")
            if(nombre_sqs == name_sqs):
                id_sqs = os.environ['ID_SQS']
                sqs = self.conexion_sqs(region)
                url_sqs = f"https://sqs.{region}.amazonaws.com/{id_sqs}/{name_sqs}"
                sqs.delete_message(
                    QueueUrl = url_sqs,
                    ReceiptHandle=id_elimina
                )
    def envia_muchos_msg(self, messages, nombre_sqs):
        datos_cola = os.environ['SQS_PARSEO'].split('||')
        for datos in datos_cola:
            name_sqs, region = datos.split("=")
            if(nombre_sqs == name_sqs):
                id_sqs = os.environ['ID_SQS']
                sqs = self.conexion_sqs(region)
                url_sqs = f"https://sqs.{region}.amazonaws.com/{id_sqs}/{name_sqs}"
                with ThreadPoolExecutor() as executor:
                    for i in range(0, len(messages), 10):
                        batch = messages[i:i+10]
                        entries = [{'Id': str(idx), 'MessageBody': json.dumps(msg)} for idx, msg in enumerate(batch)]
                        executor.submit(self.enviar_batch, sqs, url_sqs, entries)
    def enviar_batch(self, sqs, url_sqs, entries):
        sqs.send_message_batch(QueueUrl=url_sqs, Entries=entries)
