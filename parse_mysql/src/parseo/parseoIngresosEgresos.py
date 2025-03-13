from parseo.manipudorDatos import manipudorDatos

class parseoIngresosEgresos(manipudorDatos):
    def __init__(self, texto_xml = "", cfdi_url = "", tipo_cambio = 0):
        self.texto_xml = texto_xml
        self._cfdi_url = cfdi_url
        self._tipo_cambio = tipo_cambio
        self._respuesta = []
        if(texto_xml != ""):
            self.parseo_datos()
    @property
    def obtener_ingresos_egresos(self):
        return self._respuesta
    def parseo_impuestos_trasladados(self, impuestos_traslados):
        exentos_base = 0
        exentos_importe = 0
        tasa_0_base = 0
        tasa_0_importe = 0
        tasa_8_base = 0
        tasa_8_importe = 0
        tasa_16_base = 0
        tasa_16_importe = 0
        base_ieps_tasa_traslado = 0
        importe_ieps_tasa_traslado = 0
        base_ieps_cuota_traslado = 0
        importe_ieps_cuota_traslado = 0
        for traslados in impuestos_traslados:
            base_traslado = self.convertir_float(traslados.get("Base", ""))
            impuesto_traslado = self.limpiar_cadenas(traslados.get("Impuesto", ""))
            importe_traslado = self.convertir_float(traslados.get("Importe", ""))
            tipo_factor_traslado = self.limpiar_cadenas(traslados.get("TipoFactor", "")).upper()
            tasa_o_cuota_traslado = self.limpiar_cadenas(traslados.get("TasaOCuota", "")).upper()
            if (impuesto_traslado == '002'):
                if (('EXENTO' in tasa_o_cuota_traslado.upper() or "E" in tasa_o_cuota_traslado) or 'EXENTO' in tipo_factor_traslado.upper() or "E" in tipo_factor_traslado):
                    exentos_base += base_traslado
                    exentos_importe += importe_traslado
                elif ('16' in tasa_o_cuota_traslado or '16' in tipo_factor_traslado):
                    tasa_16_base += base_traslado
                    tasa_16_importe += importe_traslado
                elif ('8' in tasa_o_cuota_traslado or '8' in tipo_factor_traslado):
                    tasa_8_base += base_traslado
                    tasa_8_importe += importe_traslado
                else:
                    tasa_0_base += base_traslado
                    tasa_0_importe += importe_traslado
            elif (impuesto_traslado == '003'):
                if(tipo_factor_traslado == 'TASA'):
                    base_ieps_tasa_traslado += base_traslado
                    importe_ieps_tasa_traslado += importe_traslado
                elif(tipo_factor_traslado == 'CUOTA'):
                    base_ieps_cuota_traslado += base_traslado
                    importe_ieps_cuota_traslado += importe_traslado
        respuesta = {"exentos_base": exentos_base, "exentos_importe": exentos_importe, "tasa_16_base": tasa_16_base, "tasa_16_importe": tasa_16_importe, "tasa_8_base": tasa_8_base, "tasa_8_importe": tasa_8_importe, "tasa_0_base": tasa_0_base, "tasa_0_importe": tasa_0_importe, "base_ieps_tasa_traslado": base_ieps_tasa_traslado, "importe_ieps_tasa_traslado": importe_ieps_tasa_traslado, "base_ieps_cuota_traslado": base_ieps_cuota_traslado, "importe_ieps_cuota_traslado": importe_ieps_cuota_traslado}
        return respuesta
    def parseo_impuestos_retenidos(self, impuestos_retenciones):
        retenciones_base_iva = 0
        retenciones_importe_iva = 0
        retenciones_base_isr = 0
        retenciones_importe_isr = 0
        base_ieps_tasa_retencion = 0
        importe_ieps_tasa_retencion = 0
        base_ieps_cuota_retencion = 0
        importe_ieps_cuota_retencion = 0
        for retenciones in impuestos_retenciones:
            base_retencion = self.convertir_float(retenciones.get("Base", ""))
            impuesto_retencion = self.limpiar_cadenas(retenciones.get("Impuesto", ""))
            importe_retencion = self.convertir_float(retenciones.get("Importe", ""))
            tipo_factor_retencion = self.limpiar_cadenas(retenciones.get("TipoFactor", "")).upper()
            if (impuesto_retencion == '002'):
                retenciones_base_iva += base_retencion
                retenciones_importe_iva += importe_retencion
            if (impuesto_retencion == '001'):
                retenciones_base_isr += base_retencion
                retenciones_importe_isr += importe_retencion
            if (impuesto_retencion == '003'):
                if(tipo_factor_retencion == 'TASA'):
                    base_ieps_tasa_retencion += base_retencion
                    importe_ieps_tasa_retencion += importe_retencion
                elif(tipo_factor_retencion == 'CUOTA'):
                    base_ieps_cuota_retencion += base_retencion
                    importe_ieps_cuota_retencion += importe_retencion
        return {"retenciones_base_iva": retenciones_base_iva, "retenciones_importe_iva": retenciones_importe_iva, "retenciones_base_isr": retenciones_base_isr, "retenciones_importe_isr": retenciones_importe_isr, "base_ieps_tasa_retencion": base_ieps_tasa_retencion, "importe_ieps_tasa_retencion": importe_ieps_tasa_retencion, "base_ieps_cuota_retencion": base_ieps_cuota_retencion, "importe_ieps_cuota_retencion": importe_ieps_cuota_retencion}
    def parseo_datos(self):
        exentos_base = 0
        exentos_importe = 0
        tasa_0_base = 0
        tasa_0_importe = 0
        tasa_8_base = 0
        tasa_8_importe = 0
        tasa_16_base = 0
        tasa_16_importe = 0
        base_ieps_tasa_traslado = 0
        importe_ieps_tasa_traslado = 0
        base_ieps_cuota_traslado = 0
        importe_ieps_cuota_traslado = 0

        retenciones_base_iva = 0
        retenciones_importe_iva = 0
        retenciones_base_isr = 0
        retenciones_importe_isr = 0
        base_ieps_tasa_retencion = 0
        importe_ieps_tasa_retencion = 0
        base_ieps_cuota_retencion = 0
        importe_ieps_cuota_retencion = 0
        noobject_impuestos = 0
        list_conceptos = self.texto_xml.xpath('//cfdi:Conceptos', namespaces={"cfdi": self._cfdi_url})
        a_cuenta_terceros = 0
        if self.texto_xml.find('.//cfdi:ACuentaTerceros', namespaces={"cfdi": self._cfdi_url}) is not None:
            a_cuenta_terceros = 1
        for conceptos in list_conceptos:
            list_concepto = conceptos.xpath('cfdi:Concepto', namespaces={"cfdi": self._cfdi_url})
            for concepto in list_concepto:
                importe = self.convertir_float(concepto.get("Importe", ""))
                objeto_imp = ''
                objeto_imp = self.limpiar_cadenas(concepto.get("ObjetoImp", ""))
                if (objeto_imp == '01'):
                    noobject_impuestos += self.convertir_float(importe)
                impuestos_traslados = self.parseo_impuestos_trasladados(concepto.xpath('cfdi:Impuestos/cfdi:Traslados/cfdi:Traslado', namespaces={"cfdi": self._cfdi_url}))
                exentos_base += impuestos_traslados['exentos_base']
                exentos_importe += impuestos_traslados['exentos_importe']
                tasa_0_base += impuestos_traslados['tasa_0_base']
                tasa_0_importe += impuestos_traslados['tasa_0_importe']
                tasa_8_base += impuestos_traslados['tasa_8_base']
                tasa_8_importe += impuestos_traslados['tasa_8_importe']
                tasa_16_base += impuestos_traslados['tasa_16_base']
                tasa_16_importe += impuestos_traslados['tasa_16_importe']
                base_ieps_tasa_traslado += impuestos_traslados['base_ieps_tasa_traslado']
                importe_ieps_tasa_traslado += impuestos_traslados['importe_ieps_tasa_traslado']
                base_ieps_cuota_traslado += impuestos_traslados['base_ieps_cuota_traslado']
                importe_ieps_cuota_traslado += impuestos_traslados['importe_ieps_cuota_traslado']
                impuestos_retenciones = self.parseo_impuestos_retenidos(concepto.xpath('cfdi:Impuestos/cfdi:Retenciones/cfdi:Retencion', namespaces={"cfdi": self._cfdi_url}))
                retenciones_base_iva += impuestos_retenciones['retenciones_base_iva']
                retenciones_importe_iva += impuestos_retenciones['retenciones_importe_iva']
                retenciones_base_isr += impuestos_retenciones['retenciones_base_isr']
                retenciones_importe_isr += impuestos_retenciones['retenciones_importe_isr']
                base_ieps_tasa_retencion += impuestos_retenciones['base_ieps_tasa_retencion']
                importe_ieps_tasa_retencion += impuestos_retenciones['importe_ieps_tasa_retencion']
                base_ieps_cuota_retencion += impuestos_retenciones['base_ieps_cuota_retencion']
                importe_ieps_cuota_retencion += impuestos_retenciones['importe_ieps_cuota_retencion']
        
        noobject_impuestos_pesos = self.convertir_a_pesos(self._tipo_cambio, noobject_impuestos)
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
        self._respuesta = [True, {"noobjetos_impuestos": self.decimal_2(noobject_impuestos), "tasa_e_base": self.decimal_2(exentos_base), "tasa_e_iva": self.decimal_2(exentos_importe), "tasa_0_base": self.decimal_2(tasa_0_base), "tasa_0_iva": self.decimal_2(tasa_0_importe), "tasa_8_base": self.decimal_2(tasa_8_base), "tasa_8_iva": self.decimal_2(tasa_8_importe), "tasa_16_base": self.decimal_2(tasa_16_base), "tasa_16_iva": self.decimal_2(tasa_16_importe), "trasladado_ieps_base_tasa": self.decimal_2(base_ieps_tasa_traslado), "trasladado_ieps_importe_tasa": self.decimal_2(importe_ieps_tasa_traslado), "trasladado_ieps_base_cuota": self.decimal_2(base_ieps_cuota_traslado), "trasladado_ieps_importe_cuota": self.decimal_2(importe_ieps_cuota_traslado), "retenciones_iva_base": self.decimal_2(retenciones_base_iva), "retenciones_iva_importe": self.decimal_2(retenciones_importe_iva), "retenciones_isr_base": self.decimal_2(retenciones_base_isr), "retenciones_isr_importe": self.decimal_2(retenciones_importe_isr), "retenciones_ieps_base_tasa": self.decimal_2(base_ieps_tasa_retencion), "retenciones_ieps_importe_tasa": self.decimal_2(importe_ieps_tasa_retencion), "retenciones_ieps_base_cuota": self.decimal_2(base_ieps_cuota_retencion), "retenciones_ieps_importe_cuota": self.decimal_2(importe_ieps_cuota_retencion), "noobjetos_impuestos_pesos": self.decimal_2(noobject_impuestos_pesos), "tasa_e_base_pesos": self.decimal_2(exentos_base_pesos), "tasa_e_iva_pesos": self.decimal_2(exentos_importe_pesos), "tasa_0_base_pesos": self.decimal_2(tasa_0_base_pesos), "tasa_0_iva_pesos": self.decimal_2(tasa_0_importe_pesos), "tasa_8_base_pesos": self.decimal_2(tasa_8_base_pesos), "tasa_8_iva_pesos": self.decimal_2(tasa_8_importe_pesos), "tasa_16_base_pesos": self.decimal_2(tasa_16_base_pesos), "tasa_16_iva_pesos": self.decimal_2(tasa_16_importe_pesos), "trasladado_ieps_base_tasa_pesos": self.decimal_2(base_ieps_tasa_traslado_pesos), "trasladado_ieps_importe_tasa_pesos": self.decimal_2(importe_ieps_tasa_traslado_pesos), "trasladado_ieps_base_cuota_pesos": self.decimal_2(base_ieps_cuota_traslado_pesos), "trasladado_ieps_importe_cuota_pesos": self.decimal_2(importe_ieps_cuota_traslado_pesos), "retenciones_iva_base_pesos": self.decimal_2(retenciones_base_iva_pesos), "retenciones_iva_importe_pesos": self.decimal_2(retenciones_importe_iva_pesos), "retenciones_isr_base_pesos": self.decimal_2(retenciones_base_isr_pesos), "retenciones_isr_importe_pesos": self.decimal_2(retenciones_importe_isr_pesos), "retenciones_ieps_base_tasa_pesos": self.decimal_2(base_ieps_tasa_retencion_pesos), "retenciones_ieps_importe_tasa_pesos": self.decimal_2(importe_ieps_tasa_retencion_pesos), "retenciones_ieps_base_cuota_pesos": self.decimal_2(base_ieps_cuota_retencion_pesos), "retenciones_ieps_importe_cuota_pesos": self.decimal_2(importe_ieps_cuota_retencion_pesos), "a_cuenta_terceros": a_cuenta_terceros, "objetoimp": objeto_imp}]