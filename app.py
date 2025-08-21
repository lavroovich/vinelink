from flask import Flask, render_template, send_from_directory
from flask_sqlalchemy import SQLAlchemy
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///vines.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

database = SQLAlchemy(app)

# ----- Модель -----
class Vine(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    name = database.Column(database.String(100), nullable=False)
    color = database.Column(database.String(50), nullable=False)
    country = database.Column(database.String(100), nullable=False)
    region = database.Column(database.String(100), nullable=True)
    grape = database.Column(database.String(200), nullable=True)  # JSON-строка
    sugar = database.Column(database.String(50), nullable=False)
    pdf_file = database.Column(database.String(200), nullable=False)

# ----- Роут каталога -----
@app.route("/")
def catalog():
    vines = Vine.query.all()
    
    vines_list = []
    for v in vines:
        try:
            grapes = json.loads(v.grape) if v.grape else []
        except:
            grapes = [v.grape] if v.grape else []

        vines_list.append({
            "id": v.id,
            "name": v.name,
            "color": v.color,
            "country": v.country,
            "region": v.region,
            "grape": grapes,   # список сортов!
            "sugar": v.sugar,
            "pdf_file": v.pdf_file
        })
    
    return render_template("catalog.html", vines=vines_list)

# ----- Раздача PDF -----
@app.route("/vinery/<filename>")
def pdfs(filename):
    return send_from_directory("pdfs", filename)

# ----- Тестовый роут для загрузки -----
@app.route("/dev-only/upload-test-vines")
def upload_test_vines():
    # 1 сорт
    wine1 = Vine(
        name="[ТЕСТОВОЕ] Каберне Совиньон",
        color="red",
        country="russia",
        region="Краснодар",
        grape=json.dumps(["Cabernet Sauvignon"]),  # сериализация
        sugar="dry",
        pdf_file="kab_sov.pdf"
    )

    # несколько сортов
    wine2 = Vine(
        name="[ТЕСТОВОЕ] Бордо купаж",
        color="red",
        country="france",
        region="Бордо",
        grape=json.dumps(["Cabernet Sauvignon", "Merlot", "Cabernet Franc"]),
        sugar="dry",
        pdf_file="bordeaux.pdf"
    )

    database.session.add(wine1)
    database.session.add(wine2)
    database.session.commit()
    return "Test vines uploaded successfully!"

import qrcode
from io import BytesIO
from flask import Flask, send_file, url_for

# ... твой предыдущий код выше ...

# ----- QR-код роут -----
@app.route("/vinery/qr/<filename>")
def pdf_qr(filename):
    # формируем полный URL к PDF
    pdf_url = f"https://aviator.lavroovich.fun/vinery/{filename}"
    
    # генерим QR
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(pdf_url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    # отдаем как PNG прямо в браузер
    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return send_file(buf, mimetype="image/png")

# ----- Инициализация -----
with app.app_context():
    database.create_all()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=4400)