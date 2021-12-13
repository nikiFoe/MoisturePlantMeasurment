import sqlite3


class SQLHandler:

    def __init__(self):
        self.connectionSQL, self.cursor  = self.loadSQL()

    def loadSQL(self):
        connectionSQL = sqlite3.connect("moisture.db")
        cursor = connectionSQL.cursor()
        self.loadTable(cursor)
        return connectionSQL, cursor

    def loadTable(self, cursor):
        try:
            sql_command = """
                            CREATE TABLE moist ( 
                            _number INTEGER PRIMARY KEY,
                            _time DATE,
                            _sensor varchar(255), 
                            _humidity INTEGER);"""

            cursor.execute(sql_command)
        except sqlite3.OperationalError:
            print("Table already existing")
            sql_command = """DELETE FROM moist"""
            cursor.execute(sql_command)


    def safeSQL(self):
        self.connectionSQL.commit()

    def setSQL(self, sqlInput):
        self.connectionSQL = sqlInput

    def getSQL(self):
        return self.connectionSQL

    def getCursor(self):
        return self.cursor

    def deleteTable(self):
        pass

