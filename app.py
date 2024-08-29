from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Necessary for flashing messages
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Ensure the upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Configure MySQL connection with root user
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="carts_db"
)

@app.route('/')
def index():
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, name, cart_icon, number_of_items, max_number_of_items, location FROM carts")
    carts = cursor.fetchall()
    for cart in carts:
        cart['cart_icon'] = cart['cart_icon'].decode('utf-8') if isinstance(cart['cart_icon'], bytes) else cart['cart_icon']
    return render_template('index.html', carts=carts)

@app.route('/cart/<int:cart_id>', methods=['GET', 'POST'])
def cart_detail(cart_id):
    cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        number_of_items = int(request.form['number_of_items'])
        location = request.form['location']
        
        cursor.execute("SELECT max_number_of_items FROM carts WHERE id = %s", (cart_id,))
        max_items = cursor.fetchone()['max_number_of_items']
        
        if number_of_items < 0 or number_of_items > max_items:
            flash('Must be within parameters')
            return redirect(url_for('cart_detail', cart_id=cart_id))
        
        cursor.execute("""
            UPDATE carts SET number_of_items = %s, location = %s, timestamp = CURRENT_TIMESTAMP WHERE id = %s
        """, (number_of_items, location, cart_id))
        conn.commit()
        return redirect(url_for('index'))
    
    cursor.execute("SELECT * FROM carts WHERE id = %s", (cart_id,))
    cart = cursor.fetchone()
    if cart and isinstance(cart['cart_icon'], bytes):
        cart['cart_icon'] = cart['cart_icon'].decode('utf-8')
    return render_template('cart_detail.html', cart=cart)

@app.route('/add_cart', methods=['GET', 'POST'])
def add_cart():
    if request.method == 'POST':
        file = request.files['cart_icon']
        if file:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)

            data = request.form
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO carts (name, cart_icon, number_of_items, max_number_of_items, location, checked_out_by)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (data['name'], file.filename, data['number_of_items'], data['max_number_of_items'], data['location'], data['checked_out_by']))
            conn.commit()
            return redirect(url_for('index'))
    return render_template('add_cart.html')

@app.route('/camera')
def camera():
    return render_template('camera.html')

if __name__ == '__main__':
    app.run(debug=True)
