from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
      # flask oluşturuldu hocam
app = Flask("__saglik_platformu_proje__")
app.config['SECRET_KEY'] = 'Veli_Sezo_007'
     # test için yaptım hocam 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///saglik_platformu.db'
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = True 
     # burada her veri değisikliğinde deneme aşamasında uyarı almak için track'i açtım hocam
db = SQLAlchemy(app)
     # veritabanını başlatıyorum hocam ve giriş yöneticisini başlatıyorum.
login_manager = LoginManager(app)
login_manager.login_view = 'giris'
@login_manager.user_loader
def load_user(user_id):
    return None
     # rotalar yani web sayfalarını oluşturuyorum hocam
@app.route('/')  # URL'ye yanıt vermesi için kullandım. 
def ana_sayfa():
    return render_template('ana_sayfa.html')
@app.route('/giris', methods=['GET', 'POST'])   # burada GET ve POST methodları sayesinde
                                           #hem sayfayı gösteriyorum hemde kullanıcıdan veri istiyorum
def giris():
        return render_template('giris.html')
@app.route('/kayit', methods=['GET', 'POST'])
def kayit():
        return render_template('kayit.html')
     #şimdi uuygulamayı ilk kez çalıştıracağım hocam.
if __name__ == '__main__' :
    app.run(debug=True, host='localhost', port=5000)