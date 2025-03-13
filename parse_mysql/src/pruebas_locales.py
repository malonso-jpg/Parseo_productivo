from parseo.parseoDatosGenerales import parseoDatosGenerales
from parseo.parseoIngresosEgresos import parseoIngresosEgresos
from parseo.parseoPagos import parseoPagos
from parseo.parseoNomina import parseoNomina
from parseo.parseoConceptos import parseoConceptos
from parseo.parseoRelaciones import parseoRelaciones
from aws.mensajesSQS import mensajesSQS
from aws.awsS3 import awsS3
from data.funcionesMySQL import funcionesMySQL

import json, os, re
from lxml import etree
import traceback
from datetime import datetime
import concurrent.futures
import time

class app():
    def __init__(self):
        self.respuesta_datos = []
        self.respuesta_muchos = {
            'relaciones': [],
            'conceptos': [],
            'pagos_documentos': [],
            'nomina_sub_contrataciones': [],
            'nomina_incapacidades': [],
            'nomina_detallada': []
        }
        self.nodos_cfdi = []
    def datos_cfdis(self):
        if(self.respuesta_datos):
            return self.respuesta_datos
        return False
    def datos_detallados_cfdi(self):
        if(self.respuesta_muchos):
            return self.respuesta_muchos
        return False
    def quitar_nodos(self, texto_xml, datos_json):
        xml_string_modificado = ""
        for quitar_nodos in datos_json['quitar_nodos']:
            separado = quitar_nodos.split('||')
            quita = separado[0]
            nodo = separado[1]
            if nodo in texto_xml:
                if xml_string_modificado == "":
                    patron_contenido = re.compile(quita, re.DOTALL)
                    xml_string_modificado = re.sub(patron_contenido, '', texto_xml)
                else:
                    patron_contenido = re.compile(quita, re.DOTALL)
                    xml_string_modificado = re.sub(patron_contenido, '', xml_string_modificado)

        expresion_regular = '|'.join(re.escape(elemento) for elemento in datos_json['nodos'])
        resultados = re.findall(expresion_regular, texto_xml)
        self.nodos_cfdi = '||'.join(list(set(resultados)))

        if xml_string_modificado == "":
            return texto_xml
        else:
            return xml_string_modificado
    def corregir_errores(self, texto_xml, datos_json):
        xml_string_modificado = ""
        for replace in datos_json['replace']:
            separado = replace.split('||')
            replazar = separado[0]
            por = separado[1]
            if(xml_string_modificado == ""):
                xml_string_modificado = re.sub(f'{replazar}', por, texto_xml)
            else:
                xml_string_modificado = re.sub(f'{replazar}', por, xml_string_modificado)
        if xml_string_modificado == "":
            return texto_xml
        else:
            return xml_string_modificado
    def abrir_xml(self, archivo_xml):
        with open(archivo_xml, 'r', encoding='utf-8') as archivo:
            xml_string = archivo.read()
        
        with open('/home/malonso/Documentos/Proyectos/Python/Lambdas/parse_mysql/src/datos_corregir.json', 'r') as archivo:
            datos_json = json.load(archivo)
        xml_string = self.quitar_nodos(xml_string, datos_json)
        try:
            xml = etree.fromstring(xml_string)
        except Exception as e:
            xml_string = self.corregir_errores(xml_string, datos_json)
            if('Please use bytes input or XML fragments without declaration' in str(e)):
                if isinstance(xml_string, str):
                    xml_string = xml_string.encode("utf-8")
            try:
                xml = etree.fromstring(xml_string)
            except etree.XMLSyntaxError:
                try:
                    xml = etree.parse(archivo_xml)
                except etree.XMLSyntaxError:
                    parser = etree.XMLParser(recover=True)
                    xml = etree.fromstring(xml_string, parser)
            except Exception as e :
                error_info = traceback.format_exc()
                xml = "Error Abrir xml|"+str(error_info)
        return xml
    def datos_generales_nececito(self, lista, claves_deseadas):
        nuevo_diccionario = {clave: lista[clave] for clave in claves_deseadas if clave in lista}
        return nuevo_diccionario
    def parsear(self, rfc, caracter, archivo):
        #print(archivo)
        texto_archivo = self.abrir_xml(archivo)
        if('Error Abrir xml' not in texto_archivo):
            try:
                parseo_datos_generales = parseoDatosGenerales(texto_xml=texto_archivo, caracter=caracter, rfc=rfc)
                datos_generales = parseo_datos_generales.obtener_datos
                cfdi_url = parseo_datos_generales.obtener_url_cfd
                #print(datos_generales)
                if(datos_generales):
                    lista_datos_nesesito = ["rfc_principal", "emitido_recibido", "anio_emision", "mes_emision", "uuid",  "rfc_contraparte", "fecha_emision", "fecha_cert_sat", "tipo_comprobante"]
                    datos_compulsa_generales = self.datos_generales_nececito(datos_generales, lista_datos_nesesito)
                    datos_compulsa_generales['nodos']= self.nodos_cfdi
                    if(datos_generales['tipo_comprobante'] in ('I', "E")):
                        parseo_ing_egr = parseoIngresosEgresos(texto_archivo, cfdi_url, datos_generales['tipo_cambio'])
                        datos_ingresos_egresos = parseo_ing_egr.obtener_ingresos_egresos
                        if(datos_ingresos_egresos[0] != False):
                            lista_datos_nesesita = ["rfc_principal", "emitido_recibido", "anio_emision", "mes_emision", "uuid",  "rfc_contraparte", "fecha_emision", "name_principal", "name_contraparte", "fecha_cert_sat", "version", "tipo_comprobante", "serie", "folio", "lugar_expedicion", "regimen_fiscal_emisor", "regimen_fiscal_receptor", "codigo_postal_receptor", "metodo_pago", "forma_pago", "condiciones_pago", "uso_cfdi",  "inf_global_periodicidad", "inf_global_anio", "inf_global_mes",  "moneda", "tipo_cambio", "subtotal", "descuento", "total", "total_impuestos_retenidos", "total_impuestos_trasladados", "subtotal_pesos", "descuento_pesos", "total_pesos", "total_impuestos_retenidos_pesos", "total_impuestos_trasladados_pesos"]
                            datos = self.datos_generales_nececito(datos_generales, lista_datos_nesesita)
                            diccionario_combinado = {**datos, **datos_ingresos_egresos[1]}
                            self.respuesta_datos.append(['ingresos_egresos', diccionario_combinado])
                    elif(datos_generales['tipo_comprobante'] == 'P'):
                        parsea_pagos = parseoPagos(texto_archivo)
                        pagos_general = parsea_pagos.obtener_pagos
                        pagos_documentos = parsea_pagos.obtener_pagos_documentos
                        if(pagos_general[0] != False):
                            lista_datos_nesesita = ["rfc_principal", "emitido_recibido", "anio_emision", "mes_emision", "uuid",  "rfc_contraparte", "fecha_emision", "name_principal", "name_contraparte", "fecha_cert_sat", "version", "tipo_comprobante", "serie", "folio", "lugar_expedicion", "regimen_fiscal_emisor", "regimen_fiscal_receptor", "codigo_postal_receptor"]
                            datos = self.datos_generales_nececito(datos_generales, lista_datos_nesesita)
                            diccionario_combinado = {**datos, **pagos_general[1]}
                            self.respuesta_datos.append(['pagos_general', diccionario_combinado])
                        if(pagos_documentos[0] != False):
                            lista_datos_nesesita = ["rfc_principal", "emitido_recibido", "anio_emision", "mes_emision", "uuid",  "rfc_contraparte", "fecha_emision", "version"]
                            for datos_pagos_documentos in pagos_documentos:
                                datos = self.datos_generales_nececito(datos_generales, lista_datos_nesesita)
                                diccionario_combinado = {**datos, **datos_pagos_documentos}
                                self.respuesta_muchos['pagos_documentos'].append(diccionario_combinado)
                    elif(datos_generales['tipo_comprobante'] == 'N'):
                        parseo_nomina = parseoNomina(texto_archivo)
                        if(parseo_nomina.obtener_nomina!= False):
                            lista_datos_nesesita = ["rfc_principal", "emitido_recibido", "anio_emision", "mes_emision", "uuid",  "rfc_contraparte", "fecha_emision", "name_principal", "name_contraparte", "fecha_cert_sat", "version", "tipo_comprobante", "serie", "folio", "lugar_expedicion", "metodo_pago", "regimen_fiscal_emisor", "regimen_fiscal_receptor", "codigo_postal_receptor", "uso_cfdi", "moneda", "tipo_cambio", "subtotal", "descuento", "total", "forma_pago", "condiciones_pago"]
                            for datos_nomina in parseo_nomina.obtener_nomina:
                                datos = self.datos_generales_nececito(datos_generales, lista_datos_nesesita)
                                diccionario_combinado = {**datos, **datos_nomina}
                                self.respuesta_datos.append(['nomina', diccionario_combinado])

                            if parseo_nomina.obtener_detalle_nomina != False:
                                lista_datos_nesesita = ["rfc_principal", "emitido_recibido", "anio_emision", "mes_emision", "uuid",  "rfc_contraparte", "fecha_emision"]
                                for nomina_detallada in parseo_nomina.obtener_detalle_nomina:
                                    datos = self.datos_generales_nececito(datos_generales, lista_datos_nesesita)
                                    diccionario_combinado = {**datos, **nomina_detallada}
                                    self.respuesta_muchos['nomina_detallada'].append(diccionario_combinado)

                            if(parseo_nomina.obtener_incapacidades != False):
                                lista_datos_nesesita = ["rfc_principal", "emitido_recibido", "anio_emision", "mes_emision", "uuid",  "rfc_contraparte", "fecha_emision"]
                                for nomina_incapacidades in parseo_nomina.obtener_incapacidades:
                                    datos = self.datos_generales_nececito(datos_generales, lista_datos_nesesita)
                                    diccionario_combinado = {**datos, **nomina_incapacidades}
                                    self.respuesta_muchos['nomina_incapacidades'].append(diccionario_combinado)

                            if(parseo_nomina.obtener_nomina_sub_contratacion != False):
                                lista_datos_nesesita = ["rfc_principal", "emitido_recibido", "anio_emision", "mes_emision", "uuid",  "rfc_contraparte", "fecha_emision"]
                                for nomina_sub_contrataciones in parseo_nomina.obtener_nomina_sub_contratacion:
                                    datos = self.datos_generales_nececito(datos_generales, lista_datos_nesesita)
                                    diccionario_combinado = {**datos, **nomina_sub_contrataciones}
                                    self.respuesta_muchos['nomina_sub_contrataciones'].append(diccionario_combinado)
                    if(datos_generales['conceptos']):
                        lista_datos_nesesita = ["rfc_principal", "emitido_recibido", "anio_emision", "mes_emision", "uuid",  "rfc_contraparte", "fecha_emision", "subtotal", "descuento", "total", "subtotal_pesos", "descuento_pesos", "total_pesos", "tipo_comprobante", "total_impuestos_trasladados_pesos", "total_impuestos_trasladados", "total_impuestos_retenidos_pesos", "total_impuestos_retenidos"]
                        parsea_conceptos = parseoConceptos(texto_archivo, cfdi_url, datos_generales['tipo_cambio'])
                        if(parsea_conceptos.obtener_conceptos[0] != False):
                            for conceptos in parsea_conceptos.obtener_conceptos:
                                datos = self.datos_generales_nececito(datos_generales, lista_datos_nesesita)
                                diccionario_combinado = {**datos, **conceptos}
                                self.respuesta_muchos['conceptos'].append(diccionario_combinado)
                    if(datos_generales['relaciones']):
                        lista_datos_nesesita = ["rfc_principal", "emitido_recibido", "anio_emision", "mes_emision", "uuid",  "rfc_contraparte", "fecha_emision"]
                        parsea_relaciones = parseoRelaciones(texto_archivo, cfdi_url)
                        if(parsea_relaciones.obtener_relaciones[0] != False):
                            for relaciones in parsea_relaciones.obtener_relaciones:
                                datos = self.datos_generales_nececito(datos_generales, lista_datos_nesesita)
                                diccionario_combinado = {**datos, **relaciones}
                                self.respuesta_muchos['relaciones'].append(diccionario_combinado)
                    return [True, datos_compulsa_generales]
                else:
                    return [False, "Parsear xml", "No se obtubieron datos del CFDI"]
            except Exception:
                error_info = traceback.format_exc()
                return [False, "Parsear xml", str(error_info)]
        else:
            return [False, "Abrir archivo xml", texto_archivo.split('|')[1]]
def limpia_cadena_errores(error):
    error = error.replace("'", "")
    error = error.replace('"', "")
    return error
def errores_base(error_app):
    error_app = str(error_app.replace("'", "")).upper()
    resp_error = False
    errores_volver = ['UNABLE TO COMPLETE OPERATION', 'CLIENT REQUEST TIMEOUT. SEE', 'UNABLE TO COMPLETE THE OPERATION', 'HOST', 'TIMEOUT', 'NONETYPE OBJECT HAS NO ATTRIBUTE EXECUTE', 'DUPLICATE ENTRY']
    #Errores de conexion
    for error in errores_volver:
        if error in error_app:
            #Para volver a enviar a cola de listo
            resp_error = True
    return resp_error
def obtener_tamano_archivo(ruta_archivo):
    if os.path.exists(ruta_archivo):
        tamano_bytes = os.path.getsize(ruta_archivo)
        tamano_mb = tamano_bytes / (1024 * 1024)
        return tamano_mb
    else:
        return 0
def envia_mensajes_error(error, data, class_sqs):
    error = str(error)
    if(not error or errores_base(error)):
        print("Error al enviar mensaje base", json.dumps(data))
    else:
        print("ERROR", data, error)
        data["msg"] = 'Error no controlado'
        data["error"] = limpia_cadena_errores(error)
        print("Error al enviar mensaje", data)
def registra_cfdi_si_o_no(datos_parseo, conexion, data, class_sqs, class_aws, archivo):
    datos_nesesito ='fecha_parseado_archivado, rfc_principal'
    tabla = "compulsa"
    where = f"rfc_principal = '{datos_parseo['rfc_principal']}' and emitido_recibido = '{datos_parseo['emitido_recibido']}' AND anio_emision = {datos_parseo['anio_emision']} and mes_emision = {datos_parseo['mes_emision']} AND uuid = '{datos_parseo['uuid']}' "
    result = conexion.mysql_query(datos_nesesito, tabla, where)
    if(result[0] == True):
        siparseo = ''
        sihay_datos = ''
        for fila in result[1]:
            siparseo = fila.get("fecha_parseado_archivado")
            sihay_datos  = fila.get("rfc_principal")
        registra_compulsa = True
        if(sihay_datos == ''):
            #Registramos en compulsa
            registra_compulsa = conexion.insert(datos_parseo, 'compulsa')
        if siparseo == '' or siparseo == None:
            if(registra_compulsa == True):
                return True
            else:
                print("ERRO4", registra_compulsa)
                envia_mensajes_error(registra_compulsa, data, class_sqs)
        else:
            #print("ya esta registrado", archivo)
            #class_aws.elimina_archivo(data['arn'])
            try:
                os.remove(archivo)
            except Exception:
                pass
            return False  
    else:
        print("ERRO10", result[1])
        envia_mensajes_error(result[1], data, class_sqs)
        return False
def registra_informacion(datos, tabla, class_conexion):
    registra_base = True
    if(len(datos)>0):
        if(len(datos)>10000):
            res = class_conexion.insert_muchos(datos, tabla)
            if(res == True):
                registra_base = True
            else:
                registra_base = res
        else:
            for dato in datos:
                res = class_conexion.insert(dato, tabla)
                if(res == True):
                    registra_base = True
                else:
                    registra_base = res
                    break
    return registra_base
def obtener_archivos_de_carpeta(carpeta_origen, caracter, rfc_parametro):
    archivos = []
    for root, dirs, files in os.walk(carpeta_origen):
        for file in files:
            if file.endswith('.xml'):
                # Obtener partes de la ruta para construir la información deseada
                ruta_archivo = os.path.join(root, file)
                
                # Construir el diccionario con la información requerida
                archivo_info = {
                    "arn": ruta_archivo,
                    "rfc": rfc_parametro,
                    "caracter": caracter
                }
                
                archivos.append(archivo_info)
    
    return archivos

def ok_parseo(data, fecha_mensaje, class_sqs, ruta_descarga, class_aws):
    with funcionesMySQL() as class_conexion:
        #data = json.loads(record['body'])
        #id_elimina = data['id_elimina']
        if class_conexion is None or class_conexion is  False:
            cola = 'listoXml'
            if(class_conexion is False):
                cola = 'parseo_many_conexiones'
            print("conexion", class_conexion)
            if(class_sqs.envia_msg(json.dumps(data), cola) != True):
                print("Error al enviar mensaje archivo grande", json.dumps(data))
            return
        rfc = data['rfc']
        caracter = data['caracter']
        arn_archivo = data['arn']
        #print(arn_archivo)
        nombre_archivo = os.path.basename(arn_archivo)
        archivo = f'{ruta_descarga}{nombre_archivo}'

        #print(nombre_archivo, obtener_tamano_archivo(archivo))
        try:
            #DESCARGA CFDI
            #descargo_archivo = class_aws.descargar_archivo(arn_archivo, archivo)
            descargo_archivo = True
            if(descargo_archivo == True):
                class_app = app()
                resp_parseo = class_app.parsear(rfc, caracter, archivo)
                if(resp_parseo[0] == True):
                    datos_parseo = resp_parseo[1]
                    if(datos_parseo['uuid'] !='00000000-0000-0000-0000-000000000000'):
                        resul_consulta = registra_cfdi_si_o_no(datos_parseo, class_conexion, data, class_sqs, class_aws, archivo)
                        if(resul_consulta):
                                tablas = []
                                tablas.append('compulsa')
                                registro_base_tabla_principal = True
                                registro_base_tabla_detalladas = True
                                if(datos_parseo['tipo_comprobante'].upper() != 'T'):
                                    #print(class_app.datos_cfdis())
                                    datos_cfdi = class_app.datos_cfdis()
                                    if(datos_cfdi != False):
                                        for tabla, datos_cfdi in class_app.datos_cfdis():
                                            tablas.append(tabla)
                                            resp_registro = registra_informacion([datos_cfdi], tabla, class_conexion)
                                            if(resp_registro != True):
                                                registro_base_tabla_principal = resp_registro
                                                break
                                    if(registro_base_tabla_principal):
                                        datos_detallados = class_app.datos_detallados_cfdi()
                                        #print(datos_detallados)
                                        if(datos_detallados != False):
                                            for tabla, datos in datos_detallados.items():
                                                tablas.append(tabla)
                                                resp_registro = registra_informacion(datos, tabla, class_conexion)
                                                if(resp_registro != True):
                                                    registro_base_tabla_detalladas = resp_registro
                                                    break
                                if(registro_base_tabla_principal == True and registro_base_tabla_detalladas == True):
                                    arn_final = f"CFDIS/{rfc}/{caracter}/{datos_parseo['tipo_comprobante'].upper()}/{datos_parseo['anio_emision']}/{datos_parseo['mes_emision']}/{datos_parseo['uuid']}.xml"
                                    fecha_parseo = datetime.now()
                                    datos = {"arn_archivo_xml": arn_final, "fecha_parseado_archivado": fecha_parseo, "fecha_descargado": fecha_parseo, "version_parseo": os.environ['VERSION_PAGO'], "nodos": datos_parseo['nodos']}
                                    where_update = f"rfc_principal = '{datos_parseo['rfc_principal']}' and emitido_recibido = '{datos_parseo['emitido_recibido']}' AND anio_emision = {datos_parseo['anio_emision']} and mes_emision = {datos_parseo['mes_emision']} AND uuid = '{datos_parseo['uuid']}'"
                                    
                                    if(class_conexion.mysql_update(datos, 'compulsa', where_update) == True):
                                        #Funciono todo lo de la base de datos Vamos a subir a s3
                                        msg = {"caracter": caracter, "rfc": rfc, "anio_emision": datos_parseo['anio_emision'], "mes_emision": datos_parseo['mes_emision'], "uuid": datos_parseo['uuid'], "tipo_comprobante": datos_parseo['tipo_comprobante'].upper()}
                                        #resp_subir_archivo = class_aws.subir_archivo(archivo, arn_final)
                                        resp_subir_archivo = True
                                        if(resp_subir_archivo == True):
                                            try:
                                                os.remove(archivo)
                                            except Exception:
                                                pass
                                            #class_aws.elimina_archivo(arn_archivo)
                                            #print(arn_final)
                                            #class_sqs.eliminar_msg(id_elimina, 'listoXml') 
                                            #class_sqs.envia_msg(json.dumps(msg), "confirmaParseo")
                                        else:
                                            msg['archivo'] = archivo
                                            msg['msg_error'] = limpia_cadena_errores(resp_subir_archivo)
                                            if(class_sqs.envia_msg(json.dumps(msg), "parseoErrorSubirArchivo")!= True):
                                                print("ERROR al enviar mensaje parseo error", json.dumps(msg))
                                    else:
                                        for tabla in tablas:
                                            where = f"rfc_principal = '{datos_parseo['rfc_principal']}' and emitido_recibido = '{datos_parseo['emitido_recibido']}' AND anio_emision = {datos_parseo['anio_emision']} and mes_emision = {datos_parseo['mes_emision']} AND uuid = '{datos_parseo['uuid']}'"
                                            class_conexion.delete_mysql(tabla, where)
                                        mensaje_error = ""
                                        if(registro_base_tabla_principal != True):
                                            mensaje_error = registro_base_tabla_principal
                                        elif(registro_base_tabla_detalladas != True):
                                            mensaje_error = registro_base_tabla_detalladas
                                        else:
                                            mensaje_error = str(registro_base_tabla_principal)+str(registro_base_tabla_detalladas)
                                        print("ERROR1", registro_base_tabla_detalladas, registro_base_tabla_principal)
                                        if('Duplicate entry' in mensaje_error):
                                            class_sqs.envia_msg(json.dumps(data), "listoXml")
                                        else:
                                            envia_mensajes_error(mensaje_error, data, class_sqs)
                                else:
                                    for tabla in tablas:
                                        where = f"rfc_principal = '{datos_parseo['rfc_principal']}' and emitido_recibido = '{datos_parseo['emitido_recibido']}' AND anio_emision = {datos_parseo['anio_emision']} and mes_emision = {datos_parseo['mes_emision']} AND uuid = '{datos_parseo['uuid']}'"
                                        class_conexion.delete_mysql(tabla, where)
                                    mensaje_error = ""
                                    if(registro_base_tabla_principal != True):
                                        mensaje_error = registro_base_tabla_principal
                                    elif(registro_base_tabla_detalladas != True):
                                        mensaje_error = registro_base_tabla_detalladas
                                    else:
                                        mensaje_error = str(registro_base_tabla_principal)+str(registro_base_tabla_detalladas)
                                    print("ERROR2", registro_base_tabla_detalladas, registro_base_tabla_principal)
                                    if('Duplicate entry' in mensaje_error):
                                        class_sqs.envia_msg(json.dumps(data), "listoXml")
                                    else:
                                        envia_mensajes_error(mensaje_error, data, class_sqs)
                    else:
                        data['msg']='Este pararece con el uuid: 00000000-0000-0000-0000-000000000000'
                        class_sqs.envia_msg(json.dumps(data), "parseo_xml_sin_uuid")
                else:
                    print("Error parseo", resp_parseo[1], resp_parseo[2])
                    msg = {"msg": resp_parseo[2], "arn": arn_archivo, "rfc": rfc, "error": limpia_cadena_errores(resp_parseo[2])}
                    print("ERROR al enviar mensaje parseo", msg)
                #tamaño en megas
                
            else:
                
                if descargo_archivo == False:
                    #print("archivo descargado", descargo_archivo)
                    #class_sqs.eliminar_msg(id_elimina, 'listoXml')
                    pass
                elif(descargo_archivo == '503'):
                    data["msg"] = "No se pudo hacer la descarga: 503"
                    class_sqs.envia_msg(json.dumps(data), "parseo_many_conexiones")
                #No se pudo hacer la descarga
                else:
                    print('No se pudo hacer la descarga', str(descargo_archivo), arn_archivo)
                    msg = {"msg": "No de descargo el cfdi", "arn": arn_archivo, "rfc": rfc, "error": limpia_cadena_errores(descargo_archivo)}
                    if(class_sqs.envia_msg(msg, 'parseoError') != True):
                        print("Error al enviar mensaje descarga", msg)
                
        except Exception:
            error_info = traceback.format_exc()
            print(error_info, '1')
            envia_mensajes_error(error_info, data, class_sqs)
def lambda_handler(event, context):
    class_sqs = mensajesSQS()
    class_aws = awsS3()
    fecha_mensaje = ""
    #print("aqui")'', ''
    for cliente, anio, rfc_parametro in [['CENAGAS', 2024, 'CNC140829256']]:
        for caracter in ['RECIBIDO', 'EMITIDO']:
            print(cliente, caracter, rfc_parametro, anio)
            carpeta_origen = f'/tmp/{cliente}/{rfc_parametro}/{anio}/{caracter}/'
            archivos_a_procesar = obtener_archivos_de_carpeta(carpeta_origen, caracter, rfc_parametro)
            ruta_descarga = f'/tmp/{cliente}/{rfc_parametro}/{anio}/{caracter}/'
            num_threads = 10  # Puedes ajustar este número según el número de hilos que desees
            with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
                futures = []
                for data in archivos_a_procesar:
                    futures.append(executor.submit(ok_parseo, data, fecha_mensaje, class_sqs, ruta_descarga, class_aws))

                # Esperar a que todos los futuros se completen
                for future in concurrent.futures.as_completed(futures):
                    try:
                        future.result()
                    except Exception as e:
                        print(f"Error al procesar un archivo: {e}")
            
def main():
    lambda_handler(None, None)

if __name__ == "__main__":
    ini_proc = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    main()
    fin_proc = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    diferencia_de_tiempo = ((datetime.strptime(fin_proc, "%Y-%m-%d %H:%M:%S")) - (datetime.strptime(ini_proc, "%Y-%m-%d %H:%M:%S")))
        
    diferencia_en_horas = int(diferencia_de_tiempo.total_seconds() // 3600)
    diferencia_en_minutos = int((diferencia_de_tiempo.total_seconds() % 3600) // 60)
    diferencia_en_segundos = int(diferencia_de_tiempo.total_seconds() % 60)

    if diferencia_en_horas > 0:
        if diferencia_en_minutos > 0:
            print(f"Pasaron {diferencia_en_horas} horas, {diferencia_en_minutos} minutos y {diferencia_en_segundos} segundos.")
        else:
            print(f"Pasaron {diferencia_en_horas} horas y {diferencia_en_segundos} segundos.")
    else:
        print(f"Pasaron {diferencia_en_minutos} minutos y {diferencia_en_segundos} segundos.")  
