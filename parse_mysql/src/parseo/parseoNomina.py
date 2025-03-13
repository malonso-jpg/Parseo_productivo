from parseo.manipudorDatos import manipudorDatos
import os
class parseoNomina(manipudorDatos):
    def __init__(self, texto_xml):
        self.texto_xml = texto_xml
        self._respuesta = []
        self._url_nomina = ""
        self._pdop = []
        self._res_incapacidades = []
        self._res_sub_contrataciones = []
        if(self.texto_xml != ""):
            self.urlis_nomina()
            self.parsea_nomina()
    @property
    def obtener_nomina(self):
        if self._respuesta:
            return self._respuesta
        return False
    @property
    def obtener_detalle_nomina(self):
        if (self._pdop):
            return self._pdop
        return False
    @property
    def obtener_nomina_sub_contratacion(self):
        if (self._res_sub_contrataciones):
            return self._res_sub_contrataciones
        return False
    @property
    def obtener_incapacidades(self):
        if(self._res_incapacidades):
            return self._res_incapacidades
        return False
    def urlis_nomina(self):
        # Obtenemos la URL del cfdi para el namespaces y poder parsear
        urls_cfdis = os.environ['NOMINA'].split('||')

        try:
            namespaces = self.texto_xml.nsmap
        except Exception:
            root = self.texto_xml.getroot()
            namespaces = root.nsmap
        urls = ""
        ver_cfdi = ""
        for prefix, uri in namespaces.items():
            if (prefix == 'nomina12'):
                ver_cfdi = uri
            urls += " "+ uri
        
        url_nomina = ""
        if(ver_cfdi == ""):
            for url in urls_cfdis:
                url_nomina = url
                if(url in urls):
                    ver_cfdi = url
        if (ver_cfdi == ''):
            ver_cfdi = url_nomina
        self._url_nomina = ver_cfdi
    def parseo_datos_emisor(self, datos_emisor):
        registro_patronal = ""
        origen_recurso = ""
        curp_emisor = ""
        rfc_patron_origen = ""
        monto_recursos_propios = 0.0
        for dato_emisor in datos_emisor:
            registro_patronal = self.limpiar_cadenas(dato_emisor.get('RegistroPatronal', ""))
            curp_emisor = self.limpiar_cadenas(dato_emisor.get('Curp', ""))
            rfc_patron_origen = self.limpiar_cadenas(dato_emisor.get('RfcPatronOrigen', ""))
            entidad = dato_emisor.xpath('nomina12:EntidadSNCF', namespaces={"nomina12": self._url_nomina})
            for nfc in entidad:
                origen_recurso = self.limpiar_cadenas(nfc.get('OrigenRecurso', ""))
                monto_recursos_propios = self.convertir_float(nfc.get('MontoRecursoPropio', ""))
        return {"curp_emisor": curp_emisor, "rfc_patron_origen": rfc_patron_origen, "registro_patronal": registro_patronal, "origen_recurso": origen_recurso, "monto_recursos_propios": monto_recursos_propios}
    def parse_datos_receptor(self, datos_receptor, num_nomina):
        antiguedad = ""
        clave_entidad_federativa = ""
        curp_receptor = ""
        departamento = ""
        fecha_inicio_rel_laboral = ""
        num_empleado = 0
        num_seguridad_social = 0
        periodicidad_pago = ""
        riesgo_puesto = ""
        salario_base_cot_apor = 0
        salario_diario_integrado = 0
        tipo_contrato = ""
        tipo_jornada = ""
        tipo_regimen = ""
        sindicalizado = ""
        puesto = ""
        banco = ""
        cuenta_bancaria = 0
        rfc_labora = ""
        porcentaje_tiempo = 0.0
        sub_contratacion_tiene = 0
        for dato_receptor in datos_receptor:
            de_cuantos_sub = int(dato_receptor.xpath("count(.//nomina12:SubContratacion)", namespaces={"nomina12": self._url_nomina}))
            num = 1
            for sub_contratacion in dato_receptor.xpath('nomina12:SubContratacion', namespaces={"nomina12": self._url_nomina}):
                sub_contratacion_tiene = 1
                rfc_labora = self.limpiar_cadenas(sub_contratacion.get('RfcLabora', ""))
                porcentaje_tiempo = self.convertir_float(sub_contratacion.get('PorcentajeTiempo', ""))
                self._res_sub_contrataciones.append({"cuantos_sub_contratacion": de_cuantos_sub, "num_sub_contratacion": num, "rfc_labora": rfc_labora, "porcentaje_tiempo": self.decimal_2(porcentaje_tiempo), "num_nomina": num_nomina})
                num += 1
            antiguedad = self.limpiar_cadenas(dato_receptor.get('Antigüedad', ""))
            clave_entidad_federativa = self.limpiar_cadenas(dato_receptor.get('ClaveEntFed', ""))
            curp_receptor = self.limpiar_cadenas(dato_receptor.get('Curp', ""))
            departamento = self.limpiar_cadenas(dato_receptor.get('Departamento', ""))
            fecha_inicio_rel_laboral = self.limpiar_cadenas(dato_receptor.get('FechaInicioRelLaboral', ""))
            num_empleado = self.limpiar_cadenas(dato_receptor.get('NumEmpleado', ""))
            num_seguridad_social = self.convertir_int(dato_receptor.get('NumSeguridadSocial', ""))
            periodicidad_pago = self.limpiar_cadenas(dato_receptor.get('PeriodicidadPago', ""))
            riesgo_puesto = self.limpiar_cadenas(dato_receptor.get('RiesgoPuesto', ""))
            salario_base_cot_apor = self.convertir_float(dato_receptor.get('SalarioBaseCotApor', ""))
            salario_diario_integrado = self.convertir_float( dato_receptor.get('SalarioDiarioIntegrado', ""))
            tipo_contrato = self.limpiar_cadenas(dato_receptor.get('TipoContrato', ""))
            tipo_jornada = self.limpiar_cadenas(dato_receptor.get('TipoJornada', ""))
            tipo_regimen = self.limpiar_cadenas(dato_receptor.get('TipoRegimen', ""))
            sindicalizado = self.limpiar_cadenas(dato_receptor.get('Sindicalizado', ""))
            puesto = self.limpiar_cadenas(dato_receptor.get("Puesto", ""))
            banco = self.limpiar_cadenas(dato_receptor.get("Banco", ""))
            cuenta_bancaria = self.convertir_int(dato_receptor.get("CuentaBancaria", ""))
        return {"antiguedad": antiguedad, "clave_entidad_federativa": clave_entidad_federativa, "curp_receptor": curp_receptor, "departamento": departamento, "fecha_inicio_rel_laboral": fecha_inicio_rel_laboral, "num_empleado": num_empleado, "num_seguridad_social": num_seguridad_social, "periodicidad_pago": periodicidad_pago, "riesgo_puesto": riesgo_puesto, "salario_base_cot_apor": salario_base_cot_apor, "salario_diario_integrado": salario_diario_integrado, "tipo_contrato": tipo_contrato, "tipo_jornada": tipo_jornada, "tipo_regimen": tipo_regimen, "sindicalizado": sindicalizado, "puesto": puesto, "banco": banco, "cuenta_bancaria": cuenta_bancaria, "sub_contratacion": sub_contratacion_tiene}
    def parsea_incapacidades(self, incapacidades, num_nomina):
        for incapacidad in incapacidades:
            de_cuantos_incapacidad = int(incapacidad.xpath("count(.//nomina12:Incapacidad)", namespaces={"nomina12": self._url_nomina}))
            num_incapacidad = 1
            for detalles_incapacidad in incapacidad.xpath('nomina12:Incapacidad', namespaces={"nomina12": self._url_nomina}):
                dias_incapacidad = self.convertir_int(detalles_incapacidad.get('DiasIncapacidad', ""))
                tipo_incapacidad = self.limpiar_cadenas(detalles_incapacidad.get('TipoIncapacidad', ""))
                importe_monetario = self.convertir_float(detalles_incapacidad.get('ImporteMonetario', ""))
                self._res_incapacidades.append({"num_nomina": num_nomina, "dias_incapacidad": dias_incapacidad, "tipo_incapacidad": tipo_incapacidad, "importe_monetario": self.decimal_2(importe_monetario), "de_cuantos_incapacidad": de_cuantos_incapacidad, "num_incapacidad": num_incapacidad})
                num_incapacidad += 1
    def parsea_percepciones(self, datos_percepciones, num_nomina):
        prc_total_sueldo = 0
        prc_total_gravado = 0
        prc_total_exento = 0
        prc_total_separacion_indemnizacion = 0
        prc_total_jubilacion = 0

        jub_total_una_exhibicion = 0.0
        jub_total_parcialidad = 0.0
        jub_monto_diario = 0.0
        jub_ingreso_acumulable = 0.0
        jub_ingreso_no_acumulable = 0.0

        hxtas_dias = 0
        hxtas_tipo_horas = ""
        hxtas_horas_extras = 0
        hxtas_importe_pagado = 0.0

        sep_total_pagado = 0.0
        sep_anios_servicio = 0
        sep_ultimo_sueldo_mes_ordinario = 0.0
        sep_ingreso_acumulable = 0.0
        sep_ingreso_no_acumulable = 0.0

        aot_valor_mercado = 0.0
        aot_precio_a_otorgarse = 0.0
        for percepciones in datos_percepciones:
            prc_total_sueldo = self.convertir_float(percepciones.get('TotalSueldos', ""))
            prc_total_gravado = self.convertir_float(percepciones.get('TotalGravado', ""))
            prc_total_exento = self.convertir_float(percepciones.get('TotalExento', ""))
            prc_total_separacion_indemnizacion = self.convertir_float(percepciones.get('TotalSeparacionIndemnizacion', ""))
            prc_total_jubilacion = self.convertir_float(percepciones.get('TotalJubilacionPensionRetiro', ""))
            de_cuantos = int(percepciones.xpath("count(.//nomina12:Percepcion)", namespaces={"nomina12": self._url_nomina}))
            num = 1
            for jubilacion in percepciones.xpath('nomina12:JubilacionPensionRetiro', namespaces={"nomina12": self._url_nomina}):
                jub_total_una_exhibicion += self.convertir_float(jubilacion.get('TotalUnaExhibicion', ""))
                jub_total_parcialidad += self.convertir_float(jubilacion.get('TotalParcialidad', ""))
                jub_monto_diario += self.convertir_float(jubilacion.get('MontoDiario', ""))
                jub_ingreso_acumulable += self.convertir_float(jubilacion.get('IngresoAcumulable', ""))
                jub_ingreso_no_acumulable += self.convertir_float(jubilacion.get('IngresoNoAcumulable', ""))
            for separacion_i in percepciones.xpath('nomina12:SeparacionIndemnizacion', namespaces={"nomina12": self._url_nomina}):
                sep_total_pagado += self.convertir_float(separacion_i.get('TotalPagado', ""))
                sep_anios_servicio += self.convertir_int(separacion_i.get('NumAñosServicio', ""))
                sep_ultimo_sueldo_mes_ordinario += self.convertir_float(separacion_i.get('UltimoSueldoMensOrd', ""))
                sep_ingreso_acumulable += self.convertir_float(separacion_i.get('IngresoAcumulable', ""))
                sep_ingreso_no_acumulable += self.convertir_float(separacion_i.get('IngresoNoAcumulable', ""))
            for percepcion in percepciones.xpath('nomina12:Percepcion', namespaces={"nomina12": self._url_nomina}):
                for horas in percepcion.xpath('nomina12:HorasExtra', namespaces={"nomina12": self._url_nomina}):
                    hxtas_dias += self.convertir_int(horas.get('Dias', ""))
                    tipo_horas = self.limpiar_cadenas(horas.get('TipoHoras', ""))
                    if hxtas_tipo_horas == "":
                        hxtas_tipo_horas = tipo_horas
                    elif int(tipo_horas) >= int(hxtas_tipo_horas):
                        hxtas_tipo_horas = tipo_horas
                    hxtas_horas_extras += self.convertir_int(horas.get('HorasExtra', ""))
                    hxtas_importe_pagado += self.convertir_float(horas.get('ImportePagado', ""))
                for acciones_o in percepcion.xpath('nomina12:AccionesOTitulos', namespaces={"nomina12": self._url_nomina}):
                    aot_valor_mercado += self.convertir_float(acciones_o.get('ValorMercado', ""))
                    aot_precio_a_otorgarse += self.convertir_float(acciones_o.get('PrecioAlOtorgarse', ""))
                importe_gravado = self.convertir_float(percepcion.get('ImporteGravado', ""))
                importe_exento = self.convertir_float(percepcion.get('ImporteExento', ""))
                tipo_percepcion = self.limpiar_cadenas(percepcion.get('TipoPercepcion', ""))
                clave = self.limpiar_cadenas(percepcion.get('Clave', ""))
                concepto = self.limpiar_cadenas(percepcion.get('Concepto', ""))
                self._pdop.append({"de_cuantos": de_cuantos, "num": num, "num_nomina": num_nomina,"tipo_prc_ded_oat": "P", "tipo": tipo_percepcion, "clave": clave, "concepto": concepto, "importe": self.decimal_2(importe_gravado), "importe_exento": self.decimal_2(importe_exento)})
                num += 1    
        return {"prc_total_sueldo": prc_total_sueldo, "prc_total_gravado": prc_total_gravado, "prc_total_exento": prc_total_exento, "prc_total_separacion_indemnizacion": prc_total_separacion_indemnizacion, "prc_total_jubilacion": prc_total_jubilacion, "jub_total_una_exhibicion": jub_total_una_exhibicion, "jub_total_parcialidad": jub_total_parcialidad, "jub_monto_diario": jub_monto_diario, "jub_ingreso_acumulable": jub_ingreso_acumulable, "jub_ingreso_no_acumulable": jub_ingreso_no_acumulable, "hxtas_dias": hxtas_dias, "hxtas_tipo_horas": hxtas_tipo_horas, "hxtas_horas_extras": round(hxtas_horas_extras), "hxtas_importe_pagado": hxtas_importe_pagado, "sep_total_pagado": sep_total_pagado, "sep_anios_servicio": round(sep_anios_servicio), "sep_ultimo_sueldo_mes_ordinario": sep_ultimo_sueldo_mes_ordinario, "sep_ingreso_acumulable": sep_ingreso_acumulable, "sep_ingreso_no_acumulable": sep_ingreso_no_acumulable, "aot_valor_mercado": aot_valor_mercado, "aot_precio_a_otorgarse": aot_precio_a_otorgarse}
    def parsea_dedupciones(self, datos_dedupciones, num_nomina):
        ded_total_impuestos_retenidos  = 0.0
        ded_total_otras_deducciones = 0.0
        for dedupciones in datos_dedupciones: 
            ded_total_impuestos_retenidos  = self.convertir_float(dedupciones.get('TotalImpuestosRetenidos', ""))
            ded_total_otras_deducciones = self.convertir_float(dedupciones.get('TotalOtrasDeducciones', ""))

            de_cuantos = int(dedupciones.xpath("count(.//nomina12:Deduccion)", namespaces={"nomina12": self._url_nomina}))
            num = 1
            for deduccion in dedupciones.xpath('nomina12:Deduccion', namespaces={"nomina12": self._url_nomina}):
                importe = self.convertir_float(deduccion.get('Importe', ""))
                tipo_deduccion = self.limpiar_cadenas(deduccion.get('TipoDeduccion', ""))
                clave = self.limpiar_cadenas(deduccion.get('Clave', ""))
                concepto = self.limpiar_cadenas(deduccion.get('Concepto', ""))
                self._pdop.append({"de_cuantos": de_cuantos, "num": num, "num_nomina": num_nomina,"tipo_prc_ded_oat": "D", "tipo": tipo_deduccion, "clave": clave, "concepto": concepto, "importe": self.decimal_2(importe), "importe_exento": 0})
                num += 1
        return {"ded_total_impuestos_retenidos": ded_total_impuestos_retenidos , "ded_total_otras_deducciones": ded_total_otras_deducciones}
    def parseo_otros_pagos(self, datos_otros_pagos, num_nomina):
        subsidio_causado = 0

        compensa_saldo_a_favor = 0.0
        compensa_anio = 0
        compensa_remanente_saldo_favor = 0.0

        for otros_pagos in datos_otros_pagos:
            de_cuantos = int(otros_pagos.xpath("count(.//nomina12:OtroPago)", namespaces={"nomina12": self._url_nomina}))
            num = 1
            for otro_pago in otros_pagos.xpath('nomina12:OtroPago', namespaces={"nomina12": self._url_nomina}):
                for subsidio in otro_pago.xpath('nomina12:SubsidioAlEmpleo', namespaces={"nomina12": self._url_nomina}):
                    subsidio_causado += self.convertir_float(subsidio.get('SubsidioCausado', ""))
                
                for compensacion in otros_pagos.xpath('nomina12:CompensacionSaldosAFavor', namespaces={"nomina12": self._url_nomina}):
                    compensa_saldo_a_favor += self.convertir_float(compensacion.get('SaldoAFavor', ""))
                    anio = self.convertir_int(compensacion.get('Año', ""))
                    if(compensa_anio == 0):
                        compensa_anio = anio
                    elif int(anio) < int(compensa_anio):
                        compensa_anio = anio
                    compensa_remanente_saldo_favor += self.convertir_float(compensacion.get('RemanenteSalFav', ""))
                
                importe = self.convertir_float(otro_pago.get('Importe', ""))
                tipo_otro_pago = self.limpiar_cadenas(otro_pago.get('TipoOtroPago', ""))
                clave = self.limpiar_cadenas(otro_pago.get('Clave', ""))
                concepto = self.limpiar_cadenas(otro_pago.get('Concepto', ""))
                self._pdop.append({"de_cuantos": de_cuantos, "num": num, "num_nomina": num_nomina,"tipo_prc_ded_oat": "O", "tipo": tipo_otro_pago, "clave": clave, "concepto": concepto, "importe": self.decimal_2(importe), "importe_exento": 0})
                num += 1
        return {"subsidio_causado": subsidio_causado, "compensa_saldo_a_favor": compensa_saldo_a_favor, "compensa_anio": compensa_anio, "compensa_remanente_saldo_favor": compensa_remanente_saldo_favor}
    def parsea_nomina(self):
        nomina12 = self.texto_xml.xpath('//nomina12:Nomina', namespaces={"nomina12": self._url_nomina})
        de_cuantos_nomina = int(self.texto_xml.xpath("count(//nomina12:Nomina)", namespaces={"nomina12": self._url_nomina}))
        num_nomina = 1
        for nomina in nomina12:
            fecha_final_pago = self.convertir_date(self.limpiar_cadenas(nomina.get('FechaFinalPago', "")))
            fecha_inicial_pago = self.convertir_date(self.limpiar_cadenas(nomina.get('FechaInicialPago', "")))
            fecha_pago = self.convertir_date(self.limpiar_cadenas(nomina.get('FechaPago', "")))

            numero_dias_pagados = self.convertir_float(nomina.get('NumDiasPagados', ""))
            tipo_nomina = self.limpiar_cadenas(nomina.get('TipoNomina', ""))
            total_deducciones = self.convertir_float(nomina.get('TotalDeducciones', ""))
            total_otros_pagos = self.convertir_float(nomina.get('TotalOtrosPagos', ""))
            total_percepciones = self.convertir_float(nomina.get('TotalPercepciones', ""))
            version_nomina = self.limpiar_cadenas(nomina.get('Version', ""))
            
            datos_emisor = self.parseo_datos_emisor(nomina.xpath('nomina12:Emisor', namespaces={"nomina12": self._url_nomina}))
            datos_receptor = self.parse_datos_receptor(nomina.xpath('nomina12:Receptor', namespaces={"nomina12": self._url_nomina}), num_nomina)

            datos_percepciones = self.parsea_percepciones(nomina.xpath('nomina12:Percepciones', namespaces={"nomina12": self._url_nomina}), num_nomina)
            datos_deducciones = self.parsea_dedupciones(nomina.xpath('nomina12:Deducciones', namespaces={"nomina12": self._url_nomina}), num_nomina)
            datos_otros_pagos = self.parseo_otros_pagos(nomina.xpath('nomina12:OtrosPagos', namespaces={"nomina12": self._url_nomina}), num_nomina)

            #sub_contratacion = self.parsea_sub_contratacion(nomina.xpath('nomina12:SubContratacion', namespaces={"nomina12": self._url_nomina}))
            self.parsea_incapacidades(nomina.xpath('nomina12:Incapacidades', namespaces={"nomina12": self._url_nomina}), num_nomina)
            self._respuesta.append({"de_cuantos_nomina": de_cuantos_nomina, "num_nomina": num_nomina, "version_nomina": version_nomina, "tipo_nomina": tipo_nomina, "fecha_pago": fecha_pago, "fecha_inicial_pago": fecha_inicial_pago, "fecha_final_pago": fecha_final_pago, "num_dias_pagados": self.decimal_2(numero_dias_pagados), "total_percepciones": self.decimal_2(total_percepciones), "total_deducciones": self.decimal_2(total_deducciones), "total_otros_pagos": self.decimal_2(total_otros_pagos), "registro_patronal": datos_emisor['registro_patronal'], "curp_emisor": datos_emisor['curp_emisor'], "rfc_patron_origen": datos_emisor['rfc_patron_origen'], "origen_recurso": datos_emisor['origen_recurso'], "monto_recursos_propios": self.decimal_2(datos_emisor['monto_recursos_propios']), "curp_receptor": datos_receptor['curp_receptor'], "num_seguridad_social_receptor": datos_receptor['num_seguridad_social'], "fecha_inicio_rel_laboral": self.convertir_date(datos_receptor['fecha_inicio_rel_laboral']), "antiguedad": datos_receptor['antiguedad'], "tipo_contrato": datos_receptor['tipo_contrato'], "sindicalizado": datos_receptor['sindicalizado'], "tipo_jornada": datos_receptor['tipo_jornada'], "tipo_regimen": datos_receptor['tipo_regimen'], "num_empleado": datos_receptor['num_empleado'], "departamento": datos_receptor['departamento'], "puesto": datos_receptor['puesto'], "riesgo_puesto": datos_receptor['riesgo_puesto'], "periodicidad_pago": datos_receptor['periodicidad_pago'], "banco": datos_receptor['banco'], "cuenta_bancaria": datos_receptor['cuenta_bancaria'], "salario_base_cot_apor": self.decimal_2(datos_receptor['salario_base_cot_apor']), "salario_diario_integrado": self.decimal_2(datos_receptor['salario_diario_integrado']), "clave_ent_fed": datos_receptor['clave_entidad_federativa'], "sub_contratacion": datos_receptor["sub_contratacion"], "prc_total_sueldo": self.decimal_2(datos_percepciones["prc_total_sueldo"]), "total_gravado": self.decimal_2(datos_percepciones["prc_total_gravado"]), "total_exento": self.decimal_2(datos_percepciones["prc_total_exento"]), "prc_total_separacion_indemnizacion": self.decimal_2(datos_percepciones["prc_total_separacion_indemnizacion"]), "prc_total_jubilacion": self.decimal_2(datos_percepciones["prc_total_jubilacion"]), "aot_valor_mercado": self.decimal_2(datos_percepciones["aot_valor_mercado"]), "aot_precio_a_otorgarse": self.decimal_2(datos_percepciones["aot_precio_a_otorgarse"]), "hxtas_dias": datos_percepciones["hxtas_dias"], "hxtas_tipo_horas": datos_percepciones["hxtas_tipo_horas"], "hxtas_horas_extras": datos_percepciones["hxtas_horas_extras"], "hxtas_importe_pagado": self.decimal_2(datos_percepciones["hxtas_importe_pagado"]), "jub_total_una_exhibicion": self.decimal_2(datos_percepciones["jub_total_una_exhibicion"]), "jub_total_parcialidad": self.decimal_2(datos_percepciones["jub_total_parcialidad"]), "jub_monto_diario": self.decimal_2(datos_percepciones["jub_monto_diario"]), "jub_ingreso_acumulable": self.decimal_2(datos_percepciones["jub_ingreso_acumulable"]), "jub_ingreso_no_acumulable": self.decimal_2(datos_percepciones["jub_ingreso_no_acumulable"]), "sep_total_pagado": self.decimal_2(datos_percepciones["sep_total_pagado"]), "sep_anios_servicio": datos_percepciones["sep_anios_servicio"], "sep_ultimo_sueldo_mes_ordinario": self.decimal_2(datos_percepciones["sep_ultimo_sueldo_mes_ordinario"]), "sep_ingreso_acumulable": self.decimal_2(datos_percepciones["sep_ingreso_acumulable"]), "sep_ingreso_no_acumulable": self.decimal_2(datos_percepciones["sep_ingreso_no_acumulable"]), "ded_total_impuestos_retenidos": self.decimal_2(datos_deducciones["ded_total_impuestos_retenidos"] ), "ded_total_otras_deducciones": self.decimal_2(datos_deducciones["ded_total_otras_deducciones"]), "subsidio_causado": self.decimal_2(datos_otros_pagos["subsidio_causado"]), "compensa_saldo_a_favor": self.decimal_2(datos_otros_pagos["compensa_saldo_a_favor"]), "compensa_anio": datos_otros_pagos["compensa_anio"], "compensa_remanente_saldo_favor": self.decimal_2(datos_otros_pagos["compensa_remanente_saldo_favor"])})
            num_nomina += 1

            