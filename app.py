from flask import (
    Flask,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for
)
import mysql.connector as connector
import pandas as pd

app = Flask(__name__)
class User:
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

    def __repr__(self):
        return f'<User: {self.username}>'

users = []
users.append(User(id=1, username='Anthony', password='password'))
users.append(User(id=2, username='Becca', password='secret'))
users.append(User(id=3, username='Carlos', password='somethingsimple'))


app = Flask(__name__)
app.secret_key = 'somesecretkeythatonlyishouldknow'

@app.before_request
def before_request():
    g.user = None

    if 'user_id' in session:
        user = [x for x in users if x.id == session['user_id']][0]
        g.user = user
        

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session.pop('user_id', None)

        username = request.form['username']
        password = request.form['password']
        
        user = [x for x in users if x.username == username]
        if user:
            user = user[0]
        if user and user.password == password:
            session['user_id'] = user.id
            return redirect(url_for('states'))

        return redirect(url_for('login'))

    return render_template('login.html')


con = connector.connect(host = 'localhost',
                        port = '3309',
                        user = 'root',
                        password = '')

c = con.cursor(buffered=True)

@app.route('/states')
def states():
    
    if not g.user:
        return redirect(url_for('login'))
    q = 'USE jobs_data'
    c.execute(q)
    con.commit()
    q = 'select * from states'
    c.execute(q)
    data = c.fetchall()
    print(data)
    return render_template('states.html', data = data)

@app.route('/cat/<int:id>',methods=['GET','POST'])
def cat(id):
    if not g.user:
        return redirect(url_for('login'))
    q = 'USE jobs_data'
    c.execute(q)
    con.commit()
    # q = '''SELECT category FROM job_types_1 WHERE s_id="%s"''' %(id)
    q = '''SELECT distinct category FROM job_types_1 WHERE s_id="%s"''' %(id)
    c.execute(q)
    data = c.fetchall()
    print(data)
    return render_template('categories.html', data = data, s_id = id)

@app.route('/subcat/<int:id>/<string:cat>',methods=['GET','POST'])
def subcat(id,cat):
    if not g.user:
        return redirect(url_for('login'))
    q = 'USE jobs_data'
    c.execute(q)
    con.commit()
    print(cat,id)
    q = '''SELECT distinct sub_category FROM job_types_2 WHERE s_id=%s and category="%s"''' %(id,cat)
    c.execute(q)
    data = c.fetchall()
    return render_template('subcat.html', data = data, s_id = id , cat = cat)

@app.route('/jobs/<int:id>/<string:cat>/<string:subcat>',methods=['GET','POST'])
def jobs(id,cat,subcat):
    if not g.user:
        return redirect(url_for('login'))
    q = 'USE jobs_data'
    c.execute(q)
    con.commit()
    print(cat,id,subcat)
    q = '''select * from jobs where id IN (select sc_id from job_types_2 where sub_category = "%s" and category = "%s" and s_id = %s)''' %(subcat,cat,id)
    c.execute(q)
    data = c.fetchall()
    print(data)
    return render_template('jobs.html', data = data)

if __name__ == '__main__':
   app.run(debug=True)