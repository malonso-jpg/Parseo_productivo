from parseo.manipudorDatos import manipudorDatos
import os
class parseoPagos(manipudorDatos):
    def __init__(self, texto_xml):
        self.texto_xml = texto_xml
        self._respuesta = []
        self._respuesta_documentos = []
        if(self.texto_xml != ""):
            self.parsea_pagos()
            self.parsea_pagos_documentos()
    @property
    def obtener_pagos(self):
        if not self._respuesta:
            return [False]
        return self._respuesta
    def parsea_pagos(self):
        entro = False
        pagos = os.environ['PAGOS'].split('||')
        for urls_pago in pagos:
            tipo, url = urls_pago.split('=')
            total_trasladado_base_iva16 = 0
            total_trasladado_impuesto_iva16 = 0
            total_trasladado_base_iva8 = 0
            total_trasladado_impuesto_iva8 = 0
            total_trasladado_base_iva0 = 0
            total_trasladado_impuesto_iva0 = 0
            total_trasladado_base_iva_exento = 0
            total_retenciones_iva = 0
            total_retenciones_isr = 0
            total_retenciones_ieps = 0
            monto_total_pagos = 0
            version_pago = ""
            if (tipo == "pago20" and self.texto_xml.find('.//pago20:Pagos', namespaces={"pago20": url}) is not None):
                pagos20 = self.texto_xml.xpath('//pago20:Pagos', namespaces={"pago20": url})
                for pago20 in pagos20:
                    version_pago = self.limpiar_cadenas(pago20.get('Version', ""))
                    pagos_totales = pago20.xpath('pago20:Totales',  namespaces={"pago20": url})
                    for total_pagos in pagos_totales:
                        total_trasladado_base_iva16 = self.convertir_float(total_pagos.get('TotalTrasladosBaseIVA16', ""))
                        total_trasladado_impuesto_iva16 = self.convertir_float(total_pagos.get('TotalTrasladosImpuestoIVA16', ""))
                        total_trasladado_base_iva8 = self.convertir_float(total_pagos.get('TotalTrasladosBaseIVA8', ""))
                        total_trasladado_impuesto_iva8 = self.convertir_float(total_pagos.get('TotalTrasladosImpuestoIVA8', ""))
                        total_trasladado_base_iva0 = self.convertir_float(total_pagos.get('TotalTrasladosBaseIVA0', ""))
                        total_trasladado_impuesto_iva0 = self.convertir_float(total_pagos.get('TotalTrasladosImpuestoIVA0', ""))
                        total_trasladado_base_iva_exento = self.convertir_float(total_pagos.get('TotalTrasladosBaseIVAExento', ""))
                        total_retenciones_iva = self.convertir_float(total_pagos.get('TotalRetencionesIVA', ""))
                        total_retenciones_isr = self.convertir_float(total_pagos.get('TotalRetencionesISR', ""))
                        total_retenciones_ieps = self.convertir_float(total_pagos.get('TotalRetencionesIEPS', ""))
                        monto_total_pagos = self.convertir_float(total_pagos.get('MontoTotalPagos', ""))
                        entro = True
            elif(tipo == "pago10" and self.texto_xml.find('.//pago10:Pagos', namespaces={"pago10": url}) is not None):
                pagos10 = self.texto_xml.xpath('//pago10:Pagos', namespaces={"pago10": url})
                for pago10 in pagos10:
                    version_pago = self.limpiar_cadenas(pago10.get('Version', ""))
                    entro = True
            if(entro):
                self._respuesta = [True, {"version_pago": version_pago, "total_trasladado_base_iva16": self.decimal_2(total_trasladado_base_iva16), "total_trasladado_importe_iva16": self.decimal_2(total_trasladado_impuesto_iva16), "total_trasladado_base_iva8": self.decimal_2(total_trasladado_base_iva8), "total_trasladado_importe_iva8": self.decimal_2(total_trasladado_impuesto_iva8), "total_trasladado_base_iva0": self.decimal_2(total_trasladado_base_iva0), "total_trasladado_importe_iva0": self.decimal_2(total_trasladado_impuesto_iva0), "total_trasladado_base_iva_exento": self.decimal_2(total_trasladado_base_iva_exento), "total_retenciones_iva": self.decimal_2(total_retenciones_iva), "total_retenciones_isr": self.decimal_2(total_retenciones_isr), "total_retenciones_ieps": self.decimal_2(total_retenciones_ieps), "monto_total_pagos": self.decimal_2(monto_total_pagos)}]
                break
        
    @property
    def obtener_pagos_documentos(self):
        if not self._respuesta_documentos:
            return [False]
        return self._respuesta_documentos
    def parseo_traslado_dr(self, traslados_dr = "", tiene = False):
        exentos_base = 0
        exentos_iva = 0
        t0_base = 0
        t0_iva = 0
        t8_base = 0
        t8_iva = 0
        t16_base = 0
        t16_iva = 0
        ieps_base_traslado = 0
        ieps_importe_traslado = 0
        if tiene:
            for traslado_dr in traslados_dr:
                base_dr = self.convertir_float(traslado_dr.get('BaseDR', ""))
                impuesto_dr = self.limpiar_cadenas(traslado_dr.get('ImpuestoDR', ""))
                tipo_factor_dr = self.limpiar_cadenas(traslado_dr.get('TipoFactorDR', ""))
                tasa_o_cuota_dr = self.limpiar_cadenas(traslado_dr.get('TasaOCuotaDR', ""))
                importe_dr = self.convertir_float(traslado_dr.get('ImporteDR', ""))
                if (impuesto_dr == '002'):
                    if (('EXENTO' in tasa_o_cuota_dr.upper() or "E" in tasa_o_cuota_dr) or 'EXENTO' in tipo_factor_dr.upper() or "E" in tipo_factor_dr):
                        exentos_base += base_dr
                        exentos_iva += importe_dr
                    elif('16' in tipo_factor_dr or '16' in tasa_o_cuota_dr):
                        t16_base += base_dr
                        t16_iva += importe_dr
                    elif('8' in tipo_factor_dr or '8' in tasa_o_cuota_dr):
                        t8_base += base_dr
                        t8_iva += importe_dr
                    else:
                        t0_base += base_dr
                        t0_iva += importe_dr
                if (impuesto_dr == '003'):
                    ieps_base_traslado += base_dr
                    ieps_importe_traslado += importe_dr
        return {"exentos_base": exentos_base, "exentos_iva": exentos_iva, "t0_base": t0_base, "t0_iva": t0_iva, "t8_base": t8_base, "t8_iva": t8_iva, "t16_base": t16_base, "t16_iva": t16_iva, "ieps_base_traslado": ieps_base_traslado, "ieps_importe_traslado": ieps_importe_traslado}
    def parseo_retenciones_dr(self, retenciones_dr = "", tiene = False):
        iva_base_retencion = 0
        iva_importe_retencion = 0
        isr_base_retencion = 0
        isr_importe_retencion = 0
        ieps_base_retencion = 0
        ieps_importe_retencion = 0
        if tiene:
            for retencion_dr in retenciones_dr:
                impuesto_dr = self.limpiar_cadenas(retencion_dr.get('ImpuestoDR', ""))
                basedr = self.convertir_float(retencion_dr.get('BaseDR', ""))
                importe_dr = self.convertir_float(retencion_dr.get('ImporteDR', ""))
                if (impuesto_dr == '002'):
                    iva_base_retencion += basedr
                    iva_importe_retencion += importe_dr
                if (impuesto_dr == '001'):
                    isr_base_retencion += basedr
                    isr_importe_retencion += importe_dr
                if (impuesto_dr == '003'):
                    ieps_base_retencion += basedr
                    ieps_importe_retencion += importe_dr
        return {"iva_base_retencion": iva_base_retencion ,"iva_importe_retencion": iva_importe_retencion ,"isr_base_retencion": isr_base_retencion ,"isr_importe_retencion": isr_importe_retencion ,"ieps_base_retencion": ieps_base_retencion ,"ieps_importe_retencion": ieps_importe_retencion}
    def parseo_traslados_p(self, traslados_p= "", tiene = False):
        exentos_base = 0
        exentos_iva = 0
        t0_base = 0
        t0_iva = 0
        t8_base = 0
        t8_iva = 0
        t16_base = 0
        t16_iva = 0
        ieps_base_traslado = 0
        ieps_importe_traslado = 0
        if tiene:
            for traslado_p in traslados_p:
                impuesto_p = self.limpiar_cadenas(traslado_p.get('ImpuestoP', ""))
                base_p = self.convertir_float(traslado_p.get('BaseP', ""))
                importe_p = self.convertir_float(traslado_p.get('ImporteP', ""))
                tipo_factor_p = self.limpiar_cadenas(traslado_p.get('TipoFactorP', ""))
                tasa_o_cuota_p = self.limpiar_cadenas(traslado_p.get('TasaOCuotaP', ""))
                if impuesto_p == '002':
                    if (('EXENTO' in tipo_factor_p or 'EXENTO' in tasa_o_cuota_p)):
                        exentos_base += base_p
                        exentos_iva += importe_p
                    if('16' in tipo_factor_p or '16' in tasa_o_cuota_p):
                        t16_base += base_p
                        t16_iva += importe_p
                    elif('8' in tipo_factor_p or '8' in tasa_o_cuota_p):
                        t8_base += base_p
                        t8_iva += importe_p
                    else:
                        t0_base += base_p
                        t0_iva += importe_p
                if (impuesto_p == '003'):
                    ieps_base_traslado += base_p
                    ieps_importe_traslado += importe_p
        return {"exentos_base": exentos_base, "exentos_iva": exentos_iva, "t0_base": t0_base, "t0_iva": t0_iva, "t8_base": t8_base, "t8_iva": t8_iva, "t16_base": t16_base, "t16_iva": t16_iva, "ieps_base_traslado": ieps_base_traslado, "ieps_importe_traslado": ieps_importe_traslado}
    def parseo_retenciones_p(self, retenciones_p = "", tiene = False):
        iva_base_retencion = 0
        iva_importe_retencion = 0
        isr_base_retencion = 0
        isr_importe_retencion = 0
        ieps_base_retencion = 0
        ieps_importe_retencion = 0
        if tiene:
            for retencion_p in retenciones_p:
                impuesto_p = self.limpiar_cadenas(retencion_p.get('ImpuestoDR', ""))
                importe_p = self.convertir_float(retencion_p.get('ImporteDR', ""))
                if (impuesto_p == '002'):
                    iva_importe_retencion += importe_p
                if (impuesto_p == '001'):
                    isr_importe_retencion += importe_p
                if (impuesto_p == '003'):
                    ieps_importe_retencion += importe_p
        return {"iva_base_retencion": iva_base_retencion ,"iva_importe_retencion": iva_importe_retencion ,"isr_base_retencion": isr_base_retencion ,"isr_importe_retencion": isr_importe_retencion ,"ieps_base_retencion": ieps_base_retencion ,"ieps_importe_retencion": ieps_importe_retencion}
    def parsea_pagos_documentos(self):
        entro = False
        pagos = os.environ['PAGOS'].split('||')
        for urls_pago in pagos:
            tipo, url = urls_pago.split('=')
            if (tipo == "pago20" and self.texto_xml.find('.//pago20:Pagos', namespaces={"pago20": url}) is not None):
                num = 1
                '''de_cuantos_imp = 0
                de_cuantos_rel = 0
                de_cuantos_rel = int(self.texto_xml.xpath("count(//pago20:Pagos//pago20:Pago//pago20:DoctoRelacionado)", namespaces={"pago20": url}))
                de_cuantos_imp = int(self.texto_xml.xpath("count(//pago20:Pagos//pago20:Pago//pago20:ImpuestosP)", namespaces={"pago20": url}))
                de_cuantos = de_cuantos_rel+de_cuantos_imp'''
                de_cuantos = int(self.texto_xml.xpath("count(//pago20:Pagos//pago20:Pago//pago20:DoctoRelacionado)", namespaces={"pago20": url}))
                pagos20 = self.texto_xml.xpath('//pago20:Pagos', namespaces={"pago20": url})
                for pago20 in pagos20:
                    pagos = pago20.xpath('pago20:Pago', namespaces={"pago20": url})
                    for pago in pagos:
                        fecha_pago = ""
                        fecha_pago = self.convertir_date(pago.get('FechaPago', ""))
                        forma_pago = self.limpiar_cadenas(pago.get('FormaDePagoP', ""))
                        moneda_pago = self.limpiar_cadenas(pago.get('MonedaP', ""))
                        tipo_cambio_pago = self.convertir_float(pago.get('TipoCambioP', ""))
                        monto_pago = self.convertir_float(pago.get('Monto', ""))
                        numero_operacion = self.limpiar_cadenas(pago.get('NumOperacion', ""))
                        docto_relacionado = pago.xpath('pago20:DoctoRelacionado', namespaces={"pago20": url})
                        for relacionado in docto_relacionado:
                            id_documento = self.limpiar_cadenas(relacionado.get('IdDocumento', ""))
                            moneda_dr = self.limpiar_cadenas(relacionado.get('MonedaDR', ""))
                            equivalencia_dr = self.convertir_float(relacionado.get('EquivalenciaDR', ""))
                            num_parcialidad = self.convertir_int(relacionado.get('NumParcialidad', ""))
                            importe_saldo_anterior = self.convertir_float(relacionado.get('ImpSaldoAnt', ""))
                            objeto_importe_dr = self.limpiar_cadenas(relacionado.get('ObjetoImpDR', ""))
                            importe_pagado = self.convertir_float(relacionado.get('ImpPagado', ""))
                            serie_dr = self.limpiar_cadenas(relacionado.get('Serie', ""))
                            folio_dr = self.limpiar_cadenas(relacionado.get('Folio', ""))
                            traslados_dr = self.parseo_traslado_dr(relacionado.xpath('pago20:ImpuestosDR/pago20:TrasladosDR/pago20:TrasladoDR', namespaces={"pago20": url}), True)
                            exentos_base_pesos = self.convertir_a_pesos(tipo_cambio_pago, traslados_dr['exentos_base'])
                            exentos_iva_pesos = self.convertir_a_pesos(tipo_cambio_pago, traslados_dr['exentos_iva'])
                            t0_base_pesos = self.convertir_a_pesos(tipo_cambio_pago, traslados_dr['t0_base'])
                            t0_iva_pesos = self.convertir_a_pesos(tipo_cambio_pago, traslados_dr['t0_iva'])
                            t8_base_pesos = self.convertir_a_pesos(tipo_cambio_pago, traslados_dr['t8_base'])
                            t8_iva_pesos = self.convertir_a_pesos(tipo_cambio_pago, traslados_dr['t8_iva'])
                            t16_base_pesos = self.convertir_a_pesos(tipo_cambio_pago, traslados_dr['t16_base'])
                            t16_iva_pesos = self.convertir_a_pesos(tipo_cambio_pago, traslados_dr['t16_iva'])
                            ieps_base_traslado_pesos = self.convertir_a_pesos(tipo_cambio_pago, traslados_dr['ieps_base_traslado'])
                            ieps_importe_traslado_pesos = self.convertir_a_pesos(tipo_cambio_pago, traslados_dr['ieps_importe_traslado'])
                            retenciones_dr = self.parseo_retenciones_dr(relacionado.xpath('pago20:ImpuestosDR/pago20:RetencionesDR/pago20:RetencionDR', namespaces={"pago20": url}), True)
                            iva_base_retencion_pesos = self.convertir_a_pesos(tipo_cambio_pago, retenciones_dr['iva_base_retencion'])
                            iva_importe_retencion_pesos = self.convertir_a_pesos(tipo_cambio_pago, retenciones_dr['iva_importe_retencion'])
                            isr_base_retencion_pesos = self.convertir_a_pesos(tipo_cambio_pago, retenciones_dr['isr_base_retencion'])
                            isr_importe_retencion_pesos = self.convertir_a_pesos(tipo_cambio_pago, retenciones_dr['isr_importe_retencion'])
                            ieps_base_retencion_pesos = self.convertir_a_pesos(tipo_cambio_pago, retenciones_dr['ieps_base_retencion'])
                            ieps_importe_retencion_pesos = self.convertir_a_pesos(tipo_cambio_pago, retenciones_dr['ieps_importe_retencion'])
                            self._respuesta_documentos.append({"cuantos_pagos": de_cuantos, "num_pago": num, "fecha_pago": fecha_pago, "forma_pago": forma_pago, "moneda_pago": moneda_pago, "tipo_cambio_pago": tipo_cambio_pago, "monto_pago": self.decimal_2(monto_pago), "numero_operacion_pago": numero_operacion, "id_documento": id_documento, "moneda_dr": moneda_dr, "equivalencia_dr": equivalencia_dr, "numero_parcialidad": num_parcialidad, "importe_saldo_anterior": self.decimal_2(importe_saldo_anterior), "objeto_importe_dr": objeto_importe_dr, "importe_pagado": self.decimal_2(importe_pagado), "serie_dr": serie_dr, "folio_dr": folio_dr, "tasa_e_base": self.decimal_2(traslados_dr['exentos_base']), "tasa_e_iva": self.decimal_2(traslados_dr['exentos_iva']), "tasa_0_base": self.decimal_2(traslados_dr['t0_base']), "tasa_0_iva": self.decimal_2(traslados_dr['t0_iva']), "tasa_8_base": self.decimal_2(traslados_dr['t8_base']), "tasa_8_iva": self.decimal_2(traslados_dr['t8_iva']), "tasa_16_base": self.decimal_2(traslados_dr['t16_base']), "tasa_16_iva": self.decimal_2(traslados_dr['t16_iva']), "trasladado_ieps_base": self.decimal_2(traslados_dr['ieps_base_traslado']), "trasladado_ieps_importe": self.decimal_2(traslados_dr['ieps_importe_traslado']), "retenciones_iva_base": self.decimal_2(retenciones_dr['iva_base_retencion']), "retenciones_iva_importe": self.decimal_2(retenciones_dr['iva_importe_retencion']), "retenciones_isr_base": self.decimal_2(retenciones_dr['isr_base_retencion']), "retenciones_isr_importe": self.decimal_2(retenciones_dr['isr_importe_retencion']), "retenido_ieps_base": self.decimal_2(retenciones_dr['ieps_base_retencion']), "retenido_ieps_importe": self.decimal_2(retenciones_dr['ieps_importe_retencion']), "tasa_e_base_pesos": self.decimal_2(exentos_base_pesos), "tasa_e_iva_pesos": self.decimal_2(exentos_iva_pesos), "tasa_0_base_pesos": self.decimal_2(t0_base_pesos), "tasa_0_iva_pesos": self.decimal_2(t0_iva_pesos), "tasa_8_base_pesos": self.decimal_2(t8_base_pesos), "tasa_8_iva_pesos": self.decimal_2(t8_iva_pesos), "tasa_16_base_pesos": self.decimal_2(t16_base_pesos), "tasa_16_iva_pesos": self.decimal_2(t16_iva_pesos), "trasladado_ieps_base_pesos": self.decimal_2(ieps_base_traslado_pesos), "trasladado_ieps_importe_pesos": self.decimal_2(ieps_importe_traslado_pesos), "retenciones_iva_base_pesos": self.decimal_2(iva_base_retencion_pesos), "retenciones_iva_importe_pesos": self.decimal_2(iva_importe_retencion_pesos), "retenciones_isr_base_pesos": self.decimal_2(isr_base_retencion_pesos), "retenciones_isr_importe_pesos": self.decimal_2(isr_importe_retencion_pesos), "retenido_ieps_base_pesos": self.decimal_2(ieps_base_retencion_pesos), "retenido_ieps_importe_pesos": self.decimal_2(ieps_importe_retencion_pesos)})
                            num += 1
                        ''' impuestosP = pago.xpath('pago20:ImpuestosP', namespaces={"pago20": url})
                        for impuestoP in impuestosP:
                            id_documento = "ImpuestosP"
                            moneda_dr = ""
                            equivalencia_dr = 0
                            num_parcialidad = 0
                            importe_saldo_anterior = 0
                            objeto_importe_dr = ""
                            importe_pagado = 0
                            serie_dr = ""
                            folio_dr = ""
                            traslados_p = self.parseo_traslados_p(impuestoP.xpath('pago20:TrasladosP/pago20:TrasladoP', namespaces={"pago20": url}), True)
                            exentos_base_pesos = self.convertir_a_pesos(tipo_cambio_pago, traslados_p['exentos_base'])
                            exentos_iva_pesos = self.convertir_a_pesos(tipo_cambio_pago, traslados_p['exentos_iva'])
                            t0_base_pesos = self.convertir_a_pesos(tipo_cambio_pago, traslados_p['t0_base'])
                            t0_iva_pesos = self.convertir_a_pesos(tipo_cambio_pago, traslados_p['t0_iva'])
                            t8_base_pesos = self.convertir_a_pesos(tipo_cambio_pago, traslados_p['t8_base'])
                            t8_iva_pesos = self.convertir_a_pesos(tipo_cambio_pago, traslados_p['t8_iva'])
                            t16_base_pesos = self.convertir_a_pesos(tipo_cambio_pago, traslados_p['t16_base'])
                            t16_iva_pesos = self.convertir_a_pesos(tipo_cambio_pago, traslados_p['t16_iva'])
                            ieps_base_traslado_pesos = self.convertir_a_pesos(tipo_cambio_pago, traslados_p['ieps_base_traslado'])
                            ieps_importe_traslado_pesos = self.convertir_a_pesos(tipo_cambio_pago, traslados_p['ieps_importe_traslado'])

                            retenciones_p = self.parseo_retenciones_p(impuestoP.xpath('pago20:RetencionesP/pago20:RetencioneP', namespaces={"pago20": url}), True)

                            iva_base_retencion_pesos = self.convertir_a_pesos(tipo_cambio_pago, retenciones_p['iva_base_retencion'])
                            iva_importe_retencion_pesos = self.convertir_a_pesos(tipo_cambio_pago, retenciones_p['iva_importe_retencion'])
                            isr_base_retencion_pesos = self.convertir_a_pesos(tipo_cambio_pago, retenciones_p['isr_base_retencion'])
                            isr_importe_retencion_pesos = self.convertir_a_pesos(tipo_cambio_pago, retenciones_p['isr_importe_retencion'])
                            ieps_base_retencion_pesos = self.convertir_a_pesos(tipo_cambio_pago, retenciones_p['ieps_base_retencion'])
                            ieps_importe_retencion_pesos = self.convertir_a_pesos(tipo_cambio_pago, retenciones_p['ieps_importe_retencion'])


                            self._respuesta_documentos.append({"cuantos_pagos": de_cuantos, "num_pago": num, "fecha_pago": fecha_pago, "forma_pago": forma_pago, "moneda_pago": moneda_pago, "tipo_cambio_pago": tipo_cambio_pago, "monto_pago": self.decimal_2(monto_pago), "numero_operacion_pago": numero_operacion, "id_documento": id_documento, "moneda_dr": moneda_dr, "equivalencia_dr": equivalencia_dr, "numero_parcialidad": num_parcialidad, "importe_saldo_anterior": self.decimal_2(importe_saldo_anterior), "objeto_importe_dr": objeto_importe_dr, "importe_pagado": self.decimal_2(importe_pagado), "serie_dr": serie_dr, "folio_dr": folio_dr, "tasa_e_base": self.decimal_2(traslados_dr['exentos_base']), "tasa_e_iva": self.decimal_2(traslados_dr['exentos_iva']), "tasa_0_base": self.decimal_2(traslados_dr['t0_base']), "tasa_0_iva": self.decimal_2(traslados_dr['t0_iva']), "tasa_8_base": self.decimal_2(traslados_dr['t8_base']), "tasa_8_iva": self.decimal_2(traslados_dr['t8_iva']), "tasa_16_base": self.decimal_2(traslados_dr['t16_base']), "tasa_16_iva": self.decimal_2(traslados_dr['t16_iva']), "trasladado_ieps_base": self.decimal_2(traslados_dr['ieps_base_traslado']), "trasladado_ieps_importe": self.decimal_2(traslados_dr['ieps_importe_traslado']), "retenciones_iva_base": self.decimal_2(retenciones_dr['iva_base_retencion']), "retenciones_iva_importe": self.decimal_2(retenciones_dr['iva_importe_retencion']), "retenciones_isr_base": self.decimal_2(retenciones_dr['isr_base_retencion']), "retenciones_isr_importe": self.decimal_2(retenciones_dr['isr_importe_retencion']), "retenido_ieps_base": self.decimal_2(retenciones_dr['ieps_base_retencion']), "retenido_ieps_importe": self.decimal_2(retenciones_dr['ieps_importe_retencion']), "tasa_e_base_pesos": self.decimal_2(exentos_base_pesos), "tasa_e_iva_pesos": self.decimal_2(exentos_iva_pesos), "tasa_0_base_pesos": self.decimal_2(t0_base_pesos), "tasa_0_iva_pesos": self.decimal_2(t0_iva_pesos), "tasa_8_base_pesos": self.decimal_2(t8_base_pesos), "tasa_8_iva_pesos": self.decimal_2(t8_iva_pesos), "tasa_16_base_pesos": self.decimal_2(t16_base_pesos), "tasa_16_iva_pesos": self.decimal_2(t16_iva_pesos), "trasladado_ieps_base_pesos": self.decimal_2(ieps_base_traslado_pesos), "trasladado_ieps_importe_pesos": self.decimal_2(ieps_importe_traslado_pesos), "retenciones_iva_base_pesos": self.decimal_2(iva_base_retencion_pesos), "retenciones_iva_importe_pesos": self.decimal_2(iva_importe_retencion_pesos), "retenciones_isr_base_pesos": self.decimal_2(isr_base_retencion_pesos), "retenciones_isr_importe_pesos": self.decimal_2(isr_importe_retencion_pesos), "retenido_ieps_base_pesos": self.decimal_2(ieps_base_retencion_pesos), "retenido_ieps_importe_pesos": self.decimal_2(ieps_importe_retencion_pesos)})
                            num += 1'''
                entro = True
            elif(tipo == "pago10" and self.texto_xml.find('.//pago10:Pagos', namespaces={"pago10": url}) is not None):
                de_cuantos = int(self.texto_xml.xpath("count(//pago10:Pagos//pago10:Pago//pago10:DoctoRelacionado)", namespaces={"pago10": url}))
                pagos10 = self.texto_xml.xpath('//pago10:Pagos', namespaces={"pago10": url})
                num = 1
                for pago10 in pagos10:
                    pagos = pago10.xpath('pago10:Pago', namespaces={"pago10": url})
                    for pago in pagos:
                        fecha_pago = ""
                        fecha_pago = self.convertir_date(pago.get('FechaPago', ""))
                        forma_pago = self.limpiar_cadenas(pago.get('FormaDePagoP', ""))
                        moneda_pago = self.limpiar_cadenas(pago.get('MonedaP', ""))
                        tipo_cambio_pago = self.convertir_float(pago.get('TipoCambioP', ""))
                        monto_pago = self.convertir_float(pago.get('Monto', ""))
                        numero_operacion = self.limpiar_cadenas(pago.get('NumOperacion', ""))
                        docto_relacionado = pago.xpath('pago10:DoctoRelacionado', namespaces={"pago10": url})
                        for relacionado in docto_relacionado:
                            id_documento = self.limpiar_cadenas(relacionado.get('IdDocumento', ""))
                            moneda_dr = self.limpiar_cadenas(relacionado.get('MonedaDR', ""))
                            equivalencia_dr = self.convertir_float(relacionado.get('EquivalenciaDR', ""))
                            num_parcialidad = self.convertir_int(relacionado.get('NumParcialidad', ""))
                            importe_saldo_anterior = self.convertir_float(relacionado.get('ImpSaldoAnt', ""))
                            objeto_importe_dr = self.limpiar_cadenas(relacionado.get('ObjetoImpDR', ""))
                            importe_pagado = self.convertir_float(relacionado.get('ImpPagado', ""))
                            serie_dr = self.limpiar_cadenas(relacionado.get('Serie', ""))
                            folio_dr = self.limpiar_cadenas(relacionado.get('Folio', ""))
                            traslados_dr = self.parseo_traslado_dr()
                            exentos_base_pesos = self.convertir_a_pesos(tipo_cambio_pago, traslados_dr['exentos_base'])
                            exentos_iva_pesos = self.convertir_a_pesos(tipo_cambio_pago, traslados_dr['exentos_iva'])
                            t0_base_pesos = self.convertir_a_pesos(tipo_cambio_pago, traslados_dr['t0_base'])
                            t0_iva_pesos = self.convertir_a_pesos(tipo_cambio_pago, traslados_dr['t0_iva'])
                            t8_base_pesos = self.convertir_a_pesos(tipo_cambio_pago, traslados_dr['t8_base'])
                            t8_iva_pesos = self.convertir_a_pesos(tipo_cambio_pago, traslados_dr['t8_iva'])
                            t16_base_pesos = self.convertir_a_pesos(tipo_cambio_pago, traslados_dr['t16_base'])
                            t16_iva_pesos = self.convertir_a_pesos(tipo_cambio_pago, traslados_dr['t16_iva'])
                            ieps_base_traslado_pesos = self.convertir_a_pesos(tipo_cambio_pago, traslados_dr['ieps_base_traslado'])
                            ieps_importe_traslado_pesos = self.convertir_a_pesos(tipo_cambio_pago, traslados_dr['ieps_importe_traslado'])
                            retenciones_dr = self.parseo_retenciones_dr()
                            iva_base_retencion_pesos = self.convertir_a_pesos(tipo_cambio_pago, retenciones_dr['iva_base_retencion'])
                            iva_importe_retencion_pesos = self.convertir_a_pesos(tipo_cambio_pago, retenciones_dr['iva_importe_retencion'])
                            isr_base_retencion_pesos = self.convertir_a_pesos(tipo_cambio_pago, retenciones_dr['isr_base_retencion'])
                            isr_importe_retencion_pesos = self.convertir_a_pesos(tipo_cambio_pago, retenciones_dr['isr_importe_retencion'])
                            ieps_base_retencion_pesos = self.convertir_a_pesos(tipo_cambio_pago, retenciones_dr['ieps_base_retencion'])
                            ieps_importe_retencion_pesos = self.convertir_a_pesos(tipo_cambio_pago, retenciones_dr['ieps_importe_retencion'])

                            self._respuesta_documentos.append({"cuantos_pagos": de_cuantos, "num_pago": num, "fecha_pago": fecha_pago, "forma_pago": forma_pago, "moneda_pago": moneda_pago, "tipo_cambio_pago": tipo_cambio_pago, "monto_pago": self.decimal_2(monto_pago), "numero_operacion_pago": numero_operacion, "id_documento": str(id_documento).upper(), "moneda_dr": moneda_dr, "equivalencia_dr": equivalencia_dr, "numero_parcialidad": num_parcialidad, "importe_saldo_anterior": self.decimal_2(importe_saldo_anterior), "objeto_importe_dr": objeto_importe_dr, "importe_pagado": self.decimal_2(importe_pagado), "serie_dr": serie_dr, "folio_dr": folio_dr, "tasa_e_base": self.decimal_2(traslados_dr['exentos_base']), "tasa_e_iva": self.decimal_2(traslados_dr['exentos_iva']), "tasa_0_base": self.decimal_2(traslados_dr['t0_base']), "tasa_0_iva": self.decimal_2(traslados_dr['t0_iva']), "tasa_8_base": self.decimal_2(traslados_dr['t8_base']), "tasa_8_iva": self.decimal_2(traslados_dr['t8_iva']), "tasa_16_base": self.decimal_2(traslados_dr['t16_base']), "tasa_16_iva": self.decimal_2(traslados_dr['t16_iva']), "trasladado_ieps_base": self.decimal_2(traslados_dr['ieps_base_traslado']), "trasladado_ieps_importe": self.decimal_2(traslados_dr['ieps_importe_traslado']), "retenciones_iva_base": self.decimal_2(retenciones_dr['iva_base_retencion']), "retenciones_iva_importe": self.decimal_2(retenciones_dr['iva_importe_retencion']), "retenciones_isr_base": self.decimal_2(retenciones_dr['isr_base_retencion']), "retenciones_isr_importe": self.decimal_2(retenciones_dr['isr_importe_retencion']), "retenido_ieps_base": self.decimal_2(retenciones_dr['ieps_base_retencion']), "retenido_ieps_importe": self.decimal_2(retenciones_dr['ieps_importe_retencion']), "tasa_e_base_pesos": self.decimal_2(exentos_base_pesos), "tasa_e_iva_pesos": self.decimal_2(exentos_iva_pesos), "tasa_0_base_pesos": self.decimal_2(t0_base_pesos), "tasa_0_iva_pesos": self.decimal_2(t0_iva_pesos), "tasa_8_base_pesos": self.decimal_2(t8_base_pesos), "tasa_8_iva_pesos": self.decimal_2(t8_iva_pesos), "tasa_16_base_pesos": self.decimal_2(t16_base_pesos), "tasa_16_iva_pesos": self.decimal_2(t16_iva_pesos), "trasladado_ieps_base_pesos": self.decimal_2(ieps_base_traslado_pesos), "trasladado_ieps_importe_pesos": self.decimal_2(ieps_importe_traslado_pesos), "retenciones_iva_base_pesos": self.decimal_2(iva_base_retencion_pesos), "retenciones_iva_importe_pesos": self.decimal_2(iva_importe_retencion_pesos), "retenciones_isr_base_pesos": self.decimal_2(isr_base_retencion_pesos), "retenciones_isr_importe_pesos": self.decimal_2(isr_importe_retencion_pesos), "retenido_ieps_base_pesos": self.decimal_2(ieps_base_retencion_pesos), "retenido_ieps_importe_pesos": self.decimal_2(ieps_importe_retencion_pesos)})
                            num += 1
                entro = True
            if entro:
                break