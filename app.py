from flask import Flask, render_template, request, redirect, url_for,session
import pyodbc
import secrets
import hashlib
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import seaborn as sns
from werkzeug.utils import secure_filename
import plotly.express as px
 

import os

server = 'LAPTOP-SEREJ8QF\MYSQL'
database = 'se'
username = 'sa'
password = 'mysql@123'

conn = pyodbc.connect(f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}')
cursor = conn.cursor()

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/' 
import matplotlib
matplotlib.use('Agg')
 
create_table_query = '''IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'registration')
BEGIN
    CREATE TABLE registration(
        Id_number VARCHAR(50)PRIMARY KEY ,
        Name VARCHAR(50) NOT NULL,
        password VARCHAR(255) NOT NULL,
        email VARCHAR(100) unique,
        phone_number VARCHAR(30) NOT NULL,
        Gender VARCHAR(20) NOT NULL,
        DoB VARCHAR(20) NOT NULL,
        semister  VARCHAR(20) NOT NULL,
        batch  VARCHAR(20) NOT NULL,
        branch  VARCHAR(20) NOT NULL,
        subjects  VARCHAR(20) NOT NULL,
        reset_token VARCHAR(50)
    );
END
'''

cursor.execute(create_table_query)
conn.commit()

@app.route('/')
def home():
        return render_template('home.html')
   

@app.route('/submit', methods=['POST'])
 
def submit():
    error_message = " "
    try:
        name = request.form['name1']
        email = request.form['email']
        password = request.form['password']
        phonenumber = request.form['phoneNumber']
        dob = request.form['dateofbirth']
        gender = request.form.get('gender')
        semister=request.form['Sem']
        batch=request.form['batch']
        branch=request.form['branch']
        Idnumber=request.form['Idnumber'].lower()
        selected_subjects = request.form.getlist('subjects[]')
        reset_token = secrets.token_urlsafe(16)
        select_query = 'SELECT Id_number,email FROM registration WHERE email = ? OR Id_number=?'
        cursor.execute(select_query, (email,Idnumber))
        result = cursor.fetchone()
        if result:
            error_message = "This email or Id is already registered."
            return render_template('registration_form.html', error_message=error_message)
        else:
            insert_query = '''INSERT INTO registration (Id_number, Name, password, email, phone_number, Gender, DoB, semister, batch, branch, reset_token) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''
            cursor.execute(insert_query, (Idnumber, name,password , email, phonenumber, gender, dob, semister, batch, branch, reset_token))

            insert_subject_query = '''INSERT INTO subjects (Id_number, subjects) VALUES (?, ?)'''
            for subject in selected_subjects:
                cursor.execute(insert_subject_query, (Idnumber, subject,))

        # Commit the changes to the database
        conn.commit()
        success = "Successfully Registered"
        return render_template('login.html', success_message=success)
    except pyodbc.IntegrityError as e:
        # Handle the case where a duplicate key violation occurs (e.g., duplicate email)
        conn.rollback()
        return render_template('registration_form.html', error_message=error_message)
#student login
@app.route('/student_login', methods=['POST'])
def student_login():
    email = request.form['useremail']
    password = request.form['userpassword']

    # Use placeholders to prevent SQL injection
    select_query = 'SELECT id_number,email, password,semister, branch  FROM registration WHERE email = ? AND password = ?'
    cursor.execute(select_query, (email, password))
    result = cursor.fetchone()

    if result:
        # User exists with the provided email and password
        id_number,email, password, semister, branch = result
        session['user_email'] = email
        session['semister'] = semister
        session['branch'] = branch
        session['id_number']=id_number

        return render_template('student_dashbard.html')
    else:
        # No matching user found
        # Perform your login failure logic here
        error_message = "Username or Password Invalid."

        return render_template('login.html',login_error_message=error_message)





def send_password_reset_email(email, reset_token):
    email_address = os.environ.get("EMAIL_ADDRESS", "arigalaadarsh6@gmail.com")
    email_password = "etcnyerbognigpwx "
    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    # Email content
    subject = "Password Reset"
    base_url = "http://127.0.0.1:5000"
    reset_url = f"{base_url}/reset_password/{reset_token}"
    body = f"Click the following link to reset your password: {reset_url}"

    # Create the email message
    message = MIMEMultipart()
    message['From'] = email_address
    message['To'] = email
    message['Subject'] = subject
    message.attach(MIMEText(body, 'plain'))

    try:
        # Connect to the SMTP server
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()

        # Log in to the email server
        server.login(email_address, email_password)

        # Send the email
        server.send_message(message)
 
    except smtplib.SMTPAuthenticationError as e:
        print(f"SMTP Authentication Error: {e}")

    finally:
        # Quit the server
        server.quit()



@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']

        # Check if the email exists in the database
        check_email_query = 'SELECT email FROM registration WHERE email = ?'
        cursor.execute(check_email_query, (email,))
        existing_email = cursor.fetchone()

        if existing_email:
            # Generate a reset token
            reset_token = secrets.token_urlsafe(16)

            # Update the reset token in the database
            update_query = 'UPDATE registration SET reset_token = ? WHERE email = ?'
            cursor.execute(update_query, (reset_token, email))
            conn.commit()

            # Implement email sending functionality here with the reset token
            send_password_reset_email(email, reset_token)

            sent_suceessfully= "Password reset email sent. Check your inbox."
            return render_template('forgot_password.html',sent_suceessfully=sent_suceessfully)

        else:
            # Email not found in the database
            notfound= "Email not found. Please check your email address and try again."
            return render_template('forgot_password.html',notfound_email=notfound)


    return render_template('forgot_password.html')


@app.route('/reset_password/<reset_token>', methods=['GET', 'POST'])
def reset_password(reset_token):
    if request.method == 'POST':
        new_password = request.form['new_password']

        # Update the password in the database for the user with the provided reset token
        update_query = 'UPDATE registration SET password = ?,reset_token=NULL WHERE reset_token = ?'
        cursor.execute(update_query, (new_password,reset_token))
        conn.commit()
        return redirect(url_for('reset_successful'))
    
    return render_template('reset_password.html', reset_token=reset_token)

@app.route('/reset_successful')
def reset_successful():

    password_reseted="Successfully reseted password"
    return render_template('login.html', password_reseted= password_reseted)






@app.route('/student', methods=['POST'])
def student():
    selected_option = request.form.get('branch_sec')
    ID_Numbers = request.form.get('ID_Numbers')
    _,_, sec = selected_option.split('_')
    ID_Numbers = list(set(item.lower() for item in ID_Numbers.split(',')))

     # Insert new rows into the database for each absent value
    for value in  ID_Numbers:
        insert_into_student_database(selected_option,sec, value)
    
    return render_template('student_dashboard.html')
 


@app.route('/profile')
def student_profile():
    id_number=session['id_number']
    profile_query='select * from registration where id_number=?'
    cursor.execute(profile_query,id_number)
    results=cursor.fetchone()
    profile_pic='select image from images where id_number=?'
    cursor.execute(profile_pic,id_number)
    profile_result=cursor.fetchone()
    if(profile_result):
        profile_image=profile_result[0]  
    else:
        profile_image='static/uploads/profile.png'
    return render_template('student_profile.html',data=results, profile_image= profile_image)
 
@app.route('/subjects')
def student_subjects():
    id_number=session.get('id_number')
    profile_query='select * from registration where id_number=?'
    cursor.execute(profile_query,id_number)
    student_profile_data=cursor.fetchone()
    subjects_query='select * from subjects where id_number=?'
    cursor.execute(subjects_query,id_number)
    subjects=cursor.fetchall()
    profile_pic='select image from images where id_number=?'
    cursor.execute(profile_pic,id_number)
    profile_result=cursor.fetchone()
    if(profile_result):
        profile_image=profile_result[0]  
    else:
        profile_image='uploads/profile.png'
 
    return render_template('student_profile.html',subjects=subjects,data=student_profile_data, profile_image= profile_image)

#Pie charts for students performance
def generate_pie_chart(present, total, subject):
    labels = ['Present', 'Total']
    absents=1-total
    if present == 0 and total == 0:
        sizes = [0.5, 0.5]  # Equal distribution when both are zero
    else:
        absents = max(0, total - present)
        sizes = [max(0, present), max(0, absents)]
    colors = ['#ff707a', '#03c2c2']
    explode = [0.1, 0.0]

    # Create a Pie chart using Plotly Express
    fig = px.pie(names=labels, values=sizes, color_discrete_sequence=colors, hole=0.2)
    fig.update_traces(textinfo='percent+label', pull=explode, texttemplate=' <span style="color:black;">%{percent:.1%}</span>', hoverinfo='text')
    fig.update_layout(
        width=350,
        height=300,
        showlegend=False,
        title_text=subject,
        title_x=0.5,
        title_y=1,
        title_font=dict(size=18, color='black', family='Arial'),  # Set font properties
        paper_bgcolor='rgba(0,0,0,0)',  # Set the background color to transparent
        plot_bgcolor='rgba(0,0,0,0)'    # Set the plot area color to transparent
    )
    fig.update_traces(
        textfont=dict(color='white', size=20),
        hoverlabel=dict(font=dict(color='white', size=20))
    )
    # Save the chart to a BytesIO stream
    image_stream = BytesIO()
    fig.write_image(image_stream, format='png')
    image_stream.seek(0)

    # Encode the image as base64
    pie_chart = base64.b64encode(image_stream.read()).decode('utf-8')

    return pie_chart



@app.route('/subject_performance')
def subject_performance():
    Idnumber = session['id_number']
    subject_data = []
    pie = list()
    pie_data1=[]
    pie_data2=[]

    select_query = 'SELECT subjects FROM subjects WHERE Id_number=?'
    
    # Use a separate connection and cursor for this query
    with conn.cursor() as cursor:
        cursor.execute(select_query, (Idnumber,))
        result = cursor.fetchall()

        for row in result:
            subject = row.subjects
            sanitized_subject = str(subject).replace(" ", "_").lower()

            absent_query = f"SELECT COUNT(DISTINCT Date) FROM {sanitized_subject} WHERE Id_number = ?"
            total_date_query = f"SELECT COUNT(DISTINCT Date) FROM {sanitized_subject}"

            try:
                # Use the original connection and cursor for the rest of the queries
                cursor.execute(absent_query, (Idnumber,))
                absent_count = cursor.fetchone()[0]

                cursor.execute(total_date_query)
                total_count = cursor.fetchone()[0]

                difference = total_count - absent_count

                subject_data.append({
                    'Subjects': subject,
                    'Total No Of Absent Classes': absent_count,
                    'Total No of Presents': difference,
                    'Total No of Classes ': total_count,

                })

                pie_chart = generate_pie_chart(difference, total_count, subject)
                if len(pie_data1) < 3:
                    pie_data1.append(pie_chart)
                else:
                    pie_data2.append(pie_chart)
            except Exception as e:
                print(f"Error executing query: {e}")

    # Commit changes to the database
    conn.commit()
     # Render the template with the collected data
    return render_template('student_dashbard.html', data1=subject_data, data=pie_data1,data2=pie_data2)


def create_faculty_table():
    create_table_query = '''
        CREATE TABLE faculty_data (
            Id_number VARCHAR(255) PRIMARY KEY,
            password VARCHAR(255),
            email VARCHAR(255) UNIQUE,
            branch VARCHAR(255),
            reset_token VARCHAR(255)
        )
    '''
    cursor.execute(create_table_query)

# Check if the faculty_data table exists
cursor.execute("SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'faculty_data'")
if not cursor.fetchone():
    # If the table doesn't exist, create it
    create_faculty_table()
 
 

def create_table_if_not_exists(table_name):
    check_table_query = f'''
        SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_NAME = '{table_name}';
    '''
    cursor.execute(check_table_query)
    table_exists = cursor.fetchone()[0]

    if not table_exists:
        create_table_query = f'''
            CREATE TABLE {table_name} (
                Id_number varchar(20),
                Date date
            );
        '''
        cursor.execute(create_table_query)
        conn.commit()


def insert_into_database(selected_option, date, absent_value):
    Idnumber_column = 'Id_number'
    date_column = 'Date'
    create_table_if_not_exists(selected_option)

    try:
        check_query = f"SELECT COUNT(*) FROM {selected_option} WHERE ({Idnumber_column} = ? AND {date_column} = ?)"
        cursor.execute(check_query, (absent_value.strip(), date))
        count = cursor.fetchone()[0]

        if count == 0:
            query = f"INSERT INTO {selected_option} ({Idnumber_column}, {date_column}) VALUES (?, ?)"
            cursor.execute(query, (absent_value.strip(), date))
            conn.commit()

    except Exception as e:
        print(f"Error: {e}")
       

 
def insert_into_student_database(selected_option, section, ID_Number):
    # Assuming the table column names are 'Id' and 'section'
 
    check_query = f"SELECT COUNT(*) FROM {selected_option} WHERE (Id = ? AND section = ?)"
    cursor.execute(check_query, (ID_Number.strip(), section))
    count = cursor.fetchone()[0]

    if count == 0:
        query = f"INSERT INTO {selected_option} (Id, section) VALUES (?, ?)"
        cursor.execute(query, (ID_Number.strip(), section))
        conn.commit()
def delete_from_student_database(selected_option, ID_Number, date):
    try:
        # Assuming the table column names are 'Id_number' and 'Date'
        check_query = f"SELECT COUNT(*) FROM {selected_option} WHERE (Id_number = ? AND Date = ?)"
        cursor.execute(check_query, (ID_Number.strip(), date))

        count = cursor.fetchone()[0]

        if count > 0:
            # Assuming the table column names are 'Id_number' and 'Date'
            delete_query = f"DELETE FROM {selected_option} WHERE Id_number = ? AND Date = ?"
            cursor.execute(delete_query, (ID_Number.strip(), date))
            conn.commit()

    except Exception as e:
        print(f"Error: {e}")


@app.route('/faculty', methods=['POST'])
 
def faculty():
    error_message = " "
    try:
        email = request.form['email']
        password = request.form['password']
        semister=request.form['Sem']
        branch=request.form['branch']
        Idnumber=request.form['Idnumber'].lower()
        selected_subjects = request.form.getlist('subjects[]')
        reset_token = secrets.token_urlsafe(16)
        select_query = 'SELECT Id_number,email FROM faculty_data WHERE email = ? OR Id_number=?'
        cursor.execute(select_query, (email,Idnumber))
        result = cursor.fetchone()
        if result:
            error_message = "This email or Id is already registered."
            return render_template('faculty_registration_form.html', error_message=error_message)
        else:
            insert_query = '''INSERT INTO faculty_data (Id_number, password, email,semister,branch, reset_token) VALUES (?, ?, ?, ?, ?, ?)'''
            cursor.execute(insert_query, (Idnumber,password , email, semister, branch, reset_token))

            insert_subject_query = '''INSERT INTO faculty_subjects (Id_number, subjects) VALUES (?, ?)'''
            for subject in selected_subjects:
                cursor.execute(insert_subject_query, (Idnumber, subject,))

        # Commit the changes to the database
        conn.commit()
        success = "Successfully Registered"
        return render_template('faculty_login.html', success_message=success)
    except pyodbc.IntegrityError as e:
        # Handle the case where a duplicate key violation occurs (e.g., duplicate email)
        conn.rollback()
        return render_template('faculty_registration_form.html', error_message=error_message)
 
#faculty login
@app.route('/faculty_login', methods=['POST'])
def faculty_login():
    faculty_id = request.form['faculty_Id']
    password = request.form['faculty_password']
 
    select_query = 'SELECT id_number, password,branch FROM faculty_data WHERE Id_number = ? AND password = ?'
    cursor.execute(select_query, (faculty_id, password))
    result = cursor.fetchone()

    faculty_subjects_query = 'SELECT * FROM faculty_subjects WHERE id_number = ?'
    cursor.execute(faculty_subjects_query, (faculty_id,))
    faculty_subjects = cursor.fetchall()
    if result is not None and faculty_subjects:
        # User exists with the provided faculty_id and password
        _,_,branch=result
        faculty_subjects_list = [{'id_number': row[0], 'subjects': row[1]} for row in faculty_subjects]
        session['dept']=branch
        session['faculty_subjects']=faculty_subjects_list

        return render_template('Attendance_Admin_portal.html',subjects=faculty_subjects_list,dept=branch)
    else:
        error_message = "Username or Password Invalid."
        return render_template('faculty_login.html', login_error_message=error_message)




@app.route('/Faculty_AMS', methods=['GET', 'POST'])
def faculty_ams():
    if request.method == 'POST':
        subjects = request.form.get('subjects')
        date = request.form.get('date')
        absent = request.form.get('absent')
        delete_id = request.form.get('delete_id')

        # Check if subjects is not 'choose'
        if subjects != 'choose':

            # Split the absent values using Python
            absent_values = []
            if absent:
                absent_values = list(set(absent.split(',')))

            # Insert new rows into the database for each absent value
            if absent_values:
                for value in absent_values:
                    insert_into_database(subjects, date, value)

            # Split the delete_id values using Python
            delete_ids = []
            if delete_id:
                delete_ids = list(set(delete_id.split(',')))

            # Delete rows from the database for each delete_id value
            if delete_ids:
                for value in delete_ids:
                    delete_from_student_database(subjects, value, date)
            
        faculty_subjects = session.get('faculty_subjects', [])
        dept = session.get('dept', '')
        return render_template('Attendance_Admin_portal.html',subjects=faculty_subjects,dept=dept)

    return render_template('Attendance_Admin_portal.html')


    
#registrtion form
@app.route('/registration_form')
def registration_form():
    return render_template('registration_form.html')

#login form
@app.route('/login_form')
def login_form():
    return render_template('login.html')

#faculty login form
@app.route('/faculty_login_form')
def faculty_login_form():
    return render_template('faculty_login.html')
#faculty registrtion form
@app.route('/facult_registration_form')
def faculty_registration_form():
    return render_template('faculty_registration_form.html')

#student dashboard
@app.route('/student_dashboard')
def student_dashboard():
    
    return render_template('student_dashbard.html')
@app.route('/logout')
#logout session
def student_logout():
    # Clear the session to log the user out
    session.clear()
    return redirect(url_for('login_form'))

@app.route('/faculty_logout')

#logout session
def faculty_logout():
    # Clear the session to log the user out
    session.clear()
    return redirect(url_for('faculty_login_form'))


#home page
@app.route('/Home')
def Home():
    
    return render_template('home.html')
#About us
@app.route('/About-us')
def About_us():
    
    return render_template('About_us.html')
#Contact us
@app.route('/Contact-us')
def Contact_us():
    
    return render_template('Contact_us.html')

#college Overview
@app.route('/Overview')
def Overview():
    
    return render_template('Admin.html')
 

@app.route('/upload', methods=['POST'])
def upload():

    try:

        uploaded_file = request.files['photo']
        Idnumber = session.get('id_number')
        profile_query='select * from registration where id_number=?'
        cursor.execute(profile_query,Idnumber)
        results=cursor.fetchone()

      

        photo_path = None

        existing_image_query = '''SELECT image FROM images WHERE Id_number = ?'''
        cursor.execute(existing_image_query, (Idnumber,))
        existing_image = cursor.fetchone()

        if existing_image:
            old_image_path = existing_image[0]

            try:
                os.remove(old_image_path)
            except OSError as e:
                print(f"Error deleting file: {e}")

            photo_path = f"static/uploads/{Idnumber}_{secure_filename(uploaded_file.filename)}"
            uploaded_file.save(photo_path)

            update_image_query = 'UPDATE images SET image = ? WHERE Id_number = ?'
            cursor.execute(update_image_query, (photo_path, Idnumber))
        else:
            photo_path = f"static/uploads/{Idnumber}_{secure_filename(uploaded_file.filename)}"           
            uploaded_file.save(photo_path)
            insert_image_query = 'INSERT INTO images (Id_number, image) VALUES (?, ?)'
            cursor.execute(insert_image_query, (Idnumber, photo_path))
        

        conn.commit()

        

        return render_template('student_profile.html',data=results, profile_image=photo_path)

    except Exception as e:
        print(f"Error in upload route: {e}")
        return render_template('faculty_login.html')


if __name__ == '__main__':
    try:
        app.run(debug=False)
    finally:
        try:
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Error while closing cursor and connection: {e}")
