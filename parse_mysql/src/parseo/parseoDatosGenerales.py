from parseo.manipudorDatos import manipudorDatos
import os, re
import datetime
from lxml import etree

class parseoDatosGenerales(manipudorDatos):

    def __init__(self, texto_xml, caracter, rfc):
        self._caracter = caracter
        self._rfc = rfc
        self.texto_xml = texto_xml
        self._respuesta = {}
        self._cfdi_url = ""
        self.urlis_cfdis()
        self.parseo_datos()
        
    @property
    def obtener_datos(self):
        return self._respuesta
    @property
    def obtener_url_cfd(self):
        return self._cfdi_url
    def parseo_datos(self):
        uuid = ""
        fecha_timbrado = ""
        timbre_digital = self.texto_xml.xpath('//tfd:TimbreFiscalDigital', namespaces={"tfd": "http://www.sat.gob.mx/TimbreFiscalDigital"})
        if(timbre_digital):
            for datos in timbre_digital:
                uuid = self.limpiar_cadenas(datos.get('UUID', "00000000-0000-0000-0000-000000000000")).upper()
                fecha_timbrado = self.convertir_date(self.limpiar_cadenas(datos.get('FechaTimbrado', "")))
        else:
            xml_string = etree.tostring(self.texto_xml, encoding='unicode')
            uuid_pattern = re.compile(r'UUID="([^"]+)"')
            fecha_timbrado_pattern = re.compile(r'FechaTimbrado="([^"]+)"')
            uuid_match = uuid_pattern.search(xml_string)
            fecha_timbrado_match = fecha_timbrado_pattern.search(xml_string)
            if uuid_match and fecha_timbrado_match:
                uuid = uuid_match.group(1).upper()
                fecha_timbrado = fecha_timbrado_match.group(1)
            else:
                uuid = "00000000-0000-0000-0000-000000000000"
                fecha_timbrado = "1900-01-01T00:00:00"
        impuestos = self.parsea_impuestos(self.texto_xml.xpath('//cfdi:Comprobante/cfdi:Impuestos', namespaces={"cfdi": self._cfdi_url}))
        relacionados = False
        conceptos = False
        if (self.texto_xml.find('.//cfdi:CfdiRelacionado', namespaces={"cfdi": self._cfdi_url}) is not None):
            relacionados = True
        if (self.texto_xml.find('.//cfdi:Concepto', namespaces={"cfdi": self._cfdi_url}) is not None):
            conceptos = True
        datos_comprobante = self.texto_xml.xpath('//cfdi:Comprobante', namespaces={"cfdi": self._cfdi_url})
        version = ""
        tipo_comprobante = ""
        serie = ""
        folio = ""
        lugar_expedicion = ""
        metodo_pago = ""
        forma_pago = ""
        condicion_pago =""
        moneda = ""
        tipo_cambio = 0
        subtotal = 0
        descuento = 0
        total = 0
        for comprobante in datos_comprobante:
            fecha_emision = self.convertir_date(self.limpiar_cadenas(comprobante.get('Fecha', "")))
            anio = int(fecha_emision.strftime('%Y'))
            mes = int(fecha_emision.strftime('%m'))
            version = self.limpiar_cadenas(comprobante.get('Version', ""))
            tipo_comprobante = self.limpiar_cadenas(comprobante.get('TipoDeComprobante', ""))
            serie = self.limpiar_cadenas(comprobante.get('Serie', ""))
            folio = self.limpiar_cadenas(comprobante.get('Folio', ""))
            lugar_expedicion = self.limpiar_cadenas(comprobante.get('LugarExpedicion', ""))
            metodo_pago = self.limpiar_cadenas(comprobante.get('MetodoPago', ""))
            forma_pago = self.limpiar_cadenas(comprobante.get('FormaPago', ""))
            condicion_pago = self.limpiar_cadenas(comprobante.get('CondicionesDePago', ""))
            moneda = self.limpiar_cadenas(comprobante.get("Moneda", ""))
            tipo_cambio = self.convertir_float(comprobante.get("TipoCambio", ""))
            if (moneda == 'MXN'):
                tipo_cambio = 1
            subtotal = self.convertir_float(comprobante.get("SubTotal", ""))
            descuento = self.convertir_float(comprobante.get("Descuento", ""))
            total = self.convertir_float(comprobante.get("Total", ""))

            datos_emisor = self.parsea_datos_emisor(comprobante.xpath('cfdi:Emisor', namespaces={"cfdi": self._cfdi_url}))
            try:
                datos_receptor = self.parsea_datos_receptor(comprobante.xpath('cfdi:Receptor', namespaces={"cfdi": self._cfdi_url}))
            except Exception:
                datos_receptor = ["", "", 0, 0, ""]
            if (self.texto_xml.find('cfdi:InformacionGlobal', namespaces={"cfdi": self._cfdi_url}) is not None):
                informacion_global = self.parsea_datos_informacion_global(comprobante.xpath('cfdi:InformacionGlobal', namespaces={"cfdi": self._cfdi_url}))
            else:
                informacion_global = ["", 0, 0]
            
            subtotal_pesos = self.convertir_a_pesos(tipo_cambio, subtotal)
            descuento_pesos =  self.convertir_a_pesos(tipo_cambio, descuento)
            total_pesos =  self.convertir_a_pesos(tipo_cambio, total)
            total_imp_retenidos_pesos =  self.convertir_a_pesos(tipo_cambio, impuestos[0])
            total_imp_trasladados_pesos =  self.convertir_a_pesos(tipo_cambio, impuestos[1])

            rfc_principal = datos_receptor[0]
            rfc_contraparte = datos_emisor[0]
            name_contraparte = datos_emisor[1]
            name_principal = datos_receptor[1]
            letra_caracter = 'R'
            if(self._caracter == 'EMITIDO' and self._rfc == datos_emisor[0]):
                rfc_principal = datos_emisor[0]
                rfc_contraparte = datos_receptor[0]
                name_contraparte = datos_receptor[1]
                name_principal = datos_emisor[1]
                letra_caracter = 'E'
            self._respuesta  = {"estatus": True, "uuid": uuid, "fecha_emision": fecha_emision, "rfc_principal": rfc_principal, "rfc_contraparte": rfc_contraparte, "name_contraparte": self.limitar_cadena(name_contraparte, 600), "name_principal": self.limitar_cadena(name_principal, 600), "fecha_cert_sat": fecha_timbrado, "version": version, "tipo_comprobante": tipo_comprobante, "serie": serie, "folio": folio, "lugar_expedicion": lugar_expedicion, "metodo_pago": metodo_pago, "forma_pago": forma_pago, "condiciones_pago": self.limitar_cadena(condicion_pago, 1200), "regimen_fiscal_emisor": datos_emisor[2], "regimen_fiscal_receptor": datos_receptor[2], "codigo_postal_receptor": datos_receptor[3], "uso_cfdi": datos_receptor[4], "inf_global_periodicidad": informacion_global[0], "inf_global_anio": informacion_global[1], "inf_global_mes": informacion_global[2], "moneda": moneda, "tipo_cambio": tipo_cambio, "subtotal": self.decimal_2(subtotal), "descuento": self.decimal_2(descuento), "total": self.decimal_2(total), "total_impuestos_retenidos": self.decimal_2(impuestos[0]), "total_impuestos_trasladados": self.decimal_2(impuestos[1]), "subtotal_pesos": self.decimal_2(subtotal_pesos), "descuento_pesos": self.decimal_2(descuento_pesos), "total_pesos": self.decimal_2(total_pesos), "total_impuestos_retenidos_pesos": self.decimal_2(total_imp_retenidos_pesos), "total_impuestos_trasladados_pesos": self.decimal_2(total_imp_trasladados_pesos), "relaciones": relacionados, "conceptos": conceptos, "anio_emision": anio, "mes_emision": mes, "emitido_recibido": letra_caracter}
    def urlis_cfdis(self):
        # Obtenemos la URL del cfdi para el namespaces y poder parsear
        urls_cfdis = os.environ['URL_CFDIs'].split('||')
        try:
            namespaces = self.texto_xml.nsmap
        except Exception:
            root = self.texto_xml.getroot()
            namespaces = root.nsmap
        urls = ""
        ver_cfdi = ""
        for prefix, uri in namespaces.items():
            if (prefix == 'cfdi' or prefix == None):
                if(uri == ""):
                    continue
                ver_cfdi = uri
                urls += " "+ uri
        if(ver_cfdi.strip() != ""):
            for url in urls_cfdis:
                if(url in urls and url):
                    ver_cfdi = url
        self._cfdi_url = ver_cfdi
    def parsea_datos_emisor(self, datos_emisor):
        rfc_emisor = ""
        name_emisor = ""
        regimen_fiscal_emisor = 0
        for emisor in datos_emisor:
            rfc_emisor = self.limpiar_cadenas(emisor.get('Rfc', ""))
            name_emisor = self.limpiar_cadenas(emisor.get('Nombre', ""))
            regimen_fiscal_emisor = self.convertir_int(emisor.get('RegimenFiscal', ""))
        return [rfc_emisor, name_emisor, regimen_fiscal_emisor]
    def parsea_datos_receptor(self, datos_receptor):
        for receptor in datos_receptor:
            rfc_receptor = self.limpiar_cadenas(receptor.get('Rfc', ""))
            name_receptor = self.limpiar_cadenas(receptor.get('Nombre', ""))
            regimen_fiscal_receptor = self.convertir_int(receptor.get('RegimenFiscalReceptor', ""))
            cod_domicilio_receptor = self.convertir_int(receptor.get('DomicilioFiscalReceptor', ""))
            uso_cfdi = self.limpiar_cadenas(receptor.get('UsoCFDI', ""))
            return [rfc_receptor, name_receptor, regimen_fiscal_receptor, cod_domicilio_receptor, uso_cfdi]
    def parsea_datos_informacion_global(self, informacion_global):
        for info in informacion_global:
            infglob_periodicidad = self.limpiar_cadenas(info.get('Periodicidad', ""))
            infglob_meses = self.convertir_int(info.get('Meses', ""))
            infglob_anio = self.convertir_int(info.get('Año', ""))
            return[infglob_periodicidad, infglob_anio, infglob_meses]
    def parsea_impuestos(self, impuestos):
        total_impuestos_retenidos = 0
        total_impuestos_trasladados = 0
        for impuesto in impuestos:
            total_impuestos_retenidos = self.convertir_float(impuesto.get("TotalImpuestosRetenidos", ""))
            total_impuestos_trasladados = self.convertir_float(impuesto.get("TotalImpuestosTrasladados", ""))
        return [total_impuestos_retenidos, total_impuestos_trasladados]