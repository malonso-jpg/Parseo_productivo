from parseo.manipudorDatos import manipudorDatos

class parseoRelaciones(manipudorDatos):

    def __init__(self, texto_xml, url_cfdi):
        self.texto_xml = texto_xml
        self.url_cfdi = url_cfdi
        self._respuesta = []
        if(texto_xml != ""):
            self.parsea_relaciones()
    @property
    def obtener_relaciones(self):
        if not self._respuesta:
            return [False]
        return self._respuesta
    def parsea_relaciones(self):
        de_cuantos = int(self.texto_xml.xpath("count(//cfdi:CfdiRelacionados//cfdi:CfdiRelacionado)", namespaces={"cfdi": self.url_cfdi}))
        cfdis_relacionados = self.texto_xml.xpath('//cfdi:CfdiRelacionados', namespaces={"cfdi": self.url_cfdi})
        num = 1
        for relacionados in cfdis_relacionados:
            tipo_relacion = str(relacionados.get("TipoRelacion", ""))
            relaciones = relacionados.xpath('.//cfdi:CfdiRelacionado', namespaces={"cfdi": self.url_cfdi})
            for relacion in relaciones:
                uuid_relacionado = self.limpiar_cadenas(relacion.get("UUID", "")).upper()
                datos = {"cuantas_relaciones": de_cuantos, "num_relaciones": num, "tipo_relacion": tipo_relacion, "uuid_relacionado": uuid_relacionado}
                self._respuesta.append(datos)
                num += 1