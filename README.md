# Patient Management Database

## Final Project – Database Management Systems

A Flask-based web application for managing patients, doctors, and appointments.
By default, it connects to a local MySQL database.
Google Cloud SQL connection code is included but commented out in connection.py.

## Prerequisites

Before running the project, make sure you have the following installed:

- Python 3.10+

- MySQL Server and MySQL Workbench

- pip (Python package manager)

- Optional: virtualenv for isolated environments

## Setup Instructions
### 1. Start MySQL Server

Launch your MySQL Server instance using MySQL Workbench or the command line.

### 2. Create the Database

Open MySQL Workbench or terminal and run:
```mysql
CREATE DATABASE IF NOT EXISTS patient_mgmt;
```
### 3. Install Dependencies

Open a terminal in the project’s root folder and install dependencies:
```bash
pip install -r requirements.txt
```
It’s recommended to use a virtual environment:
```bash
python -m venv venv
venv\Scripts\activate        # On Windows
source venv/bin/activate     # On macOS/Linux
```
### 4. Seed the Database

Run the database seeding script to populate sample records:
```bash
python seed_database.py
```
### 5. Run the Application

Start the Flask app:
```bash
python app.py
```
Then open your browser and go to:
```text
http://127.0.0.1:5000
```
## Login Credentials

Usernames and passwords for testing are located in:
```text
usernames_passwords.csv
```

(Located in the project’s root directory)