from flask import Flask, render_template, request, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import random
# flask oluşturuldu hocam
app = Flask("__saglik_platformu_proje__")
app.config['SECRET_KEY'] = 'Veli_Sezo_007'
     # test için yaptım hocam 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///saglik_platformu.db'
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = True 
     # burada her veri değisikliğinde deneme aşamasında uyarı almak için track'i açtım hocam
db = SQLAlchemy(app) # vveritabanını fiziksel olarak oluşturuyorum hocam.
migrate = Migrate(app, db) # veritabanı ile uygulama arasında köprü kuruyorum hocam.
class Kullanici(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
     #E-posta ve doğrulama alanları ekledim hocam.
    email = db.Column(db.String(120), unique=True, nullable=False)
    rol = db.Column(db.String(20), nullable=False, default='hasta')
    dogrulama_kodu = db.Column(db.String(6), nullable=True)
    is_verifield = db.Column(db.Boolean, default=False) 
   # hasta veya uzman mı olduğunu öğrenmek için rol alanı ekledim hocam.
class Gönderi(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    baslik = db.Column(db.String(150), nullable=False)
    icerik = db.Column(db.Text, nullable=False)
    kullanici_id = db.Column(db.Integer, db.ForeignKey('kullanici.id'), nullable=False)
    sahip = db.relationship('Kullanici', backref=db.backref('gönderiler', lazy=True))
     # veritabanını başlatıyorum hocam ve giriş yöneticisini başlatıyorum.
     # yorum sınıfını ekliyorun
class Yorum(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    icerik = db.Column(db.Text, nullable=False)
    gonderi_id = db.Column(db.Integer, db.ForeignKey('gönderi.id'), nullable=False)
    kullanici_id = db.Column(db.Integer, db.ForeignKey('kullanici.id'), nullable=False)
      # kullanıcı ve gönderi ile ilişkilendirmek için foreign key ekledim hocam.
    sahip = db.relationship('Kullanici', backref=db.backref('yorumlar', lazy=True))
      # yorumlar ile gönderiler arasında ilişki kurmak için backref ekledim hocam.
    gonderi = db.relationship('Gönderi', backref=db.backref('yorumlar', lazy=True))
class EpostaLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    alici_email = db.Column(db.String(120), nullable=False)
    kod = db.Column(db.String(6), nullable=False)
    gonderme_tarihi = db.Column(db.DateTime, default=datetime.utcnow)
    durum = db.Column(db.String(50), default="Gönderildi") # başarılı veya başarısız fark etmiyor hocam.
login_manager = LoginManager(app)
login_manager.login_view = 'giris'
@login_manager.user_loader
def load_user(user_id):
    return Kullanici.query.get(int(user_id))
     # rotalar yani web sayfalarını oluşturuyorum hocam.
def eposta_gonder(alici_eposta, kod):
    #gonderici mail bilgileri ekliyorum
    sender_email = "ornek@gmail.com"
    sender_password = "sifreniz"  # Buraya gerçek şifreyi koymayın, güvenlik açısından risklidir.
    # e-posta içeriğini oluşturuyorum
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = alici_eposta
    msg['Subject'] = "Doğrulama Kodu"
    body = f"Doğrulama kodu: {kod}"
    msg.attach(MIMEText(body, 'plain', 'UTF-8'))
    yeni_log = EpostaLog(alici_email=alici_eposta, kod=kod)
    # e-posta gönderiyorum
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.close()
        yeni_log.durum = "BAŞARILI "
        print ("E-posta gönderildi.")
    except Exception as e:
            yeni_log_durum = f"Başarısız: {str(e)[:40]}" #hata özeti için.
            print(f"Hata oluştu: {e}")
    finally: 
        #e posta gitse de gitmese de logu kaydet
        db.session.add(yeni_log)
        db.session.commit()
@app.route('/')  # URL'ye yanıt vermesi için kullandım. 
def ana_sayfa():
    gonderiler = Gönderi.query.all()
    return render_template('ana_sayfa.html', gonderiler=gonderiler)
@app.route('/yeni_gonderi', methods=['GET', 'POST'])
@login_required
def yeni_gonderi():
    if request.method == 'POST':
        baslik = request.form.get('baslik')
        icerik = request.form.get('icerik')
        if baslik and icerik:
           yeni_gonderi = Gönderi(baslik=baslik, icerik=icerik, kullanici_id=current_user.id)
           db.session.add(yeni_gonderi)
           db.session.commit()
           return redirect(url_for('ana_sayfa')) 
       # yeni gönderi oluşturulduktan sonra ana sayfaya yönlendiriyorum hocam.
    return render_template('yeni_gonderi.html')
@app.route('/giris', methods=['GET', 'POST'])   # burada GET ve POST methodları sayesinde
                                           #hem sayfayı gösteriyorum hemde kullanıcıdan veri istiyorum
def giris():
    if request.method == 'POST':
        gelen_isim = request.form.get('username')
        gelen_sifre = request.form.get('password')
        kullanici = Kullanici.query.filter_by(username=gelen_isim).first()
        #kullanıcıyı veritabanında arıyorum hocam.
        if kullanici and check_password_hash(kullanici.password, gelen_sifre):
            login_user(kullanici)
            return redirect(url_for('ana_sayfa'))
    return render_template('giris.html')
@app.route('/kayit', methods=['GET', 'POST'])
def kayit():
    if request.method == 'POST':
        gelen_isim = request.form.get('username')
        gelen_email = request.form.get('email')
        gelen_sifre = request.form.get('password')
        rol = request.form.get('rol')

        # Rol kontrolü
        if rol == 'ogrenci' and not gelen_email.endswith('.edu.tr'):
            return render_template("kayit.html", hata="Öğrenci e-posta adresi geçerli değil.")

        # 1. Kullanıcı adı kontrolü
        if Kullanici.query.filter_by(username=gelen_isim).first():
            return render_template("kayit.html", hata="Bu kullanıcı adı zaten alınmış!")

        # 2. E-posta kontrolü
        if Kullanici.query.filter_by(email=gelen_email).first():
            return render_template("kayit.html", hata="Bu e-posta adresi zaten kayıtlı!")

        # 3. Kod Üretimi ve Şifreleme
        kod = str(random.randint(100000, 999999))
        hashed_password = generate_password_hash(gelen_sifre, method='scrypt')

        yeni_kullanici = Kullanici(
            username=gelen_isim,
            email=gelen_email,
            password=hashed_password,
            rol=rol,
            dogrulama_kodu=kod,
            is_verifield=False
        )

        db.session.add(yeni_kullanici)
        db.session.commit()

        # E-posta Gönderme
        eposta_gonder(gelen_email, kod)

        return redirect(url_for('dogrulama', kullanici_id=yeni_kullanici.id))

    return render_template('kayit.html')

@app.route('/dogrulama/<int:kullanici_id>', methods=['GET', 'POST'])
def dogrulama(kullanici_id):
    kullanici = Kullanici.query.get_or_404(kullanici_id)

    if request.method == 'POST':
        girilen_kod = request.form.get('kod')

        if girilen_kod == kullanici.dogrulama_kodu:
            kullanici.is_verifield = True
            kullanici.dogrulama_kodu = None
            db.session.commit()
            print("Hesap doğrulandı.")
            return redirect(url_for('giris'))
        else:
            return render_template('dogrulama.html', kullanici_id=kullanici_id, hata="Doğrulama kodu yanlış.")

    return render_template('dogrulama.html', kullanici_id=kullanici_id)
@app.route('/cikis')
def cikis():
    logout_user() #oturum bitirdiğimizde sistemden silmesini sağlar. 
@app.route('/profil')
@login_required
def profil():
    return render_template('profil.html')
with app.app_context():
    db.create_all() # veritabanını oluşturuyorum hocam.
if __name__ == '__main__' :
    app.run(debug=True, host='localhost', port=5000)