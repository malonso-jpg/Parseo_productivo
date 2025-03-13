from parseo.manipudorDatos import manipudorDatos
from parseo.parseoIngresosEgresos import parseoIngresosEgresos
class parseoConceptos(manipudorDatos):

    def __init__(self, texto_xml = "", cfdi_url = "", tipo_cambio = 0):
        self.texto_xml = texto_xml
        self._cfdi_url = cfdi_url
        self._tipo_cambio = tipo_cambio
        self._respuesta = []
        self.parseo_conceptos()
    @property
    def obtener_conceptos(self):
        return self._respuesta
    
    def parseo_a_cuenta_terceros(self, datos_a_cuenta):
        rfc_a_cuenta_terceros = ""
        name_a_cuenta_terceros = ""
        regimen_fical_a_cuenta_terceros = ""
        domicilio_ficas_a_cuenta_terceros = ""
        for datos in datos_a_cuenta:
            rfc_a_cuenta_terceros = self.limpiar_cadenas(datos.get("RfcACuentaTerceros", ""))
            name_a_cuenta_terceros = self.limpiar_cadenas(datos.get("NombreACuentaTerceros", ""))
            regimen_fical_a_cuenta_terceros = self.limpiar_cadenas(datos.get("RegimenFiscalACuentaTerceros", ""))
            domicilio_ficas_a_cuenta_terceros = self.limpiar_cadenas(datos.get("DomicilioFiscalACuentaTerceros", ""))
        return {"rfc_a_cuenta_terceros": rfc_a_cuenta_terceros, "name_a_cuenta_terceros": name_a_cuenta_terceros, "regimen_fical_a_cuenta_terceros": regimen_fical_a_cuenta_terceros, "domicilio_ficas_a_cuenta_terceros": domicilio_ficas_a_cuenta_terceros}
    def parseo_conceptos(self):
        list_conceptos = self.texto_xml.xpath('//cfdi:Conceptos', namespaces={"cfdi": self._cfdi_url})
        noobject_impuestos = 0
        for conceptos in list_conceptos:
            de_cuantos = int(conceptos.xpath("count(//cfdi:Concepto)", namespaces={"cfdi": self._cfdi_url}))
            list_concepto = conceptos.xpath('cfdi:Concepto', namespaces={"cfdi": self._cfdi_url})
            num = 1
            for concepto in list_concepto:
                clave_prod_serv = self.limpiar_cadenas(concepto.get('ClaveProdServ', ""))
                cantidad = self.convertir_float(concepto.get("Cantidad", ""))
                clave_unidad = self.limpiar_cadenas(concepto.get("ClaveUnidad", ""))
                unidad = self.limpiar_cadenas(concepto.get("Unidad", ""))
                no_identificacion = self.limpiar_cadenas(concepto.get("NoIdentificacion", ""))
                descripcion = self.limpiar_cadenas(concepto.get("Descripcion", ""))
                valor_unitario = self.convertir_float(concepto.get("ValorUnitario", ""))
                importe_concepto = self.convertir_float(concepto.get("Importe", ""))
                descuento_concepto = self.convertir_float(concepto.get("Descuento", ""))
                num_pedimento = self.limpiar_cadenas(concepto.get("NumeroPedim", ""))
                num_cuenta_predial = self.convertir_int(concepto.get("NumeroCuentaPredial", ""))
                objeto_imp = self.limpiar_cadenas(concepto.get("ObjetoImp", ""))
                if (objeto_imp in ('01', '02', '03', '04', '05')):
                    noobject_impuestos = (noobject_impuestos + importe_concepto)
                pie = parseoIngresosEgresos()
                impuestos_traslados = pie.parseo_impuestos_trasladados(concepto.xpath('cfdi:Impuestos/cfdi:Traslados/cfdi:Traslado', namespaces={"cfdi": self._cfdi_url}))
                impuestos_retenciones = pie.parseo_impuestos_retenidos(concepto.xpath('cfdi:Impuestos/cfdi:Retenciones/cfdi:Retencion', namespaces={"cfdi": self._cfdi_url}))
                exentos_base = impuestos_traslados['exentos_base']
                exentos_importe = impuestos_traslados['exentos_importe']
                tasa_0_base = impuestos_traslados['tasa_0_base']
                tasa_0_importe = impuestos_traslados['tasa_0_importe']
                tasa_8_base = impuestos_traslados['tasa_8_base']
                tasa_8_importe = impuestos_traslados['tasa_8_importe']
                tasa_16_base = impuestos_traslados['tasa_16_base']
                tasa_16_importe = impuestos_traslados['tasa_16_importe']
                base_ieps_tasa_traslado = impuestos_traslados['base_ieps_tasa_traslado']
                importe_ieps_tasa_traslado = impuestos_traslados['importe_ieps_tasa_traslado']
                base_ieps_cuota_traslado = impuestos_traslados['base_ieps_cuota_traslado']
                importe_ieps_cuota_traslado = impuestos_traslados['importe_ieps_cuota_traslado']
                retenciones_base_iva = impuestos_retenciones['retenciones_base_iva']
                retenciones_importe_iva = impuestos_retenciones['retenciones_importe_iva']
                retenciones_base_isr = impuestos_retenciones['retenciones_base_isr']
                retenciones_importe_isr = impuestos_retenciones['retenciones_importe_isr']
                base_ieps_tasa_retencion = impuestos_retenciones['base_ieps_tasa_retencion']
                importe_ieps_tasa_retencion = impuestos_retenciones['importe_ieps_tasa_retencion']
                base_ieps_cuota_retencion = impuestos_retenciones['base_ieps_cuota_retencion']
                importe_ieps_cuota_retencion = impuestos_retenciones['importe_ieps_cuota_retencion']

                noobject_impuestos_pesos = self.convertir_a_pesos(self._tipo_cambio, noobject_impuestos)
                importe_concepto_pesos = self.convertir_a_pesos(self._tipo_cambio, importe_concepto)
                descuento_concepto_pesos = self.convertir_a_pesos(self._tipo_cambio, descuento_concepto)
                exentos_base_pesos = self.convertir_a_pesos(self._tipo_cambio, exentos_base)
                exentos_importe_pesos = self.convertir_a_pesos(self._tipo_cambio, exentos_importe)
                tasa_0_base_pesos = self.convertir_a_pesos(self._tipo_cambio, tasa_0_base)
                tasa_0_importe_pesos = self.convertir_a_pesos(self._tipo_cambio, tasa_0_importe)
                tasa_8_base_pesos = self.convertir_a_pesos(self._tipo_cambio, tasa_8_base)
                tasa_8_importe_pesos = self.convertir_a_pesos(self._tipo_cambio, tasa_8_importe)
                tasa_16_base_pesos = self.convertir_a_pesos(self._tipo_cambio, tasa_16_base)
                tasa_16_importe_pesos = self.convertir_a_pesos(self._tipo_cambio, tasa_16_importe)
                base_ieps_tasa_traslado_pesos = self.convertir_a_pesos(self._tipo_cambio, base_ieps_tasa_traslado)
                importe_ieps_tasa_traslado_pesos = self.convertir_a_pesos(self._tipo_cambio, importe_ieps_tasa_traslado)
                base_ieps_cuota_traslado_pesos = self.convertir_a_pesos(self._tipo_cambio, base_ieps_cuota_traslado)
                importe_ieps_cuota_traslado_pesos = self.convertir_a_pesos(self._tipo_cambio, importe_ieps_cuota_traslado)
                retenciones_base_iva_pesos = self.convertir_a_pesos(self._tipo_cambio, retenciones_base_iva)
                retenciones_importe_iva_pesos = self.convertir_a_pesos(self._tipo_cambio, retenciones_importe_iva)
                retenciones_base_isr_pesos = self.convertir_a_pesos(self._tipo_cambio, retenciones_base_isr)
                retenciones_importe_isr_pesos = self.convertir_a_pesos(self._tipo_cambio, retenciones_importe_isr)
                base_ieps_tasa_retencion_pesos = self.convertir_a_pesos(self._tipo_cambio, base_ieps_tasa_retencion)
                importe_ieps_tasa_retencion_pesos = self.convertir_a_pesos(self._tipo_cambio, importe_ieps_tasa_retencion)
                base_ieps_cuota_retencion_pesos = self.convertir_a_pesos(self._tipo_cambio, base_ieps_cuota_retencion)
                importe_ieps_cuota_retencion_pesos = self.convertir_a_pesos(self._tipo_cambio, importe_ieps_cuota_retencion)

                datos_a_terceros = self.parseo_a_cuenta_terceros(concepto.xpath('cfdi:ACuentaTerceros', namespaces={"cfdi": self._cfdi_url}))
                datos = {"cuantos_conceptos": de_cuantos, "num_concepto": num, "clave_prod_serv": clave_prod_serv, "cantidad": self.decimal_5(cantidad), "clave_unidad": clave_unidad, "unidad": unidad, "descripcion": self.limitar_cadena(descripcion, 1200), "valor_unitario": self.decimal_5(valor_unitario), "importe_concepto": self.decimal_2(importe_concepto), "descuento_concepto": self.decimal_2(descuento_concepto), "numero_pedimento": num_pedimento, "numero_cta_predial": num_cuenta_predial, "objetoimp": objeto_imp, "noobjetos_impuestos": self.decimal_2(noobject_impuestos), "tasa_e_base": self.decimal_2(exentos_base), "tasa_e_iva": self.decimal_2(exentos_importe), "tasa_0_base": self.decimal_2(tasa_0_base), "tasa_0_iva": self.decimal_2(tasa_0_importe), "tasa_8_base": self.decimal_2(tasa_8_base), "tasa_8_iva": self.decimal_2(tasa_8_importe), "tasa_16_base": self.decimal_2(tasa_16_base), "tasa_16_iva": self.decimal_2(tasa_16_importe), "trasladado_ieps_base_tasa": self.decimal_2(base_ieps_tasa_traslado), "trasladado_ieps_importe_tasa": self.decimal_2(importe_ieps_tasa_traslado), "trasladado_ieps_base_cuota": self.decimal_2(base_ieps_cuota_traslado), "trasladado_ieps_importe_cuota": self.decimal_2(importe_ieps_cuota_traslado), "retenciones_iva_base": self.decimal_2(retenciones_base_iva), "retenciones_iva_importe": self.decimal_2(retenciones_importe_iva), "retenciones_isr_base": self.decimal_2(retenciones_base_isr), "retenciones_isr_importe": self.decimal_2(retenciones_importe_isr), "retenciones_ieps_base_tasa": self.decimal_2(base_ieps_tasa_retencion), "retenciones_ieps_importe_tasa": self.decimal_2(importe_ieps_tasa_retencion), "retenciones_ieps_base_cuota": self.decimal_2(base_ieps_cuota_retencion), "retenciones_ieps_importe_cuota": self.decimal_2(importe_ieps_cuota_retencion), "noobjetos_impuestos_pesos": self.decimal_2(noobject_impuestos_pesos), "importe_concepto_pesos": self.decimal_2(importe_concepto_pesos), "descuento_concepto_pesos": self.decimal_2(descuento_concepto_pesos), "tasa_e_base_pesos": self.decimal_2(exentos_base_pesos), "tasa_e_iva_pesos": self.decimal_2(exentos_importe_pesos), "tasa_0_base_pesos": self.decimal_2(tasa_0_base_pesos), "tasa_0_iva_pesos": self.decimal_2(tasa_0_importe_pesos), "tasa_8_base_pesos": self.decimal_2(tasa_8_base_pesos), "tasa_8_iva_pesos": self.decimal_2(tasa_8_importe_pesos), "tasa_16_base_pesos": self.decimal_2(tasa_16_base_pesos), "tasa_16_iva_pesos": self.decimal_2(tasa_16_importe_pesos), "trasladado_ieps_base_tasa_pesos": self.decimal_2(base_ieps_tasa_traslado_pesos), "trasladado_ieps_importe_tasa_pesos": self.decimal_2(importe_ieps_tasa_traslado_pesos), "trasladado_ieps_base_cuota_pesos": self.decimal_2(base_ieps_cuota_traslado_pesos), "trasladado_ieps_importe_cuota_pesos": self.decimal_2(importe_ieps_cuota_traslado_pesos), "retenciones_iva_base_pesos": self.decimal_2(retenciones_base_iva_pesos), "retenciones_iva_importe_pesos": self.decimal_2(retenciones_importe_iva_pesos), "retenciones_isr_base_pesos": self.decimal_2(retenciones_base_isr_pesos), "retenciones_isr_importe_pesos": self.decimal_2(retenciones_importe_isr_pesos), "retenciones_ieps_base_tasa_pesos": self.decimal_2(base_ieps_tasa_retencion_pesos), "retenciones_ieps_importe_tasa_pesos": self.decimal_2(importe_ieps_tasa_retencion_pesos), "retenciones_ieps_base_cuota_pesos": self.decimal_2(base_ieps_cuota_retencion_pesos), "retenciones_ieps_importe_cuota_pesos": self.decimal_2(importe_ieps_cuota_retencion_pesos), "rfc_a_cuenta_terceros": datos_a_terceros['rfc_a_cuenta_terceros'], "name_a_cuenta_terceros": datos_a_terceros['name_a_cuenta_terceros'], "regimen_fiscal_a_cuenta_terceros": datos_a_terceros['regimen_fical_a_cuenta_terceros'], "domicilio_fiscas_a_cuenta_terceros": datos_a_terceros['domicilio_ficas_a_cuenta_terceros'], "no_identificacion": no_identificacion}
                self._respuesta.append(datos)
                num += 1