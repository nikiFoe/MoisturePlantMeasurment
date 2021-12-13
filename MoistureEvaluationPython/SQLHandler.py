import sqlite3


class SQLHandler:

    def __init__(self):
        self.connectionSQL, self.cursor  = self.loadSQL()
        self.weeklySQL, self.cursorWeekly = self.loadWeeklySQL()

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

    def getWeeklySQL(self):
        return self.weeklySQL

    def setWeeklySQL(self, sqlInput):
        self.weeklySQL = sqlInput

    def safeWeeklySQL(self):
        self.weeklySQL.commit()

    def loadWeeklySQL(self):
        weeklySQL = sqlite3.connect("weeklySQL.db")
        weeklyCursor = weeklySQL.cursor()
        self.weeklySQLTable(weeklyCursor)
        return weeklySQL, weeklyCursor

    def weeklySQLTable(self, cursor):
        try:
            sql_command = """
                            CREATE TABLE weekly ( 
                            _number INTEGER PRIMARY KEY,
                            _time DATE,
                            _sensor varchar(255), 
                            _humidity INTEGER);"""

            cursor.execute(sql_command)
        except sqlite3.OperationalError:
            sql_command = """DELETE FROM weekly"""
            cursor.execute(sql_command)
            print("Table already existing")

    def copyData(self):
        weeklySQL = self.loadWeeklySQL()
        weeklySQLCursor = weeklySQL.cursor()
        command = """INSERT INTO Destination SELECT * FROM Source;"""