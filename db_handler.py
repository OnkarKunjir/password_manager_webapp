import sqlite3

class dbHandler:
    def __init__(self):
        self.connection = sqlite3.connect("password_manager.db" , check_same_thread=False)
        self.cursor = self.connection.cursor()

        #creating tables 
        self.cursor.execute('CREATE TABLE IF NOT EXISTS admin(user_name TEXT UNIQUE NOT NULL , password TEXT NOT NULL)')
        self.cursor.execute('CREATE TABLE IF NOT EXISTS authenticate(user_name TEXT UNIQUE NOT NULL , mail_id TEXT UNIQUE NOT NULL , password TEXT NOT NULL , valid_till DATE NOT NULL)')
        self.cursor.execute('CREATE TABLE IF NOT EXISTS pending_verification(user_name TEXT UNIQUE NOT NULL , mail_id TEXT UNIQUE NOT NULL , password TEXT NOT NULL)')
        self.cursor.execute('CREATE TABLE IF NOT EXISTS plans(plan_name TEXT UNIQUE NOT NULL , description TEXT NOT NULL , price INTEGER NOT NULL , validity INTEGER NOT NULL)')
        self.cursor.execute('CREATE TABLE IF NOT EXISTS analytics(month DATE NOT NULL UNIQUE , accounts_signedup INTEGER , accounts_upgraded INTEGER , accounts_deleted INTEGER )')
        #adding default admin account
        try:
            self.cursor.execute('INSERT INTO admin VALUES("root" , "root123")')
            self.cursor.execute('INSERT INTO plans VALUES("monthly" , "this is monthly plan" , 300 , 30)')
            self.cursor.execute('INSERT INTO analytics VALUES(DATE("NOW" , "start of month") , 0 , 0 , 0)')
            self.connection.commit()
        except sqlite3.Error as e:
            print(e)
            pass
        
    def authenticate_admin(self , user_name , password):
        #function to authenticate admins...
        try:
            query = 'SELECT password FROM admin WHERE user_name = "' + user_name + '"'
            self.cursor.execute(query)
            p = self.cursor.fetchone()
            if p[0] == password:
                return True
            return False
        except:
            return False 

    def add_plan(self , plan_name , description , price , validity):
        #function for admin to add new plans to website...
        try:
            query = 'INSERT INTO plans VALUES ("' + plan_name + '" , "' + description + '" , ' + str(price) + ' , ' + str(validity) + ')'
            self.cursor.execute(query)
            self.connection.commit()
            return True
        except sqlite3.Error:
            return False

    def get_valid_till(self , user_name):
        try:
            query = 'SELECT valid_till FROM authenticate WHERE user_name = "' + user_name + '"'
            self.cursor.execute(query)
            return self.cursor.fetchone() 
        except sqlite3.Error as e:
            print(e)
            return False

    def authenticate(self , user_name , password):
        #function to authenticate an perticular login attempt
        #if user is authenticated then return all data stored in that users table
        try:
            query = 'SELECT password FROM authenticate WHERE user_name = "' + user_name + '"'
            self.cursor.execute(query)
            p = self.cursor.fetchone()
            if p[0] == password:
                return True
            return False
        except:
            return False 

    def get_data(self , user_name):
            query = 'SELECT * FROM ' + user_name 
            self.cursor.execute(query)
            data = self.cursor.fetchall()
            return data

    def add_password(self , user_name , website , password):
        #add new password in (in useres table)
        try:
            query = 'INSERT INTO '  + user_name + ' values("' + website + '" , "' + password + '")'
            self.cursor.execute(query)
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            print(e)
            return False

    def sign_up(self , email , user_name , password):
        #create new user acount if not exist..
        try:
            query = 'SELECT user_name FROM authenticate WHERE user_name = "' + user_name + '"'
            self.cursor.execute(query)
            already_exists = self.cursor.fetchone()
            if already_exists == None:
                query = 'INSERT INTO pending_verification values("' + user_name +'" , "' + email +'" , "' + password + '")'
                self.cursor.execute(query)
                self.connection.commit()
                # query = 'CREATE TABLE IF NOT EXISTS ' + user_name + ' (website TEXT UNIQUE NOT NULL, password TEXT NOT NULL)'
                # self.cursor.execute(query)
                return True
            return False
        except sqlite3.Error as e:
            print(e)
            return False
    
    def verify_pending(self , user_name):
        try:
            query = 'UPDATE analytics SET accounts_signedup = accounts_signedup + 1 WHERE month = DATE("NOW" , "start of month")'
            self.cursor.execute(query)

            query = 'SELECT * FROM pending_verification WHERE user_name = "' + user_name + '"'
            self.cursor.execute(query)
            (user_name , email , password) =  self.cursor.fetchone()
            query = 'DELETE FROM pending_verification WHERE user_name = "' + user_name + '"'
            self.cursor.execute(query)

            query = 'INSERT INTO authenticate values("' + user_name +'" , "' + email +'" , "' + password + '" , DATE("NOW" , "+10 DAY"))'
            self.cursor.execute(query)
            self.connection.commit()
            query = 'CREATE TABLE IF NOT EXISTS ' + user_name + ' (website TEXT UNIQUE NOT NULL, password TEXT NOT NULL)'
            self.cursor.execute(query)
            return True
        except sqlite3.Error as e:
            print(e)
            return False
        
    
    def remove_website(self , user_name , website):
        try:
            query = 'DELETE FROM ' + user_name + ' WHERE website = "' + website + '"'
            self.cursor.execute(query)
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            return False

    def update_password(self , user_name , website , new_pass):
        try:
            query = 'UPDATE ' + user_name + ' SET password = "' + new_pass + '" WHERE website = "'+website+'"'
            self.cursor.execute(query)
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            return False 

    def delete_account(self , user_name):
        try:

            query = 'UPDATE analytics SET accounts_deleted = accounts_deleted + 1 WHERE month = DATE("NOW" , "start of month")'
            self.cursor.execute(query)


            query = 'DELETE FROM authenticate WHERE user_name = "' + user_name + '"'
            self.cursor.execute(query)
            
            query = 'DELETE FROM ' + user_name 
            self.cursor.execute(query)
            
            query = 'DROP TABLE ' + user_name
            self.cursor.execute(query)

            self.connection.commit()
            return True
        except sqlite3.Error as e:
            print(e)
            return False

    def paln_info(self , plan_name):
        query = 'SELECT price , validity FROM plans WHERE plan_name = "' + plan_name + '"'
        self.cursor.execute(query)
        (price , validity) = self.cursor.fetchone()
        return (price , validity) 

    def get_all_plans(self):
        query = 'SELECT * FROM plans'
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def update_validity(self , user_name , validity):
        query = 'UPDATE analytics SET accounts_upgraded = accounts_upgraded + 1 WHERE month = DATE("NOW" , "start of month")'
        self.cursor.execute(query)

        query = 'UPDATE authenticate SET valid_till = DATE(valid_till , "+' + str(validity) + ' day") WHERE user_name = "' + user_name + '"'
        print(query)
        self.cursor.execute(query)
        self.connection.commit()

    def get_analytics(self):
        query = 'SELECT * FROM analytics'
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def __del__(self):
        #to close connection with database.
        self.cursor.close()
        self.connection.close()

# if __name__ == "__main__":
#     handler = dbHandler()
#     print('sign up' , handler.sign_up('onkarkunjir8gmailcom' , 'onkar123'))
#     print('auth' , handler.authenticate('onkarkunjir8gmailcom' , 'onkar123'))
#     print(handler.add_password('onkarkunjir8gmailcom' , 'twitter' , 'twitter password'))
#     print(handler.remove_website('onkarkunjir8gmailcom' , 'twitter'))
