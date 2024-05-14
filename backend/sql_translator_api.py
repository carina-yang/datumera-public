import os
import json
from cryptography.fernet import Fernet
from flask import Flask, request, redirect, jsonify, send_file
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import zipfile
import re
import logging
from sql_translator import split_sql_files_to_translate
import firebase_admin 
from firebase_admin import credentials, auth, firestore
import stripe
from flask import Flask
from flask_cors import CORS
import shutil

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}}, expose_headers=["Content-Disposition"])

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()
users_ref = db.collection('users')

log_dir = os.environ.get('APP_LOG_DIR', '/Users/carinayang/oai_translator/translator_root/logs')
logging.basicConfig(filename=f"{log_dir}/app_log.log", level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

stripe.api_key = '***Removed***'
endpoint_secret = '***Removed***'

YOUR_DOMAIN = 'http://localhost:3000'

@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    print('create checkout session')
    id_token = request.headers.get('Authorization').split('Bearer ')[1]
    try:

        decoded_token = auth.verify_id_token(id_token)
        user_uid = decoded_token['uid']

        print(f'User UID: {user_uid}')
        data = request.get_json()  # Get data as JSON
        print(data)
        prices = stripe.Price.list(
            lookup_keys=[data['lookup_key']],  # Access the lookup_key from JSON
            expand=['data.product']
        )

        print(prices)

        checkout_session = stripe.checkout.Session.create(
            line_items=[{'price': prices.data[0].id, 'quantity': 1}],
            mode='subscription',
            success_url='http://localhost:3000/settings',
            cancel_url='http://localhost:3000/settings',
            metadata={'UID': user_uid},
        )
        return jsonify({'url': checkout_session.url})  # Return JSON response
    except auth.InvalidIdTokenError:
        return jsonify({'error': 'Invalid ID token'}), 401
    except Exception as e:
        print(e)
        return jsonify({'error': 'Server error'}), 500
    

@app.route('/webhook', methods=['POST'])
def webhook():
    print("webhook")
    event = None
    payload = request.data
    sig_header = request.headers['STRIPE_SIGNATURE']

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        raise e
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        raise e

    # Handle the event
    if event['type'] == 'checkout.session.completed':
        print("checkout.session.completed")
        session = event['data']['object']
        user_uid = session.get('metadata', {}).get('UID')
        print(user_uid)
    
        if user_uid:
            try:
                print("change supscription")
                subscription = stripe.Subscription.retrieve(session["subscription"])
                current_period_end = datetime.fromtimestamp(
                    subscription.current_period_end
                )
                user_doc = users_ref.document(user_uid)
                new_credits = user_doc.get().to_dict().get("credits", 0) + 100000
                print({
                    'stripeCustomerId': subscription.customer,
                    'stripeSubscriptionId': subscription.id,
                    'stripePriceId': subscription['items']['data'][0]['price']['id'] if subscription['items']['data'] else None,
                    'credits': new_credits,
                    'stripeCurrentPeriodEnd': current_period_end,  
                })
                user_doc.update({
                    'stripeCustomerId': subscription.customer,
                    'stripeSubscriptionId': subscription.id,
                    'stripePriceId': subscription['items']['data'][0]['price']['id'] if subscription['items']['data'] else None,
                    'credits': new_credits,
                    'stripeCurrentPeriodEnd': current_period_end,  
                })
            except Exception as e:
                print("ERROR HERE")
                print(e)

    if event["type"] == "invoice.payment_succeeded":
        print("invoice.payment_succeeded here")
        session = event['data']['object']
        print(session)
        subscription = stripe.Subscription.retrieve(session["subscription"])
        print(subscription)
        document = next(users_ref.where('stripeSubscriptionId', '==', subscription.id).limit(1).stream(), None)

        print("invoice.payment_succeeded here2")

        if document:
            print("document")
            try:
                # Found the document, now get its current credits value and add 100000
                user_doc = document.to_dict()
                new_credits = user_doc.get("credits", 0) + 100000
                current_period_end = datetime.fromtimestamp(
                    subscription.current_period_end
                )
                
                # Update the document with the new credits value
                document.reference.update({
                    'credits': new_credits,
                    'stripePriceId': subscription['items']['data'][0]['price']['id'] if subscription['items']['data'] else None,
                    'stripeCurrentPeriodEnd': current_period_end,  
                })

            except Exception as e:
                print("ERROR HERE")
                print(e)

    # ... handle other event types
    else:
      print('Unhandled event type {}'.format(event['type']))

    return jsonify(success=True)

@app.route('/translate_sql', methods=['POST'])
def translate_sql():
    id_token = request.headers.get('Authorization').split('Bearer ')[1]
    try:
        decoded_token = auth.verify_id_token(id_token)
    except Exception as e:
        print(e)
        return jsonify({'error': 'Server error'}), 500
    
    file = request.files['sql_package_file']
    src_lan = request.form['src_lan']
    tgt_lan = request.form['tgt_lan']
    sql_identifier_pattern = request.form['sql_identifier_pattern']
    sql_match_pattern = request.form['sql_match_pattern']
    errors = []
    if not file:
        errors.append("Missing file package.")
    if not src_lan or not tgt_lan:
        errors.append("Source or target language not specified.")
    if not sql_identifier_pattern or not sql_match_pattern:
        errors.append("SQL identifier or SQL matching pattern not specified.")
    if errors:
        return jsonify({'message': f'Invalid request: {errors}'}), 400

    # Save and unzip the file
    cur_timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    temp_dir = os.environ.get("TRANSLATOR_FILE_TEMP_DIR", "~/temp")
    temp_dir = os.path.expanduser(temp_dir)
    received_dir = os.path.join(temp_dir, "received")
    os.makedirs(received_dir, exist_ok=True)
    zip_path = os.path.join(received_dir, f"{cur_timestamp}.zip")
    file.save(zip_path)

    target_dir = os.path.join(temp_dir, cur_timestamp)
    os.makedirs(target_dir, exist_ok=True)

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(target_dir)

    # Call the translation function
    split_sql_files_to_translate(target_dir, src_lan, tgt_lan, sql_identifier_pattern, sql_match_pattern)
    
    # Zip the result folder
    result_dir = os.path.join(temp_dir, f"{cur_timestamp}_result")

    os.makedirs(f"{cur_timestamp}_result", exist_ok=True)
    result_zip = os.path.join(temp_dir, f"{cur_timestamp}_result.zip")

    # Return the zip file
    return send_file(shutil.make_archive(result_zip, 'zip', result_dir), as_attachment=True, download_name=f"{cur_timestamp}_result.zip")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
