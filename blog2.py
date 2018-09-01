from flask import Flask,render_template,flash,redirect,url_for,session,logging,request,jsonify,render_template_string,make_response,Blueprint
from wtforms import Form,StringField,TextAreaField,PasswordField,validators,widgets
from passlib.hash import sha256_crypt
from math import ceil
from flask_paginate import Pagination, get_page_parameter
from  flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import locale


app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Users/caner/Desktop/website/info.db'
db = SQLAlchemy(app)

class Users(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(80))
    email = db.Column(db.String(80))
    username = db.Column(db.String(80))
    password = db.Column(db.String(80))
    
class Articles(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(80))
    author = db.Column(db.String(80))
    content = db.Column(db.String(80))
    created_date = db.Column(db.String(80))
    picture = db.Column(db.String(80))
    #created_date = db.Column(db.String(80))
    goruntulenme = db.Column(db.Integer, default = 0)

#kullanıcı giriş decorator'ı
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "logged_in" in session:
            return f(*args, **kwargs)
        else:
            flash("Bu sayfayı görüntülemek için lütfen giriş yapın", "warning")
            return redirect(url_for("login"))
    return decorated_function
#kayıt formu
class RegisterForm(Form):
    name = StringField("İsim Soyisim", validators=[
        validators.length(min=4,max=25),validators.data_required(message= "Lütfen isim ve soyisminizi giriniz")
    ])
    
    user_name = StringField("Kullanıcı adı", validators=[
        validators.length(min=4,max=25),validators.data_required(message= "Lütfen bir kullanıcı adı seçiniz")
    ])
    
    email = StringField("Email Adresiniz", validators=[
        validators.Email(message="Lütfen geçerli bir email adresi girin"),validators.data_required(message= "Lütfen geçerli bir email adresi girin")
    ])
    
    password = PasswordField("Parola", validators=[
        validators.length(min=4,max=25),validators.data_required(message="Lütfen bir parola belirleyin"),
        validators.EqualTo(fieldname = "confirm",message="Parolalarınız uyuşmuyor")
    ])
    confirm = PasswordField("Parolanızı doğruayınız")

class LoginForm(Form):
    user_name = StringField("Kullanıcı Adı")
    password = PasswordField("Parola")




@app.route("/")

def index():
    
    #sorgu = "Select * From articles  ORDER BY goruntulenme DESC limit 0,3;"
    articles = Articles.query.order_by(Articles.goruntulenme.desc()).all()[:3]
    
    resim_1 = articles[0].picture
    resim_2= articles[1].picture
    resim_3= articles[2].picture
    return render_template("index.html",articles=articles,resim_1=resim_1,resim_2=resim_2,resim_3=resim_3) 

@app.route("/about")
def about():
    return render_template("about.html")



@app.route("/ekle")
def add_numbers():
    a = request.args.get('a', 0, type=int)
    b = request.args.get('b', 0, type=int)
    return jsonify(result=a + b)
    
"""@app.route("/add",methods = ["POST"])
def add():
    title = request.form.get("title")
    newTodo = Todo(title = title,complete = False)
    db.session.add(newTodo)
    db.session.commit()
    return redirect(url_for("index"))"""


@app.route("/register",methods = ["GET","POST"])
def register():
    form = RegisterForm(request.form)
    articles = Articles.query.all()
    if request.method == "POST" and form.validate():
        name = form.name.data
        user_name = form.user_name.data
        email = form.email.data
        password = sha256_crypt.encrypt(form.password.data)
        
        #sorgu = "INSERT INTO users(name,email,username,password) VALUES(%s,%s,%s,%s)"
        kayit = Users(name = name,username = user_name,email = email,password = password)
        db.session.add(kayit)
        db.session.commit()
        flash("Kayıt işlemi başarılı!","success")
        return redirect(url_for("login"))
    else:
        return render_template("register.html", form = form,articles = articles)




@app.route("/login",methods =["GET","POST"])
def login():
    form = LoginForm(request.form)
    if request.method == "POST":
        user_name = form.user_name.data
        password_entered = form.password.data

        """cursor = mysql.connection.cursor()
        sorgu = "Select * From users where username = %s"
        result = cursor.execute(sorgu,(user_name,))"""
        bilgiler = Users.query.filter_by(username = user_name).first()

        if bilgiler:

            real_password = bilgiler.password
            if sha256_crypt.verify(password_entered,real_password):
                flash("Giriş Başarılı!","success")
                session["logged_in"] = True
                session["user_name"] = user_name        
                return redirect(url_for("index"))
            else:
                flash("{} kullanıcı ismiyle kayıtlı doğru parola bulunamadı".format(user_name),"danger")
                return redirect(url_for("login"))
        else:
            flash("Böyle bir kullanıcı bulunmamakta","danger")
            return redirect(url_for("login"))

    
    
    
    return render_template("login.html",form = form)
    
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route("/dashboard")
@login_required
def dashboard():
    """cursor = mysql.connection.cursor()
    sorgu = "Select * From articles where author = %s ORDER BY id DESC"
    result = cursor.execute(sorgu,(session["user_name"],))"""
    articles = Articles.query.filter_by(author = session["user_name"]).order_by(Articles.id.desc()).all()
    if  articles:
        #articles = cursor.fetchall()
        return render_template("dashboard.html", articles = articles)
    else:
        return render_template("dashboard.html")



@app.route("/articles/<string:id>",methods=["GET","POST"])
def article(id):
    """cursor = mysql.connection.cursor()
    sorgu = "Select * from articles where id = %s"
    
    result = cursor.execute(sorgu,(id,))"""
    article = Articles.query.filter_by(id = id).first()
    if article:
        #article = cursor.fetchone()
        goruntulenme = article.goruntulenme
        goruntulenme = goruntulenme + 1
        """sorgu2 = "Update articles Set goruntulenme = %s where id = %s"
        cursor = mysql.connection.cursor()
        cursor.execute(sorgu2,(goruntulenme,id))
        mysql.connection.commit()"""
        article.goruntulenme = goruntulenme
        
        db.session.commit()
        
        return render_template("article.html",article = article)
    else:
        return render_template("article.html")

@app.route("/addarticle",methods = ["GET","POST"])
@login_required
def addarticle():
    form = ArticleForm(request.form)
    if request.method == "POST" and form.validate():
        title = form.title.data
        content = form.content.data
        picture = form.picture.data
        """cursor = mysql.connection.cursor()
        sorgu = "Insert into articles(title,author,picture,content) VALUES(%s,%s,%s,%s)"
        cursor.execute(sorgu,(title,session["user_name"],picture,content))
        mysql.connection.commit()
        cursor.close()"""
        şu_an = datetime.now()
        time1 = datetime.strftime(şu_an,"%D")
        time2 = datetime.strftime(şu_an,"%X")
        time3 = "{}   {}".format(time1,time2)
        article = Articles(title = title,content = content,picture = picture,author = session["user_name"],created_date = time3)
        db.session.add(article)
        db.session.commit()

        flash("Makale Başarıyla Eklendi","success")
        return redirect(url_for("dashboard"))
    return render_template("addarticle.html",form = form)

@app.route("/articles",defaults={"page":1})
@app.route("/articles/page/<int:page>")
def articles(page):
    page_2 = page+1
    sayi = ((page - 1) * 15)
    sayi_2 = ((page_2 - 1) * 15)
    
    
    
    """cursor = mysql.connection.cursor()
    sorgu = "Select * From articles  ORDER BY id DESC limit %s,15;"
    result_2 = cursor.execute(sorgu,(sayi_2,))
    result = cursor.execute(sorgu,(sayi,))"""
    page_1 = page-1
    
    articles = Articles.query.order_by(Articles.id.desc()).all()[sayi:15]
    
    if articles:
        #articles = list(cursor.fetchall())
        result_2 = Articles.query.order_by(Articles.id.desc()).all()[sayi_2:15]
        
        return render_template("articles.html",articles=articles,page=page,page_1=page_1,page_2=page_2,result_2 = result_2)
    
    else:
        flash("Makalelerin sonuna geldiniz","warning")
        return redirect(url_for("articles"))



@app.route("/delete/<string:id>")
@login_required
def delete(id):
    """cursor = mysql.connection.cursor()
    sorgu = "Select * from articles where author = %s and id = %s"
    result = cursor.execute(sorgu,(session["user_name"],id))"""
    article = Articles.query.filter_by(id = id,author = session["user_name"]).first()
    
    if article:
        db.session.delete(article)
        db.session.commit()
        return redirect(url_for("dashboard"))
    else:
        flash("Böyle bir makale yok veya bu işleme yetkiniz yok","danger")
        return redirect(url_for("index"))

@app.route("/edit/<string:id>",methods = ["GET","POST"])
@login_required
def edit(id):
    if request.method == "GET":
        """cursor = mysql.connection.cursor()
        sorgu = "Select * From articles where id = %s and author = %s"
        result = cursor.execute(sorgu,(id,session["user_name"]))"""
        article = Articles.query.filter_by(id = id,author = session["user_name"]).first()
        if article is None:
            flash("Böyle bir makale yok veyabu işleme yetkiniz yok","Danger")
            return redirect(url_for("index"))


        else:
            
            form = ArticleForm()
            form.title.data = article.title
            form.picture.data = article.picture
            form.content.data = article.content
            return render_template("update.html",form = form)
    else:
        #POST REQUEST
        form = ArticleForm(request.form)
        newtitle = form.title.data
        newpicture = form.picture.data
        newcontent = form.content.data
        """sorgu2 = "Update articles Set title = %s,picture =%s,content = %s where id = %s"
        cursor = mysql.connection.cursor()
        cursor.execute(sorgu2,(newtitle,newpicture,newcontent,id)
        mysql.connection.commit()"""
        article = Articles.query.filter_by(id = id).first
        article.title = title
        article.picture = picture
        article.content = content

        flash("Makale başarıyla güncellendi","success")
        return redirect(url_for("dashboard"))



class ArticleForm(Form):
    title = StringField("Makale Başlığı")
    picture = StringField("Başlık resmi url'si")
    content = TextAreaField("Makale İçeriği")


    
"""#Arama
@app.route("/search",methods = ["GET","POST"])
def search():
    if request.method == "GET":
        return redirect(url_for("index"))
    else:
        keyword = request.form.get("keyword")
        cursor = mysql.connection.cursor()
        sorgu = "Select * from articles where title like '%" + keyword +"%'"
        result = cursor.execute(sorgu)
        articles = Articles.query.all()

        if result ==0:
            flash("Aranan kelimeye uygun makale bulunamadı","warning")
            return redirect(url_for("articles"))
        else:
            articles = cursor.fetchall()
            return render_template("articles.html",articles=articles)"""


if __name__=="__main__":
    app.secret_key = 'anahtar'
    app.config['SESSION_TYPE'] = 'filesystem'
    db.create_all()
    app.run(debug=True)








