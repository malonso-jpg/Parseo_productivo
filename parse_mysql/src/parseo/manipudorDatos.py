import json
from decimal import Decimal
from datetime import datetime

class manipudorDatos:

    def limpiar_cadenas(self, texto):
        try:
            if texto.strip():
                texto = texto.replace("\n", " ")
                texto = texto.replace("\r", " ")
                texto = texto.replace("\f", " ")
                texto = texto.replace("\t", " ")
                texto = texto.replace("'", "~")
                texto = texto.replace('"', '')
                texto = texto.replace(",", "")
                texto = texto.replace(";", "")
                texto = ' '.join(texto.split())
                texto = texto.strip()
            else:
                texto = ""
        except Exception:
          texto = ""
        return str(texto)
    
    def convertir_float(self, valor):
        try:
            return float(valor)
        except ValueError:
            return 0.0
    
    def convertir_int(self, valor):
        try:
            return int(valor)
        except ValueError:
            return 0
    def convertir_a_pesos(self, tipo_cambio, valor):
        return round(valor * float(tipo_cambio), 2)
    
    def generar_json(self, datos):
        return json.dumps(datos, indent=4)
    
    def decimal_5(self, valor):
        valor_decimal = Decimal(str(valor))
        num_decimales = abs(valor_decimal.as_tuple().exponent)
        if num_decimales <= 5:
            dato = valor_decimal
        else:
            dato = round(valor_decimal, 5)
        return dato
    
    def decimal_2(self, valor):
        valor_decimal = Decimal(str(valor))
        num_decimales = abs(valor_decimal.as_tuple().exponent)
        if num_decimales <= 2:
            dato = valor_decimal
        else:
            dato = round(valor_decimal, 2)
        return dato
    
    def convertir_date(self, valor):
        valor = valor.strip()
        if(valor != ''):
            if len(valor)>11:
                if( 'T' in valor):
                    valor = datetime.strptime(valor, '%Y-%m-%dT%H:%M:%S')
                else:
                    valor = datetime.strptime(valor, '%Y-%m-%d %H:%M:%S')
            else:
                fecha = datetime.strptime(valor, '%Y-%m-%d')
                valor = datetime(fecha.year, fecha.month, fecha.day)
        else:
            valor = None
        return valor
    def limitar_cadena(self, cadena, longitud):
        return cadena[:longitud]