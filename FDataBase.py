import sqlite3


class FDataBase:
    def __init__(self, db):
        self.__db = db
        self.__cur = db.cursor()

    def addProfile(self, username, password):
        try:
            self.__cur.execute(f"SELECT COUNT() as `count` FROM profiles WHERE username LIKE '{username}'")
            res = self.__cur.fetchone()
            if res['count'] > 0:
                print('Profile already exist')
                return False
            self.__cur.execute('INSERT INTO profiles VALUES(NULL, ?, ?)', (username, password))
            self.__db.commit()
        except sqlite3.Error as e:
            print(f'DB error {e}')
            return False
        return True

    def getProfile(self, username):
        try:
            print(username)
            self.__cur.execute(f"SELECT password FROM profiles WHERE username = '{username}'")
            res = self.__cur.fetchone()
            if res: return res[0]
        except:
            print('DB error')
            return []
