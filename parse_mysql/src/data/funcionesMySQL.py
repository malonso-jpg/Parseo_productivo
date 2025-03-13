import mysql.connector
from mysql.connector import Error
import os
import traceback
class funcionesMySQL:
    _connection = None
    def __enter__(self):
        try:
            self._connection = mysql.connector.connect(
                user=os.environ['USER'], password=os.environ['PASSW'], host=os.environ['HOST'], database=os.environ['DB'], port =os.environ['PUERTO']
            )
            if self._connection.is_connected():
                return self
            else:
                print("ERROR: No se pudo conectar a MySQL.")
                return None
        except Error as e:
            print("ERROR al conectar a MySQL:", e)
            if('TOO MANY CONNECTIONS' in str(e).upper()):
                return False
            return None

    def __exit__(self, exc_type, exc_value, traceback):
        if self._connection is not None and self._connection.is_connected():
            try:
                self._connection.close()
                #print("Conexión cerrada con éxito a MySQL.")
            except Error as e:
                print("Error al cerrar la conexión a MySQL:", e)
    def insert(self, datos, tabla):
        try:
            cursor = self._connection.cursor()
            columnas = ', '.join(datos.keys())
            marcadores = ', '.join(['%s'] * len(datos))
            query = f"INSERT INTO {tabla} ({columnas}) VALUES ({marcadores})"
            #print('\n ####################################',tuple(datos.values()), '\n ####################################')
            cursor.execute(query, tuple(datos.values()))
            self._connection.commit()
            return True
        except Error as e:
            error_info = traceback.format_exc()
            print(error_info, tabla)
            return str(error_info)

    def insert_muchos(self, datos, tabla):
        try:
            cursor = self._connection.cursor()
            columnas = ', '.join(datos[0].keys())
            marcadores = ', '.join(['%s'] * len(datos[0]))
            query = f"INSERT INTO {tabla} ({columnas}) VALUES ({marcadores})"
            batch_size = 10000
            for i in range(0, len(datos), batch_size):
                batch_data = datos[i:i+batch_size]
                values = [tuple(dato.values()) for dato in batch_data]
                cursor.executemany(query, values)
            self._connection.commit()
            return True
        except Error as e:
            error_info = traceback.format_exc()
            print(error_info, tuple(datos.values()), tabla)
            return str(error_info)

    def mysql_query(self, datos_nesesito, tabla, where=None):
        try:
            consulta = f"SELECT {datos_nesesito} FROM {tabla}"
            if where:
                consulta += f" WHERE {where}"
            cursor = self._connection.cursor(dictionary=True)
            cursor.execute(consulta)
            result = cursor.fetchall()
            return [True, result]
        except Error as e:
            print("ERROR al ejecutar consulta en MySQL:", e)
            return [False, str(e)]

    def mysql_update(self, datos, tabla, where_clause=None):
        try:
            cursor = self._connection.cursor()
            set_clause = ', '.join([f"{columna} = %s" for columna in datos.keys()])
            query = f"UPDATE {tabla} SET {set_clause}"
            if where_clause:
                query += f" WHERE {where_clause}"
            cursor.execute(query, tuple(datos.values()))
            self._connection.commit()
            return True
        except Error as e:
            error_info = traceback.format_exc()
            return str(error_info)

    def delete_mysql(self, tabla, where):
        try:
            cursor = self._connection.cursor()
            consulta = f"DELETE FROM {tabla}"
            if(where):
                consulta += f" WHERE {where}"
            cursor.execute(consulta)
            self._connection.commit()
            return True
        except Error as e:
            error_info = traceback.format_exc()
            return str(error_info)