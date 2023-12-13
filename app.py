from flask import Flask, request, jsonify, render_template
import os
from werkzeug.utils import secure_filename
import base64
from PIL import Image
from io import BytesIO
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage

app = Flask(__name__)

# Folder for storing uploaded images
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def encrypt_and_embed_text(image_path, text):
    # Encode the text into bytes
    text_bytes = text.encode('utf-8')

    # Open the image
    with open(image_path, 'rb') as image_file:
        # Read the image data
        image_data = image_file.read()

    # Combine the image data and text bytes
    combined_data = image_data + text_bytes

    # Create a new image with the combined data
    encrypted_image = Image.open(BytesIO(combined_data))

    # Save the new image
    encrypted_image_path = os.path.join(UPLOAD_FOLDER, 'encrypted_image.png')
    encrypted_image.save(encrypted_image_path)

    return encrypted_image_path

@app.route('/')
def index():
    return render_template('upload_form.html')

@app.route('/upload', methods=['POST'])
def upload_image():
    # Check if the POST request has a file part
    if 'image' not in request.files or 'text' not in request.form:
        return jsonify({'error': 'Image or text not provided'})

    image = request.files['image']
    text = request.form['text']

    # If the user does not select a file, the browser may submit an empty file without a filename
    if image.filename == '':
        return jsonify({'error': 'No selected image'})

    # Save the image to the uploads folder using secure_filename
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(image.filename))
    image.save(image_path)

    # Encrypt and embed text in the image
    encrypted_image_path = encrypt_and_embed_text(image_path, text)

    # Send the encrypted image via email
    send_email(encrypted_image_path)

    return jsonify({'message': 'Image uploaded, text encrypted, and email sent successfully'})

def send_email(image_path):
    # Email configuration (replace with your SMTP server details)
    smtp_server = 'your_smtp_server.com'
    smtp_port = 587
    smtp_username = 'your_email@example.com'
    smtp_password = 'your_email_password'
    sender_email = 'your_email@example.com'
    receiver_email = 'recipient_email@example.com'

    # Create the email message
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = receiver_email
    message['Subject'] = 'Encrypted Image with Hidden Text'

    # Attach the encrypted image to the email
    with open(image_path, 'rb') as image_file:
        image_data = image_file.read()
        image_attachment = MIMEImage(image_data)
        message.attach(image_attachment)

    # Connect to the SMTP server and send the email
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.sendmail(sender_email, receiver_email, message.as_string())

if __name__ == '__main__':
    app.run(debug=False)
