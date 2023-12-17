from flask import Flask, request, jsonify, render_template
import os
from werkzeug.utils import secure_filename
from PIL import Image
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from dotenv import load_dotenv

# Załaduj konfigurację z pliku .env
load_dotenv()

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def embed_text_in_image(image_path, text, output_path):
    image = Image.open(image_path)
    image = image.convert("RGBA")

    text += "\0"  # Dodanie znaku końca tekstu
    binary_text = ''.join(format(ord(char), '08b') for char in text)

    width, height = image.size
    pixels = image.load()

    text_index = 0
    for y in range(height):
        for x in range(width):
            pixel = list(pixels[x, y])

            for n in range(3):  # Przejdź przez R, G, B
                if text_index < len(binary_text):
                    pixel[n] = pixel[n] & ~1 | int(binary_text[text_index])
                    text_index += 1

            pixels[x, y] = tuple(pixel)

            if text_index >= len(binary_text):
                image.save(output_path, format='PNG')
                return

    image.save(output_path, format='PNG')

@app.route('/')
def index():
    return render_template('upload_form.html')

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({'error': 'Image not provided'})

    image = request.files['image']
    text = request.form.get('text', '')

    text_file = request.files.get('text_file')
    if text_file:
        text = text_file.read().decode('utf-8')

    if image.filename == '':
        return jsonify({'error': 'No selected image'})

    image_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(image.filename))
    image.save(image_path)

    output_path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
    embed_text_in_image(image_path, text, output_path)

    send_email(output_path)

    return jsonify({'message': 'Image uploaded, text embedded, and email sent successfully'})

def send_email(image_path):
    smtp_server = os.getenv('SMTP_SERVER')
    smtp_port = os.getenv('SMTP_PORT', 587)
    smtp_username = os.getenv('SMTP_USERNAME')
    smtp_password = os.getenv('SMTP_PASSWORD')
    sender_email = os.getenv('SENDER_EMAIL')
    receiver_email = os.getenv('RECEIVER_EMAIL')

    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = receiver_email
    message['Subject'] = 'Image with Embedded Text'

    with open(image_path, 'rb') as image_file:
        image_attachment = MIMEImage(image_file.read(), _subtype="png")
        message.attach(image_attachment)

    with smtplib.SMTP(smtp_server, int(smtp_port)) as server:
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.sendmail(sender_email, receiver_email, message.as_string())

if __name__ == '__main__':
    app.run(debug=False)
