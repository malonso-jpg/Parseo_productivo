from data.funcionesMySQL import funcionesMySQL
from parseo.manipudorDatos import manipudorDatos

def prueba():
    manipular = manipudorDatos()
    with funcionesMySQL() as conexion:
        fecha = '1959-08-20 12:00:00'
        fecha_2 = manipular.convertir_date(fecha)
        print(fecha_2)
        print(conexion.insert({'fecha': fecha_2}, 'prueba'))
prueba()