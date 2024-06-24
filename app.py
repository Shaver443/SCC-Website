import os
import requests
from flask import Flask, render_template, flash, redirect, url_for, request, current_app
from forms import ContactForm
from config import Config
from dotenv import load_dotenv
import logging

app = Flask(__name__)

if os.getenv("FLASK_ENV") != "production":
    load_dotenv()  # Load environment variables from .env file

app.config.from_object(Config)

# Configure logging
logging.basicConfig(level=logging.INFO)

def verify_turnstile(response):
    secret_key = current_app.config['TURNSTILE_SECRET_KEY']
    payload = {'secret': secret_key, 'response': response}
    response = requests.post('https://challenges.cloudflare.com/turnstile/v0/siteverify', data=payload)
    result = response.json()
    logging.info("CAPTCHA verification result: %s", result)
    return result.get('success', False)

def send_email_via_postmark(name, email, phone, message):
    postmark_api_url = "https://api.postmarkapp.com/email"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "X-Postmark-Server-Token": current_app.config['POSTMARK_API_KEY']
    }
    data = {
        "From": current_app.config['POSTMARK_SENDER'],
        "To": current_app.config['POSTMARK_SENDER'],
        "Subject": "New Contact Form Submission",
        "TextBody": f"From: {name} <{email}>\nCell Phone: {phone}\nMessage:\n{message}"
    }
    response = requests.post(postmark_api_url, json=data, headers=headers)
    logging.info("Email send response: %s", response.text)
    return response.status_code == 200

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        logging.info("Form submitted with data: %s", form.data)
        turnstile_response = request.form.get('cf-turnstile-response')
        if verify_turnstile(turnstile_response):
            phone_data = form.phone.data if form.phone.data else "Not provided"
            if send_email_via_postmark(form.name.data, form.email.data, phone_data, form.message.data):
                logging.info("Email sent successfully.")
                return redirect(url_for('thank_you'))
            else:
                logging.error("Failed to send email.")
                return redirect(url_for('error'))
        else:
            logging.warning("CAPTCHA verification failed.")
            flash('CAPTCHA verification failed. Please try again.', 'danger')
    return render_template('contact.html', form=form)

@app.route('/thank-you')
def thank_you():
    return render_template('thank_you.html')

@app.route('/error')
def error():
    return render_template('error.html')

if __name__ == '__main__':
    app.run(debug=True)
