from flask import Flask, render_template, request, redirect, url_for
from flask_mysqldb import MySQL

app = Flask(__name__)
app.secret_key = 'supersecretkey'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'user@0901'
app.config['MYSQL_DB'] = 'waste_management'
mysql = MySQL(app)

@app.route('/')
def home():
    return render_template('index.html')

# USERS
@app.route('/register_user', methods=['GET', 'POST'])
def register_user():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        phone = request.form['phone']
        role = request.form['role']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (name, email, password, phone, role) VALUES (%s, %s, %s, %s, %s)", (name, email, password, phone, role))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('show_users'))
    return render_template('register_user.html')

@app.route('/users')
def show_users():
    cur = mysql.connection.cursor()
    cur.execute("SELECT user_id, name, email, phone, role FROM users")
    users = cur.fetchall()
    cur.close()
    return render_template('users.html', users=users)

# LOCATIONS
@app.route('/register_location', methods=['GET', 'POST'])
def register_location():
    if request.method == 'POST':
        address = request.form['address']
        area = request.form['area']
        street = request.form['street']
        city = request.form['city']
        pincode = request.form['pincode']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO locations (address, area, street, city, pincode) VALUES (%s, %s, %s, %s, %s)", (address, area, street, city, pincode))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('show_locations'))
    return render_template('register_location.html')

@app.route('/locations')
def show_locations():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM locations")
    locations = cur.fetchall()
    cur.close()
    return render_template('locations.html', locations=locations)

@app.route('/delete_location/<int:location_id>', methods=['POST'])
def delete_location(location_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM locations WHERE location_id = %s", (location_id,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('show_locations'))

# BINS
@app.route('/register_bin', methods=['GET', 'POST'])
def register_bin():
    cur = mysql.connection.cursor()
    cur.execute("SELECT location_id, address FROM locations")
    locations = cur.fetchall()
    if request.method == 'POST':
        bin_type = request.form['bin_type']
        capacity_kg = request.form['capacity_kg']
        current_level_kg = request.form['current_level_kg']
        status = request.form['status']
        location_id = request.form['location_id']
        cur.execute("INSERT INTO bins (bin_type, capacity_kg, current_level_kg, status, location_id) VALUES (%s, %s, %s, %s, %s)", (bin_type, capacity_kg, current_level_kg, status, location_id))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('show_bins'))
    return render_template('register_bin.html', locations=locations)

@app.route('/bins')
def show_bins():
    cur = mysql.connection.cursor()
    cur.execute("SELECT b.bin_id, b.bin_type, b.capacity_kg, b.current_level_kg, b.status, l.address FROM bins b JOIN locations l ON b.location_id = l.location_id")
    bins = cur.fetchall()
    cur.close()
    return render_template('bins.html', bins=bins)

@app.route('/delete_bin/<int:bin_id>', methods=['POST'])
def delete_bin(bin_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM bins WHERE bin_id = %s", (bin_id,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('show_bins'))

# COLLECTORS
@app.route('/register_collector', methods=['GET', 'POST'])
def register_collector():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        email = request.form['email']
        status = request.form['status']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO collectors (name, phone, email, status) VALUES (%s, %s, %s, %s)", (name, phone, email, status))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('show_collectors'))
    return render_template('register_collector.html')

@app.route('/collectors')
def show_collectors():
    cur = mysql.connection.cursor()
    cur.execute("SELECT collector_id, name, phone FROM collectors")
    collectors = cur.fetchall()
    cur.close()
    return render_template('collectors.html', collectors=collectors)

@app.route('/delete_collector/<int:collector_id>', methods=['POST'])
def delete_collector(collector_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM collectors WHERE collector_id = %s", (collector_id,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('show_collectors'))

# COMPLAINTS
@app.route('/register_complaint', methods=['GET', 'POST'])
def register_complaint():
    conn = mysql.connection
    cursor = conn.cursor()
    if request.method == 'POST':
        user_id = request.form['user_id']
        location_id = request.form['location_id']
        issue = request.form['issue']
        date_raised = request.form['date_raised']
        status = request.form['status']
        try:
            cursor.execute("INSERT INTO complaints (user_id, location_id, issue, date_raised, status) VALUES (%s, %s, %s, %s, %s)", (user_id, location_id, issue, date_raised, status))
            conn.commit()
            return redirect(url_for('show_complaints'))
        except Exception as e:
            conn.rollback()
        finally:
            cursor.close()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users")
    users = cursor.fetchall()
    cursor.execute("SELECT location_id FROM locations")
    locations = cursor.fetchall()
    cursor.close()
    return render_template('register_complaint.html', users=users, locations=locations)

@app.route('/complaints')
def show_complaints():
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM complaints")
    complaints = cursor.fetchall()
    cursor.close()
    return render_template('complaints.html', complaints=complaints)

@app.route('/delete_complaint/<int:complaint_id>', methods=['POST'])
def delete_complaint(complaint_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM complaints WHERE complaint_id = %s", (complaint_id,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('show_complaints'))

# WASTE COLLECTION
@app.route('/register_collection', methods=['GET', 'POST'])
def register_collection():
    cursor = mysql.connection.cursor()
    if request.method == 'POST':
        location_id = request.form['location_id']
        collection_date = request.form['collection_date']
        collection_time = request.form['collection_time']
        collector_id = request.form['collector_id']
        cursor.execute("INSERT INTO waste_collection (location_id, date, time, collector_id) VALUES (%s, %s, %s, %s)", (location_id, collection_date, collection_time, collector_id))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('show_waste_collections'))
    cursor.execute("SELECT location_id, area FROM locations")
    locations = cursor.fetchall()
    cursor.execute("SELECT collector_id, name FROM collectors")
    collectors = cursor.fetchall()
    cursor.close()
    return render_template('register_collection.html', locations=locations, collectors=collectors)

@app.route('/waste_collections')
def show_waste_collections():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT wc.collection_id, l.area, wc.date, wc.time, c.name FROM waste_collection wc JOIN locations l ON wc.location_id = l.location_id JOIN collectors c ON wc.collector_id = c.collector_id")
    collections = cursor.fetchall()
    cursor.close()
    return render_template('collections.html', collections=collections)

@app.route('/delete_collection/<int:collection_id>', methods=['POST'])
def delete_collection(collection_id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM waste_collection WHERE collection_id = %s", (collection_id,))
    mysql.connection.commit()
    cursor.close()
    return redirect(url_for('show_waste_collections'))

if __name__ == '__main__':
    app.run(debug=True)
