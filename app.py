from flask import Flask, request, render_template , redirect , url_for , session
from db_handler import dbHandler
import re 
import sqlite3
from flask_mail import Mail , Message
from itsdangerous import URLSafeTimedSerializer


app = Flask(__name__)
#app.permanent_session_lifetime = False
app.secret_key = "3a4ds3fdfad3s2fas5d"
mail_settings = {
    "MAIL_SERVER": 'smtp.gmail.com',
    "MAIL_PORT": 465,
    "MAIL_USE_TLS": False,
    "MAIL_USE_SSL": True,
    "MAIL_USERNAME": 'onkarkunjir88@gmail.com',
    "MAIL_PASSWORD": 'Just type OK @2000'
}
app.config.update(mail_settings)
mail = Mail(app)
serializer = URLSafeTimedSerializer("3a4ds3fdfad3s2fas5d")
handler = dbHandler()

@app.route('/')
def test():
    return render_template('manage_plans.html' , plans = handler.get_all_plans())

@app.route('/login_admin' , methods = ['POST' , 'GET'])
def admin_login():
    if request.method == 'POST':
        user_name = request.form.get('user_name')
        password = request.form.get('pswd')
        auth = handler.authenticate_admin(user_name , password)
        if auth:
            #session[user_name] = True
            return render_template('admin_dashbord.html' , analytics = handler.get_analytics()[-1])
        return 'login failed'
    return render_template('form.html' , form_type = 'Log In')


#functions for user to use the app

@app.route('/login' , methods = ['POST' , 'GET'])
def login():
    #login function for users...
    if request.method == 'POST':
        user_name = request.form.get('user_name')
        password = request.form.get('pswd')
        
        auth = handler.authenticate(user_name , password)
        if auth:
            session[user_name] = True
            return redirect( url_for('dashbord' , user_name = user_name))
        return 'login failed'
    return render_template('form.html' , form_type = 'Log In')

@app.route('/sign_up' , methods = ['GET' , 'POST'])
def sign_up():
    #signup and add user to pending verification table till they verify
    if request.method == 'POST':
        user_name = request.form.get('user_name')
        email = request.form.get('mail')
        password = request.form.get('pswd')
    
        done = handler.sign_up(email , user_name , password)
        #verifying email address...
        if done:
        #     session[user_name] = True
            token = serializer.dumps(user_name , salt="confirm-email")
            msg = url_for('confirm_email' , token = token , _external = True)
            msg = Message('Email verification' , sender=app.config.get('MAIL_USERNAME') , recipients=[email] , body=msg)
            mail.send(msg)
            return f"verification link sent to {email}"
        return 'Sign Up failed'
    return render_template('form.html' , form_type = 'Sign Up')

@app.route('/confirm_email/<token>')
def confirm_email(token):
    #confirm users email address and sign them up
    user_name = serializer.loads(token , salt="confirm-email" , max_age=3600)
    done = handler.verify_pending(user_name)
    if done:
        session[user_name] = True
        return redirect(url_for('subscribe_plan' , user_name = user_name))
    return 'Sign Up failed'
    
@app.route('/dashbord/<user_name>')
def dashbord(user_name):
    #function to show dashbord where user can interact with the database...
    if session.get(user_name):
        valid_till = handler.get_valid_till(user_name)
        data = handler.get_data(user_name)
        return render_template('dashbord.html' , valid_till = valid_till , user_name = user_name ,  data = data)
    return redirect(url_for('login'))

@app.route('/dashbord/<user_name>/add_new_password' , methods = ['POST' , 'GET'])
def add_password(user_name):
    if session.get(user_name):
        if request.method == 'POST':
            website = request.form.get('website')
            password = request.form.get('pswd')
            handler.add_password(user_name , website , password)
            return redirect(url_for('dashbord' , user_name = user_name))
        return render_template('add_password.html')   
    return redirect(url_for('login'))

@app.route('/dashbord/<user_name>/remove/<website>')
def remove_password(user_name , website):
    if session.get(user_name):
        handler.remove_website(user_name , website)
        return redirect(url_for('dashbord' , user_name = user_name))

@app.route('/dashbord/<user_name>/update/<website>' , methods = ['POST' , 'GET'])
def update_password(user_name , website):
    if request.method == 'POST':
        password = request.form.get('pswd')
        handler.update_password(user_name , website , password)
        return redirect(url_for('dashbord' , user_name = user_name))
    return render_template('add_password.html')


@app.route('/dashbord/<user_name>/delete_account')
def delete_account(user_name):
    if session.get(user_name):
        handler.delete_account(user_name)
        session[user_name] = None
        return redirect(url_for('login'))

@app.route('/dashbord/logout/<user_name>')
def logout(user_name):
    session[user_name] = None
    return redirect(url_for('login'))



#fucntions to perform all the payment related stuffs
@app.route('/subscribe_plan/<user_name>')
def subscribe_plan(user_name):
    return render_template('plans.html' , user_name = user_name , plans = handler.get_all_plans())


@app.route('/payment/<user_name>/<plan_name>')
def payment(user_name , plan_name):
    if session[user_name] == True:
        if plan_name == "free_trail":
            return redirect(url_for('dashbord' , user_name = user_name))
        else:
            (price , validity) = handler.paln_info(plan_name)
            handler.update_validity(user_name , validity)
            return redirect(url_for('dashbord' , user_name = user_name))
    else:
        return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)