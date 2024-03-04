from flask import Flask, request, redirect, render_template,url_for,jsonify,flash, get_flashed_messages,g,session
import sqlite3
from database import create_database
from auth import check_user_exists, check_username_exists, register_user
import logging
from flask_socketio import SocketIO, emit
from transformers import pipeline, AutoModelForQuestionAnswering, AutoTokenizer
import PyPDF2
import os
import json
from flask import render_template  # Make sure to import render_template

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hsgyenbsuen73jhdnj'  # Set a unique and secret key
socketio = SocketIO(app)

create_database()
# conn = sqlite3.connect('database.db')
# cursor = conn.cursor()

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect('database.db')
    return db.cursor()

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

@app.teardown_appcontext
def teardown_db(e=None):
    close_db(e)


@app.route('/', methods=['GET', 'POST'])
def login_register():
    logging.debug('Entering login_register route')
    flashed_messages = get_flashed_messages()
    for _ in flashed_messages:
        pass
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')
        seat_no = request.form.get('seatNo')  # Retrieve seat number from form data
        print(seat_no)

        if 'register' in request.form:
            # Check if username already exists
            existing_user = check_username_exists(username)
            if existing_user and existing_user[2] == role:
                logging.warning('Registration failed - User with the same username and role already exists')
                flash('Registration failed - A user with the same username and role already exists', 'error')
                return render_template('login_register_page.html', registration_error='A user with the same username and role already exists. Choose a different one.')

            # Check if passwords match
            confirm_password = request.form.get('confirm_password')
            if password != confirm_password:
                logging.warning('Registration failed - Passwords do not match')
                flash('Registration failed - Passwords do not match', 'error')
                return render_template('login_register_page.html', registration_error='Passwords do not match. Please try again.')

            # Register the user
            register_user(username, password, role,seat_no)
            logging.info('Registration successful')
            flash('Registration successful. Please Login.', 'error')
            return redirect(url_for('login_register'))

        elif 'login' in request.form:
            # Check if user exists
            user = check_user_exists(username, password)
            if not user:
                logging.warning('Login failed - User not found in database')
                flash('User not found. Please register first.', 'error')
                return render_template('login_register_page.html', login_error='User not found. Please register first.')

            logging.info('Login successful')
            user_data = get_user_data(username)
            
         
            if user_data:
                # Extract information from the user_data tuple
                user_id, email, password, role, seat_no = user_data

                # Inside the if user_data block
                with open('userdata.txt', 'w') as file:
                    file.write(f"{username},{role},{seat_no}")
                with open('userdata.txt', 'r') as file:
                    data = file.read().split(',')
                    stored_usernamee, stored_rolee, stored_seat_noo = data
                
                # Now you can use these values as needed
                return redirect(url_for(role, username=stored_usernamee,role=stored_rolee, seat_no=stored_seat_noo))
                
            else:
                return redirect(url_for(role))


    logging.debug('Exiting login_register route')
    return render_template('login_register_page.html')
def get_user_data(username):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    # Retrieve user data based on the username
    cur.execute("SELECT * FROM users WHERE username=?", (username,))
    user_data = cur.fetchone()
    print(user_data)
    conn.close()
	

    return user_data

@app.route('/student/<role>', methods=['GET'])
def student(role):
   # Retrieve the values from the query parameters
  
    	# In the route where you want to read the data
    with open('userdata.txt', 'r') as file:
        data = file.read().split(',')
        stored_username, stored_role, stored_seat_no = data

    username = session.get('username')
    seat_no = session.get('seat_no')


    # Return a response to the browser
    return render_template('student_page.html', username=stored_username, role=role, seat_no=stored_seat_no)


@app.route('/resume_1')
def resume_1():
    return render_template("resume_1.html")

@app.route('/resume_2')
def resume_2():
    return render_template("resume_2.html")

@app.route('/resume_template')
def resume_template():
    return render_template("resume_template.html")


@app.route('/alumni/<role>', methods=['GET'])
def alumni(role):
   # Retrieve the values from the query parameters
  
    	# In the route where you want to read the data
    with open('userdata.txt', 'r') as file:
        data = file.read().split(',')
        stored_username, stored_role, stored_seat_no = data

    username = session.get('username')
    seat_no = session.get('seat_no')


    # Return a response to the browser
    return render_template('alumni_connect.html', username=stored_username, role=role, seat_no=stored_seat_no)



@app.route('/admin/<role>', methods=['GET'])
def admin(role):
   # Retrieve the values from the query parameters
  
    	# In the route where you want to read the data
    with open('userdata.txt', 'r') as file:
        data = file.read().split(',')
        stored_username, stored_role, stored_seat_no = data

    username = session.get('username')
    seat_no = session.get('seat_no')


    # Return a response to the browser
    return render_template('admin.html', username=stored_username, role=role, seat_no=stored_seat_no)
	
	
@app.route('/chat_student')
def chat_student():
    return render_template('chat_student.html')

@app.route('/chat_alumni')
def chat_alumni():
    return render_template('chat_alumni.html')
def messageReceived(methods=['GET', 'POST']):
    print('message was received!!!')

@app.route('/faq_alumni')
def faq_alumni():
    return render_template('faq_alumni.html')

import os
import json
from flask import render_template  # Make sure to import render_template

@app.route('/admin_project_tracker')
def admin_project_tracker():
    # Define the path to the Project_data folder
    project_data_path = os.path.join(os.getcwd(), 'Project_data')

    # Initialize an empty list to store project data
    project_data_list = []

    # Iterate through seat number folders
    for seat_folder in os.listdir(project_data_path):
        seat_folder_path = os.path.join(project_data_path, seat_folder)

        # Check if the item in the folder is a directory
        if os.path.isdir(seat_folder_path):
            # Construct the path to the JSON file within the seat folder
            json_file_path = os.path.join(seat_folder_path, 'form_data.json')

            # Check if the JSON file exists
            if os.path.exists(json_file_path):
                # Load JSON data
                with open(json_file_path, 'r') as json_file:
                    project_data = json.load(json_file)
                    project_data_list.append(project_data)

    # Render the template with the loaded project data
    return render_template('admin_project_tracker.html', project_data_list=project_data_list)


@app.route('/store_suggestion', methods=['POST'])
def store_suggestion():
    suggestion = request.form['suggestion']
    seat_no = request.form['seatNo']

    # Adjust the path based on your project structure
    file_path = f'Project_data/{seat_no}/suggestion.txt'

    with open(file_path, 'a') as file:
        file.write(f'{suggestion}\n')

    return jsonify({'status': 'success'})
@app.route('/faq_student')
def faq_student():
    return render_template('faq_student.html')

@app.route('/project_status', methods=['GET', 'POST'])
def project_status():
    if request.method == 'POST':
        # Retrieve form data
        seat_no = request.form.get('seatNo')
        group_id = request.form.get('groupId')
        department = request.form.get('department')
        college_year = request.form.get('collegeYear')
        project_name = request.form.get('projectName')
        project_type = request.form.get('projectType')
        task_name = request.form.get('taskName')
        date = request.form.get('date')
        current_progress = request.form.get('currentProgress')

        # Handle file upload
        upload_task_file = request.files.get('uploadTask')
        if upload_task_file:
            # Create the 'Project_data' directory if it doesn't exist
            project_data_dir = os.path.join('Project_data', seat_no)
            os.makedirs(project_data_dir, exist_ok=True)
            
            # Save the file to the specified directory
            upload_task_file.save(os.path.join(project_data_dir, upload_task_file.filename))

            # Create a dictionary with form data
            form_data = {
                'Seat No': seat_no,
                'Group ID': group_id,
                'Department': department,
                'College Year': college_year,
                'Project Name': project_name,
                'Project Type': project_type,
                'Task Name': task_name,
                'Date': date,
                'Current Progress': current_progress
            }

            # Create a JSON file with form data
            json_file_path = os.path.join(project_data_dir, 'form_data.json')
            with open(json_file_path, 'w') as json_file:
                json.dump(form_data, json_file, indent=4)

        return "Form submitted successfully"

    return render_template('project_status.html')

@socketio.on('my event')
def handle_my_custom_event(json, methods=['GET', 'POST']):
    print('received my event: ' + str(json))
    socketio.emit('my response', json, callback=messageReceived)

def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, "rb") as file:
        pdf_reader = PyPDF2.PdfReader(file)
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text()
    return text

def pdf_to_text(pdf_path):
    text = extract_text_from_pdf(pdf_path)
    return text

def chatbot(pdf_path, user_question):
    model_name = "distilbert-base-cased-distilled-squad"
    model = AutoModelForQuestionAnswering.from_pretrained(model_name)
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    pdf_text = pdf_to_text(pdf_path)
    qa_pipeline = pipeline("question-answering", model=model, tokenizer=tokenizer)
    result = qa_pipeline(question=user_question, context=pdf_text)
    return result["answer"]

@app.route('/chatbot', methods=['POST'])
def handle_chatbot_request():
    user_question = request.form['message']
    greetings = ["hi", "hello", "hey"]
    if user_question.lower() in greetings:
        return "Hello! How may I help you?"
    else:
        pdf_path = "Chatbot files/mmcoe.pdf"  # The path to your PDF file
        answer = chatbot(pdf_path, user_question)
        return answer

if(__name__ == "__main__"):
    socketio.run(app, debug=True, port=8000)
