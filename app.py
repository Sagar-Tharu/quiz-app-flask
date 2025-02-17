from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Database Models
class User(UserMixin, db.Model):
    __tablename__ = "user"  # Explicitly setting table name
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    scores = db.relationship('Score', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Quiz Questions (300 Questions)

quiz_questions = {
    # General Knowledge (50 Questions)
    1: {'question': 'What is the capital of France?', 'options': ['Paris', 'London', 'Berlin', 'Madrid'], 'correct': 'Paris'},
    2: {'question': 'Who wrote "Romeo and Juliet"?', 'options': ['William Shakespeare', 'Charles Dickens', 'Mark Twain', 'Jane Austen'], 'correct': 'William Shakespeare'},
    3: {'question': 'Which planet is known as the Red Planet?', 'options': ['Earth', 'Mars', 'Jupiter', 'Saturn'], 'correct': 'Mars'},
    4: {'question': 'What is the largest ocean on Earth?', 'options': ['Atlantic Ocean', 'Indian Ocean', 'Arctic Ocean', 'Pacific Ocean'], 'correct': 'Pacific Ocean'},
    5: {'question': 'Who painted the Mona Lisa?', 'options': ['Vincent van Gogh', 'Pablo Picasso', 'Leonardo da Vinci', 'Claude Monet'], 'correct': 'Leonardo da Vinci'},
    6: {'question': 'What is the currency of Japan?', 'options': ['Yen', 'Dollar', 'Euro', 'Pound'], 'correct': 'Yen'},
    7: {'question': 'Which country is known as the Land of the Rising Sun?', 'options': ['China', 'Japan', 'South Korea', 'Thailand'], 'correct': 'Japan'},
    8: {'question': 'Who invented the telephone?', 'options': ['Thomas Edison', 'Alexander Graham Bell', 'Nikola Tesla', 'Albert Einstein'], 'correct': 'Alexander Graham Bell'},
    9: {'question': 'What is the smallest prime number?', 'options': ['1', '2', '3', '5'], 'correct': '2'},
    10: {'question': 'Which gas is most abundant in the Earth\'s atmosphere?', 'options': ['Oxygen', 'Nitrogen', 'Carbon Dioxide', 'Argon'], 'correct': 'Nitrogen'},
    11: {'question': 'What is the chemical symbol for water?', 'options': ['H2O', 'CO2', 'NaCl', 'O2'], 'correct': 'H2O'},
    12: {'question': 'Who is known as the Father of Computers?', 'options': ['Charles Babbage', 'Alan Turing', 'Bill Gates', 'Steve Jobs'], 'correct': 'Charles Babbage'},
    13: {'question': 'What is the largest mammal in the world?', 'options': ['Elephant', 'Blue Whale', 'Giraffe', 'Shark'], 'correct': 'Blue Whale'},
    14: {'question': 'Which country is famous for the Great Wall?', 'options': ['India', 'China', 'Japan', 'Russia'], 'correct': 'China'},
    15: {'question': 'What is the longest river in the world?', 'options': ['Nile', 'Amazon', 'Yangtze', 'Mississippi'], 'correct': 'Nile'},
    16: {'question': 'Which is the largest desert in the world?', 'options': ['Sahara', 'Arabian', 'Gobi', 'Antarctic'], 'correct': 'Antarctic'},
    17: {'question': 'Who discovered gravity?', 'options': ['Isaac Newton', 'Albert Einstein', 'Galileo Galilei', 'Stephen Hawking'], 'correct': 'Isaac Newton'},
    18: {'question': 'What is the capital of Australia?', 'options': ['Sydney', 'Melbourne', 'Canberra', 'Perth'], 'correct': 'Canberra'},
    19: {'question': 'Which is the smallest continent?', 'options': ['Asia', 'Africa', 'Australia', 'Europe'], 'correct': 'Australia'},
    20: {'question': 'What is the chemical symbol for gold?', 'options': ['Au', 'Ag', 'Fe', 'Cu'], 'correct': 'Au'},
    21: {'question': 'Which planet is closest to the Sun?', 'options': ['Earth', 'Venus', 'Mercury', 'Mars'], 'correct': 'Mercury'},
    22: {'question': 'Who wrote "The Theory of Relativity"?', 'options': ['Isaac Newton', 'Albert Einstein', 'Stephen Hawking', 'Galileo Galilei'], 'correct': 'Albert Einstein'},
    23: {'question': 'What is the largest organ in the human body?', 'options': ['Heart', 'Liver', 'Skin', 'Brain'], 'correct': 'Skin'},
    24: {'question': 'Which country is known as the Land of the Midnight Sun?', 'options': ['Norway', 'Sweden', 'Finland', 'Iceland'], 'correct': 'Norway'},
    25: {'question': 'What is the chemical symbol for oxygen?', 'options': ['O2', 'CO2', 'H2O', 'N2'], 'correct': 'O2'},
    26: {'question': 'Which country is known as the Land of the Thunder Dragon?', 'options': ['Bhutan', 'Nepal', 'Tibet', 'Myanmar'], 'correct': 'Bhutan'},
    27: {'question': 'What is the capital of Canada?', 'options': ['Toronto', 'Ottawa', 'Vancouver', 'Montreal'], 'correct': 'Ottawa'},
    28: {'question': 'Which country is known as the Land of the Rising Sun?', 'options': ['China', 'Japan', 'South Korea', 'Thailand'], 'correct': 'Japan'},
    29: {'question': 'What is the capital of Brazil?', 'options': ['Rio de Janeiro', 'São Paulo', 'Brasília', 'Salvador'], 'correct': 'Brasília'},
    30: {'question': 'Which country is known as the Land of the Long White Cloud?', 'options': ['Australia', 'New Zealand', 'Fiji', 'Samoa'], 'correct': 'New Zealand'},
    31: {'question': 'What is the capital of South Africa?', 'options': ['Cape Town', 'Pretoria', 'Johannesburg', 'Durban'], 'correct': 'Pretoria'},
    32: {'question': 'Which country is known as the Land of the Midnight Sun?', 'options': ['Norway', 'Sweden', 'Finland', 'Iceland'], 'correct': 'Norway'},
    33: {'question': 'What is the capital of Russia?', 'options': ['St. Petersburg', 'Moscow', 'Novosibirsk', 'Yekaterinburg'], 'correct': 'Moscow'},
    34: {'question': 'Which country is known as the Land of the Rising Sun?', 'options': ['China', 'Japan', 'South Korea', 'Thailand'], 'correct': 'Japan'},
    35: {'question': 'What is the capital of Argentina?', 'options': ['Buenos Aires', 'Córdoba', 'Rosario', 'Mendoza'], 'correct': 'Buenos Aires'},
    36: {'question': 'Which country is known as the Land of the Thunder Dragon?', 'options': ['Bhutan', 'Nepal', 'Tibet', 'Myanmar'], 'correct': 'Bhutan'},
    37: {'question': 'What is the capital of Egypt?', 'options': ['Cairo', 'Alexandria', 'Giza', 'Luxor'], 'correct': 'Cairo'},
    38: {'question': 'Which country is known as the Land of the Rising Sun?', 'options': ['China', 'Japan', 'South Korea', 'Thailand'], 'correct': 'Japan'},
    39: {'question': 'What is the capital of Germany?', 'options': ['Berlin', 'Munich', 'Hamburg', 'Frankfurt'], 'correct': 'Berlin'},
    40: {'question': 'Which country is known as the Land of the Midnight Sun?', 'options': ['Norway', 'Sweden', 'Finland', 'Iceland'], 'correct': 'Norway'},
    41: {'question': 'What is the capital of Italy?', 'options': ['Rome', 'Milan', 'Venice', 'Florence'], 'correct': 'Rome'},
    42: {'question': 'Which country is known as the Land of the Rising Sun?', 'options': ['China', 'Japan', 'South Korea', 'Thailand'], 'correct': 'Japan'},
    43: {'question': 'What is the capital of Spain?', 'options': ['Madrid', 'Barcelona', 'Valencia', 'Seville'], 'correct': 'Madrid'},
    44: {'question': 'Which country is known as the Land of the Thunder Dragon?', 'options': ['Bhutan', 'Nepal', 'Tibet', 'Myanmar'], 'correct': 'Bhutan'},
    45: {'question': 'What is the capital of the United Kingdom?', 'options': ['London', 'Manchester', 'Liverpool', 'Birmingham'], 'correct': 'London'},
    46: {'question': 'Which country is known as the Land of the Rising Sun?', 'options': ['China', 'Japan', 'South Korea', 'Thailand'], 'correct': 'Japan'},
    47: {'question': 'What is the capital of the United States?', 'options': ['New York', 'Washington, D.C.', 'Los Angeles', 'Chicago'], 'correct': 'Washington, D.C.'},
    48: {'question': 'Which country is known as the Land of the Midnight Sun?', 'options': ['Norway', 'Sweden', 'Finland', 'Iceland'], 'correct': 'Norway'},
    49: {'question': 'What is the capital of India?', 'options': ['Mumbai', 'Delhi', 'Bangalore', 'Kolkata'], 'correct': 'Delhi'},
    50: {'question': 'Which country is known as the Land of the Rising Sun?', 'options': ['China', 'Japan', 'South Korea', 'Thailand'], 'correct': 'Japan'},

    # Technology (50 Questions)
    51: {'question': 'What does CPU stand for?', 'options': ['Central Processing Unit', 'Computer Processing Unit', 'Central Program Unit', 'Computer Program Unit'], 'correct': 'Central Processing Unit'},
    52: {'question': 'Which programming language is known as the "mother of all languages"?', 'options': ['Python', 'C', 'Java', 'Assembly'], 'correct': 'C'},
    53: {'question': 'What is the full form of HTML?', 'options': ['HyperText Markup Language', 'Hyperlink and Text Markup Language', 'High-Level Text Machine Language', 'HyperText Machine Language'], 'correct': 'HyperText Markup Language'},
    54: {'question': 'Which company developed the Python programming language?', 'options': ['Microsoft', 'Google', 'Guido van Rossum', 'Apple'], 'correct': 'Guido van Rossum'},
    55: {'question': 'What is the primary function of RAM?', 'options': ['Long-term storage', 'Temporary storage for running applications', 'Processing graphics', 'Managing network connections'], 'correct': 'Temporary storage for running applications'},
    56: {'question': 'Which protocol is used for secure communication over the internet?', 'options': ['HTTP', 'FTP', 'HTTPS', 'SMTP'], 'correct': 'HTTPS'},
    57: {'question': 'What is the name of the first computer virus?', 'options': ['ILOVEYOU', 'Creeper', 'Stuxnet', 'Melissa'], 'correct': 'Creeper'},
    58: {'question': 'What does AI stand for?', 'options': ['Automated Intelligence', 'Artificial Intelligence', 'Advanced Interface', 'Algorithmic Intelligence'], 'correct': 'Artificial Intelligence'},
    59: {'question': 'Which company created the Android operating system?', 'options': ['Apple', 'Microsoft', 'Google', 'Samsung'], 'correct': 'Google'},
    60: {'question': 'What is the binary equivalent of the decimal number 10?', 'options': ['1010', '1001', '1100', '1111'], 'correct': '1010'},
    61: {'question': 'What is the main purpose of a firewall?', 'options': ['To block unauthorized access', 'To increase internet speed', 'To store data', 'To manage hardware resources'], 'correct': 'To block unauthorized access'},
    62: {'question': 'Which of the following is NOT a database management system?', 'options': ['MySQL', 'MongoDB', 'Oracle', 'HTML'], 'correct': 'HTML'},
    63: {'question': 'What is the full form of URL?', 'options': ['Uniform Resource Locator', 'Universal Resource Locator', 'Uniform Resource Link', 'Universal Resource Link'], 'correct': 'Uniform Resource Locator'},
    64: {'question': 'Which of the following is a cloud computing platform?', 'options': ['AWS', 'Photoshop', 'AutoCAD', 'MS Word'], 'correct': 'AWS'},
    65: {'question': 'What is the primary function of a GPU?', 'options': ['Processing graphics', 'Managing memory', 'Running the operating system', 'Storing data'], 'correct': 'Processing graphics'},
    66: {'question': 'Which of the following is NOT a programming language?', 'options': ['Python', 'Java', 'HTML', 'C++'], 'correct': 'HTML'},
    67: {'question': 'What is the full form of VPN?', 'options': ['Virtual Private Network', 'Virtual Public Network', 'Visual Private Network', 'Visual Public Network'], 'correct': 'Virtual Private Network'},
    68: {'question': 'Which company developed the first graphical web browser?', 'options': ['Microsoft', 'Netscape', 'Google', 'Apple'], 'correct': 'Netscape'},
    69: {'question': 'What is the full form of IoT?', 'options': ['Internet of Things', 'Internet of Technology', 'Interface of Things', 'Interface of Technology'], 'correct': 'Internet of Things'},
    70: {'question': 'Which of the following is a version control system?', 'options': ['Git', 'Docker', 'Kubernetes', 'Jenkins'], 'correct': 'Git'},
    71: {'question': 'What is the full form of API?', 'options': ['Application Programming Interface', 'Application Program Interface', 'Advanced Programming Interface', 'Advanced Program Interface'], 'correct': 'Application Programming Interface'},
    72: {'question': 'Which of the following is NOT an operating system?', 'options': ['Linux', 'Windows', 'macOS', 'Photoshop'], 'correct': 'Photoshop'},
    73: {'question': 'What is the full form of SSD?', 'options': ['Solid State Drive', 'Super Speed Drive', 'Solid Storage Device', 'Super Storage Device'], 'correct': 'Solid State Drive'},
    74: {'question': 'Which of the following is a machine learning framework?', 'options': ['TensorFlow', 'Django', 'Flask', 'React'], 'correct': 'TensorFlow'},
    75: {'question': 'What is the full form of DNS?', 'options': ['Domain Name System', 'Data Name System', 'Domain Network System', 'Data Network System'], 'correct': 'Domain Name System'},
    76: {'question': 'What is the primary function of a compiler?', 'options': ['Execute code', 'Translate high-level code to machine code', 'Debug code', 'Optimize code'], 'correct': 'Translate high-level code to machine code'},
    77: {'question': 'Which of the following is NOT a type of database?', 'options': ['Relational', 'NoSQL', 'Graph', 'Compiler'], 'correct': 'Compiler'},
    78: {'question': 'What is the full form of SQL?', 'options': ['Structured Query Language', 'Simple Query Language', 'Standard Query Language', 'System Query Language'], 'correct': 'Structured Query Language'},
    79: {'question': 'Which of the following is a front-end framework?', 'options': ['React', 'Django', 'Flask', 'Node.js'], 'correct': 'React'},
    80: {'question': 'What is the full form of CSS?', 'options': ['Cascading Style Sheets', 'Computer Style Sheets', 'Colorful Style Sheets', 'Creative Style Sheets'], 'correct': 'Cascading Style Sheets'},
    81: {'question': 'Which of the following is a back-end framework?', 'options': ['React', 'Angular', 'Django', 'Vue.js'], 'correct': 'Django'},
    82: {'question': 'What is the full form of JSON?', 'options': ['JavaScript Object Notation', 'Java Standard Object Notation', 'JavaScript Oriented Notation', 'Java Scripted Object Notation'], 'correct': 'JavaScript Object Notation'},
    83: {'question': 'Which of the following is a programming paradigm?', 'options': ['Object-Oriented', 'Functional', 'Procedural', 'All of the above'], 'correct': 'All of the above'},
    84: {'question': 'What is the full form of XML?', 'options': ['Extensible Markup Language', 'Extended Markup Language', 'Executable Markup Language', 'Extra Markup Language'], 'correct': 'Extensible Markup Language'},
    85: {'question': 'Which of the following is a scripting language?', 'options': ['Python', 'Java', 'C++', 'C#'], 'correct': 'Python'},
    86: {'question': 'What is the full form of IDE?', 'options': ['Integrated Development Environment', 'Interactive Development Environment', 'Integrated Debugging Environment', 'Interactive Debugging Environment'], 'correct': 'Integrated Development Environment'},
    87: {'question': 'Which of the following is a version control system?', 'options': ['Git', 'Docker', 'Kubernetes', 'Jenkins'], 'correct': 'Git'},
    88: {'question': 'What is the full form of HTTP?', 'options': ['HyperText Transfer Protocol', 'HyperText Transmission Protocol', 'HyperText Transfer Process', 'HyperText Transmission Process'], 'correct': 'HyperText Transfer Protocol'},
    89: {'question': 'Which of the following is a programming language?', 'options': ['HTML', 'CSS', 'JavaScript', 'XML'], 'correct': 'JavaScript'},
    90: {'question': 'What is the full form of FTP?', 'options': ['File Transfer Protocol', 'File Transmission Protocol', 'File Transfer Process', 'File Transmission Process'], 'correct': 'File Transfer Protocol'},
    91: {'question': 'Which of the following is a markup language?', 'options': ['HTML', 'CSS', 'JavaScript', 'Python'], 'correct': 'HTML'},
    92: {'question': 'What is the full form of CLI?', 'options': ['Command Line Interface', 'Command Language Interface', 'Command Line Interpreter', 'Command Language Interpreter'], 'correct': 'Command Line Interface'},
    93: {'question': 'Which of the following is a programming language?', 'options': ['HTML', 'CSS', 'JavaScript', 'XML'], 'correct': 'JavaScript'},
    94: {'question': 'What is the full form of GUI?', 'options': ['Graphical User Interface', 'Graphical Utility Interface', 'Graphical User Interpreter', 'Graphical Utility Interpreter'], 'correct': 'Graphical User Interface'},
    95: {'question': 'Which of the following is a programming language?', 'options': ['HTML', 'CSS', 'JavaScript', 'XML'], 'correct': 'JavaScript'},
    96: {'question': 'What is the full form of API?', 'options': ['Application Programming Interface', 'Application Program Interface', 'Advanced Programming Interface', 'Advanced Program Interface'], 'correct': 'Application Programming Interface'},
    97: {'question': 'Which of the following is a programming language?', 'options': ['HTML', 'CSS', 'JavaScript', 'XML'], 'correct': 'JavaScript'},
    98: {'question': 'What is the full form of SQL?', 'options': ['Structured Query Language', 'Simple Query Language', 'Standard Query Language', 'System Query Language'], 'correct': 'Structured Query Language'},
    99: {'question': 'Which of the following is a programming language?', 'options': ['HTML', 'CSS', 'JavaScript', 'XML'], 'correct': 'JavaScript'},
    100: {'question': 'What is the full form of CSS?', 'options': ['Cascading Style Sheets', 'Computer Style Sheets', 'Colorful Style Sheets', 'Creative Style Sheets'], 'correct': 'Cascading Style Sheets'},

    # Ecosystem/Biology/Environment/Health (50 Questions)
    101: {'question': 'What is the largest ecosystem on Earth?', 'options': ['Desert', 'Ocean', 'Forest', 'Grassland'], 'correct': 'Ocean'},
    102: {'question': 'Which gas is most abundant in the Earth\'s atmosphere?', 'options': ['Oxygen', 'Nitrogen', 'Carbon Dioxide', 'Argon'], 'correct': 'Nitrogen'},
    103: {'question': 'What is the primary source of energy for most ecosystems?', 'options': ['Wind', 'Sun', 'Water', 'Soil'], 'correct': 'Sun'},
    104: {'question': 'Which of the following is a greenhouse gas?', 'options': ['Oxygen', 'Nitrogen', 'Carbon Dioxide', 'Argon'], 'correct': 'Carbon Dioxide'},
    105: {'question': 'What is the process by which plants make their own food called?', 'options': ['Respiration', 'Photosynthesis', 'Transpiration', 'Digestion'], 'correct': 'Photosynthesis'},
    106: {'question': 'Which of the following is a decomposer?', 'options': ['Lion', 'Eagle', 'Fungi', 'Grass'], 'correct': 'Fungi'},
    107: {'question': 'What is the main cause of deforestation?', 'options': ['Urbanization', 'Agriculture', 'Mining', 'All of the above'], 'correct': 'All of the above'},
    108: {'question': 'Which layer of the Earth\'s atmosphere contains the ozone layer?', 'options': ['Troposphere', 'Stratosphere', 'Mesosphere', 'Thermosphere'], 'correct': 'Stratosphere'},
    109: {'question': 'What is the primary cause of global warming?', 'options': ['Increase in greenhouse gases', 'Deforestation', 'Industrialization', 'All of the above'], 'correct': 'All of the above'},
    110: {'question': 'Which of the following is a renewable resource?', 'options': ['Coal', 'Natural Gas', 'Solar Energy', 'Petroleum'], 'correct': 'Solar Energy'},
    111: {'question': 'What is the largest organ in the human body?', 'options': ['Heart', 'Liver', 'Skin', 'Brain'], 'correct': 'Skin'},
    112: {'question': 'Which gas do plants absorb during photosynthesis?', 'options': ['Oxygen', 'Carbon Dioxide', 'Nitrogen', 'Hydrogen'], 'correct': 'Carbon Dioxide'},
    113: {'question': 'What is the main function of red blood cells?', 'options': ['Fight infection', 'Carry oxygen', 'Digest food', 'Produce hormones'], 'correct': 'Carry oxygen'},
    114: {'question': 'Which vitamin is produced by the human body when exposed to sunlight?', 'options': ['Vitamin A', 'Vitamin B', 'Vitamin C', 'Vitamin D'], 'correct': 'Vitamin D'},
    115: {'question': 'What is the largest bone in the human body?', 'options': ['Femur', 'Tibia', 'Humerus', 'Skull'], 'correct': 'Femur'},
    116: {'question': 'Which of the following is NOT a type of blood cell?', 'options': ['Red blood cell', 'White blood cell', 'Platelet', 'Plasma cell'], 'correct': 'Plasma cell'},
    117: {'question': 'What is the main function of the respiratory system?', 'options': ['Pump blood', 'Digest food', 'Exchange gases', 'Filter toxins'], 'correct': 'Exchange gases'},
    118: {'question': 'Which organ produces insulin?', 'options': ['Liver', 'Pancreas', 'Kidney', 'Stomach'], 'correct': 'Pancreas'},
    119: {'question': 'What is the main function of the nervous system?', 'options': ['Control body movements', 'Transport nutrients', 'Produce hormones', 'Filter blood'], 'correct': 'Control body movements'},
    120: {'question': 'Which of the following is a non-renewable resource?', 'options': ['Solar energy', 'Wind energy', 'Coal', 'Hydropower'], 'correct': 'Coal'},
    121: {'question': 'What is the main cause of air pollution?', 'options': ['Deforestation', 'Industrial emissions', 'Agricultural runoff', 'Volcanic eruptions'], 'correct': 'Industrial emissions'},
    122: {'question': 'Which of the following is a primary pollutant?', 'options': ['Ozone', 'Carbon Monoxide', 'Sulfuric Acid', 'Nitric Acid'], 'correct': 'Carbon Monoxide'},
    123: {'question': 'What is the main cause of water pollution?', 'options': ['Industrial waste', 'Agricultural runoff', 'Sewage', 'All of the above'], 'correct': 'All of the above'},
    124: {'question': 'Which of the following is a greenhouse gas?', 'options': ['Oxygen', 'Nitrogen', 'Methane', 'Argon'], 'correct': 'Methane'},
    125: {'question': 'What is the main cause of soil erosion?', 'options': ['Deforestation', 'Overgrazing', 'Agricultural practices', 'All of the above'], 'correct': 'All of the above'},
    126: {'question': 'Which of the following is a renewable resource?', 'options': ['Coal', 'Natural Gas', 'Solar Energy', 'Petroleum'], 'correct': 'Solar Energy'},
    127: {'question': 'What is the main function of the circulatory system?', 'options': ['Transport nutrients', 'Exchange gases', 'Filter toxins', 'Produce hormones'], 'correct': 'Transport nutrients'},
    128: {'question': 'Which of the following is a type of renewable energy?', 'options': ['Coal', 'Natural Gas', 'Solar Energy', 'Petroleum'], 'correct': 'Solar Energy'},
    129: {'question': 'What is the main function of the digestive system?', 'options': ['Transport nutrients', 'Exchange gases', 'Filter toxins', 'Break down food'], 'correct': 'Break down food'},
    130: {'question': 'Which of the following is a type of non-renewable energy?', 'options': ['Solar Energy', 'Wind Energy', 'Coal', 'Hydropower'], 'correct': 'Coal'},
    131: {'question': 'What is the main function of the excretory system?', 'options': ['Transport nutrients', 'Exchange gases', 'Filter toxins', 'Produce hormones'], 'correct': 'Filter toxins'},
    132: {'question': 'Which of the following is a type of renewable energy?', 'options': ['Coal', 'Natural Gas', 'Solar Energy', 'Petroleum'], 'correct': 'Solar Energy'},
    133: {'question': 'What is the main function of the endocrine system?', 'options': ['Transport nutrients', 'Exchange gases', 'Filter toxins', 'Produce hormones'], 'correct': 'Produce hormones'},
    134: {'question': 'Which of the following is a type of non-renewable energy?', 'options': ['Solar Energy', 'Wind Energy', 'Coal', 'Hydropower'], 'correct': 'Coal'},
    135: {'question': 'What is the main function of the immune system?', 'options': ['Transport nutrients', 'Exchange gases', 'Filter toxins', 'Fight infections'], 'correct': 'Fight infections'},
    136: {'question': 'Which of the following is a type of renewable energy?', 'options': ['Coal', 'Natural Gas', 'Solar Energy', 'Petroleum'], 'correct': 'Solar Energy'},
    137: {'question': 'What is the main function of the lymphatic system?', 'options': ['Transport nutrients', 'Exchange gases', 'Filter toxins', 'Fight infections'], 'correct': 'Fight infections'},
    138: {'question': 'Which of the following is a type of non-renewable energy?', 'options': ['Solar Energy', 'Wind Energy', 'Coal', 'Hydropower'], 'correct': 'Coal'},
    139: {'question': 'What is the main function of the muscular system?', 'options': ['Transport nutrients', 'Exchange gases', 'Filter toxins', 'Enable movement'], 'correct': 'Enable movement'},
    140: {'question': 'Which of the following is a type of renewable energy?', 'options': ['Coal', 'Natural Gas', 'Solar Energy', 'Petroleum'], 'correct': 'Solar Energy'},
    141: {'question': 'What is the main function of the skeletal system?', 'options': ['Transport nutrients', 'Exchange gases', 'Filter toxins', 'Provide structure'], 'correct': 'Provide structure'},
    142: {'question': 'Which of the following is a type of non-renewable energy?', 'options': ['Solar Energy', 'Wind Energy', 'Coal', 'Hydropower'], 'correct': 'Coal'},
    143: {'question': 'What is the main function of the reproductive system?', 'options': ['Transport nutrients', 'Exchange gases', 'Filter toxins', 'Produce offspring'], 'correct': 'Produce offspring'},
    144: {'question': 'Which of the following is a type of renewable energy?', 'options': ['Coal', 'Natural Gas', 'Solar Energy', 'Petroleum'], 'correct': 'Solar Energy'},
    145: {'question': 'What is the main function of the urinary system?', 'options': ['Transport nutrients', 'Exchange gases', 'Filter toxins', 'Remove waste'], 'correct': 'Remove waste'},
    146: {'question': 'Which of the following is a type of non-renewable energy?', 'options': ['Solar Energy', 'Wind Energy', 'Coal', 'Hydropower'], 'correct': 'Coal'},
    147: {'question': 'What is the main function of the integumentary system?', 'options': ['Transport nutrients', 'Exchange gases', 'Filter toxins', 'Protect the body'], 'correct': 'Protect the body'},
    148: {'question': 'Which of the following is a type of renewable energy?', 'options': ['Coal', 'Natural Gas', 'Solar Energy', 'Petroleum'], 'correct': 'Solar Energy'},
    149: {'question': 'What is the main function of the nervous system?', 'options': ['Transport nutrients', 'Exchange gases', 'Filter toxins', 'Control body functions'], 'correct': 'Control body functions'},
    150: {'question': 'Which of the following is a type of non-renewable energy?', 'options': ['Solar Energy', 'Wind Energy', 'Coal', 'Hydropower'], 'correct': 'Coal'},

    # Aptitude (50 Questions)
    151: {'question': 'If 2x + 5 = 15, what is the value of x?', 'options': ['5', '10', '7.5', '2.5'], 'correct': '5'},
    152: {'question': 'What is 25% of 200?', 'options': ['50', '25', '100', '75'], 'correct': '50'},
    153: {'question': 'If a train travels 300 km in 5 hours, what is its speed?', 'options': ['50 km/h', '60 km/h', '70 km/h', '80 km/h'], 'correct': '60 km/h'},
    154: {'question': 'What is the next number in the sequence: 2, 4, 6, 8, ___?', 'options': ['10', '12', '14', '16'], 'correct': '10'},
    155: {'question': 'If a shirt costs $20 and is discounted by 20%, what is the final price?', 'options': ['$16', '$18', '$15', '$14'], 'correct': '$16'},
    156: {'question': 'What is the square root of 144?', 'options': ['12', '14', '16', '18'], 'correct': '12'},
    157: {'question': 'If 3x - 7 = 14, what is the value of x?', 'options': ['7', '8', '9', '10'], 'correct': '7'},
    158: {'question': 'What is 15% of 300?', 'options': ['30', '45', '60', '75'], 'correct': '45'},
    159: {'question': 'If a car travels 240 km in 4 hours, what is its speed?', 'options': ['50 km/h', '60 km/h', '70 km/h', '80 km/h'], 'correct': '60 km/h'},
    160: {'question': 'What is the next number in the sequence: 5, 10, 15, 20, ___?', 'options': ['25', '30', '35', '40'], 'correct': '25'},
    161: {'question': 'If a book costs $25 and is discounted by 10%, what is the final price?', 'options': ['$22.50', '$23.50', '$24.50', '$25.50'], 'correct': '$22.50'},
    162: {'question': 'What is the cube of 3?', 'options': ['9', '27', '81', '243'], 'correct': '27'},
    163: {'question': 'If 4x + 8 = 24, what is the value of x?', 'options': ['4', '5', '6', '7'], 'correct': '4'},
    164: {'question': 'What is 20% of 500?', 'options': ['50', '100', '150', '200'], 'correct': '100'},
    165: {'question': 'If a bus travels 180 km in 3 hours, what is its speed?', 'options': ['50 km/h', '60 km/h', '70 km/h', '80 km/h'], 'correct': '60 km/h'},
    166: {'question': 'What is the next number in the sequence: 10, 20, 30, 40, ___?', 'options': ['50', '60', '70', '80'], 'correct': '50'},
    167: {'question': 'If a laptop costs $800 and is discounted by 15%, what is the final price?', 'options': ['$680', '$700', '$720', '$740'], 'correct': '$680'},
    168: {'question': 'What is the square of 12?', 'options': ['144', '169', '196', '225'], 'correct': '144'},
    169: {'question': 'If 5x - 10 = 20, what is the value of x?', 'options': ['6', '7', '8', '9'], 'correct': '6'},
    170: {'question': 'What is 30% of 400?', 'options': ['100', '120', '140', '160'], 'correct': '120'},
    171: {'question': 'If a train travels 360 km in 6 hours, what is its speed?', 'options': ['50 km/h', '60 km/h', '70 km/h', '80 km/h'], 'correct': '60 km/h'},
    172: {'question': 'What is the next number in the sequence: 15, 30, 45, 60, ___?', 'options': ['75', '90', '105', '120'], 'correct': '75'},
    173: {'question': 'If a phone costs $500 and is discounted by 25%, what is the final price?', 'options': ['$375', '$400', '$425', '$450'], 'correct': '$375'},
    174: {'question': 'What is the cube of 4?', 'options': ['16', '64', '128', '256'], 'correct': '64'},
    175: {'question': 'If 6x - 12 = 24, what is the value of x?', 'options': ['6', '7', '8', '9'], 'correct': '6'},
    176: {'question': 'What is 40% of 600?', 'options': ['200', '240', '260', '280'], 'correct': '240'},
    177: {'question': 'If a car travels 420 km in 7 hours, what is its speed?', 'options': ['50 km/h', '60 km/h', '70 km/h', '80 km/h'], 'correct': '60 km/h'},
    178: {'question': 'What is the next number in the sequence: 20, 40, 60, 80, ___?', 'options': ['100', '120', '140', '160'], 'correct': '100'},
    179: {'question': 'If a tablet costs $300 and is discounted by 10%, what is the final price?', 'options': ['$270', '$280', '$290', '$300'], 'correct': '$270'},
    180: {'question': 'What is the square of 15?', 'options': ['225', '250', '275', '300'], 'correct': '225'},
    181: {'question': 'If 7x - 14 = 28, what is the value of x?', 'options': ['6', '7', '8', '9'], 'correct': '6'},
    182: {'question': 'What is 50% of 800?', 'options': ['400', '450', '500', '550'], 'correct': '400'},
    183: {'question': 'If a train travels 480 km in 8 hours, what is its speed?', 'options': ['50 km/h', '60 km/h', '70 km/h', '80 km/h'], 'correct': '60 km/h'},
    184: {'question': 'What is the next number in the sequence: 25, 50, 75, 100, ___?', 'options': ['125', '150', '175', '200'], 'correct': '125'},
    185: {'question': 'If a laptop costs $1000 and is discounted by 20%, what is the final price?', 'options': ['$800', '$820', '$840', '$860'], 'correct': '$800'},
    186: {'question': 'What is the cube of 5?', 'options': ['125', '150', '175', '200'], 'correct': '125'},
    187: {'question': 'If 8x - 16 = 32, what is the value of x?', 'options': ['6', '7', '8', '9'], 'correct': '6'},
    188: {'question': 'What is 60% of 900?', 'options': ['540', '560', '580', '600'], 'correct': '540'},
    189: {'question': 'If a car travels 540 km in 9 hours, what is its speed?', 'options': ['50 km/h', '60 km/h', '70 km/h', '80 km/h'], 'correct': '60 km/h'},
    190: {'question': 'What is the next number in the sequence: 30, 60, 90, 120, ___?', 'options': ['150', '180', '210', '240'], 'correct': '150'},
    191: {'question': 'If a phone costs $600 and is discounted by 30%, what is the final price?', 'options': ['$420', '$440', '$460', '$480'], 'correct': '$420'},
    192: {'question': 'What is the square of 20?', 'options': ['400', '450', '500', '550'], 'correct': '400'},
    193: {'question': 'If 9x - 18 = 36, what is the value of x?', 'options': ['6', '7', '8', '9'], 'correct': '6'},
    194: {'question': 'What is 70% of 1000?', 'options': ['700', '750', '800', '850'], 'correct': '700'},
    195: {'question': 'If a train travels 600 km in 10 hours, what is its speed?', 'options': ['50 km/h', '60 km/h', '70 km/h', '80 km/h'], 'correct': '60 km/h'},
    196: {'question': 'What is the next number in the sequence: 35, 70, 105, 140, ___?', 'options': ['175', '210', '245', '280'], 'correct': '175'},
    197: {'question': 'If a laptop costs $1200 and is discounted by 25%, what is the final price?', 'options': ['$900', '$950', '$1000', '$1050'], 'correct': '$900'},
    198: {'question': 'What is the cube of 6?', 'options': ['216', '250', '275', '300'], 'correct': '216'},
    199: {'question': 'If 10x - 20 = 40, what is the value of x?', 'options': ['6', '7', '8', '9'], 'correct': '6'},
    200: {'question': 'What is 80% of 1200?', 'options': ['960', '1000', '1040', '1080'], 'correct': '960'},
    
    # General Knowledge (25 Questions)
    201: {'question': 'What is the capital of France?', 'options': ['Paris', 'London', 'Berlin', 'Madrid'], 'correct': 'Paris'},
    202: {'question': 'Who wrote "Romeo and Juliet"?', 'options': ['William Shakespeare', 'Charles Dickens', 'Mark Twain', 'Jane Austen'], 'correct': 'William Shakespeare'},
    203: {'question': 'Which planet is known as the Red Planet?', 'options': ['Earth', 'Mars', 'Jupiter', 'Saturn'], 'correct': 'Mars'},
    204: {'question': 'What is the largest ocean on Earth?', 'options': ['Atlantic Ocean', 'Indian Ocean', 'Arctic Ocean', 'Pacific Ocean'], 'correct': 'Pacific Ocean'},
    205: {'question': 'Who painted the Mona Lisa?', 'options': ['Vincent van Gogh', 'Pablo Picasso', 'Leonardo da Vinci', 'Claude Monet'], 'correct': 'Leonardo da Vinci'},
    206: {'question': 'What is the currency of Japan?', 'options': ['Yen', 'Dollar', 'Euro', 'Pound'], 'correct': 'Yen'},
    207: {'question': 'Which country is known as the Land of the Rising Sun?', 'options': ['China', 'Japan', 'South Korea', 'Thailand'], 'correct': 'Japan'},
    208: {'question': 'Who invented the telephone?', 'options': ['Thomas Edison', 'Alexander Graham Bell', 'Nikola Tesla', 'Albert Einstein'], 'correct': 'Alexander Graham Bell'},
    209: {'question': 'What is the smallest prime number?', 'options': ['1', '2', '3', '5'], 'correct': '2'},
    210: {'question': 'Which gas is most abundant in the Earth\'s atmosphere?', 'options': ['Oxygen', 'Nitrogen', 'Carbon Dioxide', 'Argon'], 'correct': 'Nitrogen'},
    211: {'question': 'What is the chemical symbol for water?', 'options': ['H2O', 'CO2', 'NaCl', 'O2'], 'correct': 'H2O'},
    212: {'question': 'Who is known as the Father of Computers?', 'options': ['Charles Babbage', 'Alan Turing', 'Bill Gates', 'Steve Jobs'], 'correct': 'Charles Babbage'},
    213: {'question': 'What is the largest mammal in the world?', 'options': ['Elephant', 'Blue Whale', 'Giraffe', 'Shark'], 'correct': 'Blue Whale'},
    214: {'question': 'Which country is famous for the Great Wall?', 'options': ['India', 'China', 'Japan', 'Russia'], 'correct': 'China'},
    215: {'question': 'What is the longest river in the world?', 'options': ['Nile', 'Amazon', 'Yangtze', 'Mississippi'], 'correct': 'Nile'},
    216: {'question': 'Which is the largest desert in the world?', 'options': ['Sahara', 'Arabian', 'Gobi', 'Antarctic'], 'correct': 'Antarctic'},
    217: {'question': 'Who discovered gravity?', 'options': ['Isaac Newton', 'Albert Einstein', 'Galileo Galilei', 'Stephen Hawking'], 'correct': 'Isaac Newton'},
    218: {'question': 'What is the capital of Australia?', 'options': ['Sydney', 'Melbourne', 'Canberra', 'Perth'], 'correct': 'Canberra'},
    219: {'question': 'Which is the smallest continent?', 'options': ['Asia', 'Africa', 'Australia', 'Europe'], 'correct': 'Australia'},
    220: {'question': 'What is the chemical symbol for gold?', 'options': ['Au', 'Ag', 'Fe', 'Cu'], 'correct': 'Au'},
    221: {'question': 'Which planet is closest to the Sun?', 'options': ['Earth', 'Venus', 'Mercury', 'Mars'], 'correct': 'Mercury'},
    222: {'question': 'Who wrote "The Theory of Relativity"?', 'options': ['Isaac Newton', 'Albert Einstein', 'Stephen Hawking', 'Galileo Galilei'], 'correct': 'Albert Einstein'},
    223: {'question': 'What is the largest organ in the human body?', 'options': ['Heart', 'Liver', 'Skin', 'Brain'], 'correct': 'Skin'},
    224: {'question': 'Which country is known as the Land of the Midnight Sun?', 'options': ['Norway', 'Sweden', 'Finland', 'Iceland'], 'correct': 'Norway'},
    225: {'question': 'What is the chemical symbol for oxygen?', 'options': ['O2', 'CO2', 'H2O', 'N2'], 'correct': 'O2'},

    # Technology (25 Questions)
    226: {'question': 'What does CPU stand for?', 'options': ['Central Processing Unit', 'Computer Processing Unit', 'Central Program Unit', 'Computer Program Unit'], 'correct': 'Central Processing Unit'},
    227: {'question': 'Which programming language is known as the "mother of all languages"?', 'options': ['Python', 'C', 'Java', 'Assembly'], 'correct': 'C'},
    228: {'question': 'What is the full form of HTML?', 'options': ['HyperText Markup Language', 'Hyperlink and Text Markup Language', 'High-Level Text Machine Language', 'HyperText Machine Language'], 'correct': 'HyperText Markup Language'},
    229: {'question': 'Which company developed the Python programming language?', 'options': ['Microsoft', 'Google', 'Guido van Rossum', 'Apple'], 'correct': 'Guido van Rossum'},
    230: {'question': 'What is the primary function of RAM?', 'options': ['Long-term storage', 'Temporary storage for running applications', 'Processing graphics', 'Managing network connections'], 'correct': 'Temporary storage for running applications'},
    231: {'question': 'Which protocol is used for secure communication over the internet?', 'options': ['HTTP', 'FTP', 'HTTPS', 'SMTP'], 'correct': 'HTTPS'},
    232: {'question': 'What is the name of the first computer virus?', 'options': ['ILOVEYOU', 'Creeper', 'Stuxnet', 'Melissa'], 'correct': 'Creeper'},
    233: {'question': 'What does AI stand for?', 'options': ['Automated Intelligence', 'Artificial Intelligence', 'Advanced Interface', 'Algorithmic Intelligence'], 'correct': 'Artificial Intelligence'},
    234: {'question': 'Which company created the Android operating system?', 'options': ['Apple', 'Microsoft', 'Google', 'Samsung'], 'correct': 'Google'},
    235: {'question': 'What is the binary equivalent of the decimal number 10?', 'options': ['1010', '1001', '1100', '1111'], 'correct': '1010'},
    236: {'question': 'What is the main purpose of a firewall?', 'options': ['To block unauthorized access', 'To increase internet speed', 'To store data', 'To manage hardware resources'], 'correct': 'To block unauthorized access'},
    237: {'question': 'Which of the following is NOT a database management system?', 'options': ['MySQL', 'MongoDB', 'Oracle', 'HTML'], 'correct': 'HTML'},
    238: {'question': 'What is the full form of URL?', 'options': ['Uniform Resource Locator', 'Universal Resource Locator', 'Uniform Resource Link', 'Universal Resource Link'], 'correct': 'Uniform Resource Locator'},
    239: {'question': 'Which of the following is a cloud computing platform?', 'options': ['AWS', 'Photoshop', 'AutoCAD', 'MS Word'], 'correct': 'AWS'},
    240: {'question': 'What is the primary function of a GPU?', 'options': ['Processing graphics', 'Managing memory', 'Running the operating system', 'Storing data'], 'correct': 'Processing graphics'},
    241: {'question': 'Which of the following is NOT a programming language?', 'options': ['Python', 'Java', 'HTML', 'C++'], 'correct': 'HTML'},
    242: {'question': 'What is the full form of VPN?', 'options': ['Virtual Private Network', 'Virtual Public Network', 'Visual Private Network', 'Visual Public Network'], 'correct': 'Virtual Private Network'},
    243: {'question': 'Which company developed the first graphical web browser?', 'options': ['Microsoft', 'Netscape', 'Google', 'Apple'], 'correct': 'Netscape'},
    244: {'question': 'What is the full form of IoT?', 'options': ['Internet of Things', 'Internet of Technology', 'Interface of Things', 'Interface of Technology'], 'correct': 'Internet of Things'},
    245: {'question': 'Which of the following is a version control system?', 'options': ['Git', 'Docker', 'Kubernetes', 'Jenkins'], 'correct': 'Git'},
    246: {'question': 'What is the full form of API?', 'options': ['Application Programming Interface', 'Application Program Interface', 'Advanced Programming Interface', 'Advanced Program Interface'], 'correct': 'Application Programming Interface'},
    247: {'question': 'Which of the following is NOT an operating system?', 'options': ['Linux', 'Windows', 'macOS', 'Photoshop'], 'correct': 'Photoshop'},
    248: {'question': 'What is the full form of SSD?', 'options': ['Solid State Drive', 'Super Speed Drive', 'Solid Storage Device', 'Super Storage Device'], 'correct': 'Solid State Drive'},
    249: {'question': 'Which of the following is a machine learning framework?', 'options': ['TensorFlow', 'Django', 'Flask', 'React'], 'correct': 'TensorFlow'},
    250: {'question': 'What is the full form of DNS?', 'options': ['Domain Name System', 'Data Name System', 'Domain Network System', 'Data Network System'], 'correct': 'Domain Name System'},

    # Ecosystem/Biology/Environment/Health (25 Questions)
    251: {'question': 'What is the largest ecosystem on Earth?', 'options': ['Desert', 'Ocean', 'Forest', 'Grassland'], 'correct': 'Ocean'},
    252: {'question': 'Which gas is most abundant in the Earth\'s atmosphere?', 'options': ['Oxygen', 'Nitrogen', 'Carbon Dioxide', 'Argon'], 'correct': 'Nitrogen'},
    253: {'question': 'What is the primary source of energy for most ecosystems?', 'options': ['Wind', 'Sun', 'Water', 'Soil'], 'correct': 'Sun'},
    254: {'question': 'Which of the following is a greenhouse gas?', 'options': ['Oxygen', 'Nitrogen', 'Carbon Dioxide', 'Argon'], 'correct': 'Carbon Dioxide'},
    255: {'question': 'What is the process by which plants make their own food called?', 'options': ['Respiration', 'Photosynthesis', 'Transpiration', 'Digestion'], 'correct': 'Photosynthesis'},
    256: {'question': 'Which of the following is a decomposer?', 'options': ['Lion', 'Eagle', 'Fungi', 'Grass'], 'correct': 'Fungi'},
    257: {'question': 'What is the main cause of deforestation?', 'options': ['Urbanization', 'Agriculture', 'Mining', 'All of the above'], 'correct': 'All of the above'},
    258: {'question': 'Which layer of the Earth\'s atmosphere contains the ozone layer?', 'options': ['Troposphere', 'Stratosphere', 'Mesosphere', 'Thermosphere'], 'correct': 'Stratosphere'},
    259: {'question': 'What is the primary cause of global warming?', 'options': ['Increase in greenhouse gases', 'Deforestation', 'Industrialization', 'All of the above'], 'correct': 'All of the above'},
    260: {'question': 'Which of the following is a renewable resource?', 'options': ['Coal', 'Natural Gas', 'Solar Energy', 'Petroleum'], 'correct': 'Solar Energy'},
    261: {'question': 'What is the largest organ in the human body?', 'options': ['Heart', 'Liver', 'Skin', 'Brain'], 'correct': 'Skin'},
    262: {'question': 'Which gas do plants absorb during photosynthesis?', 'options': ['Oxygen', 'Carbon Dioxide', 'Nitrogen', 'Hydrogen'], 'correct': 'Carbon Dioxide'},
    263: {'question': 'What is the main function of red blood cells?', 'options': ['Fight infection', 'Carry oxygen', 'Digest food', 'Produce hormones'], 'correct': 'Carry oxygen'},
    264: {'question': 'Which vitamin is produced by the human body when exposed to sunlight?', 'options': ['Vitamin A', 'Vitamin B', 'Vitamin C', 'Vitamin D'], 'correct': 'Vitamin D'},
    265: {'question': 'What is the largest bone in the human body?', 'options': ['Femur', 'Tibia', 'Humerus', 'Skull'], 'correct': 'Femur'},
    266: {'question': 'Which of the following is NOT a type of blood cell?', 'options': ['Red blood cell', 'White blood cell', 'Platelet', 'Plasma cell'], 'correct': 'Plasma cell'},
    267: {'question': 'What is the main function of the respiratory system?', 'options': ['Pump blood', 'Digest food', 'Exchange gases', 'Filter toxins'], 'correct': 'Exchange gases'},
    268: {'question': 'Which organ produces insulin?', 'options': ['Liver', 'Pancreas', 'Kidney', 'Stomach'], 'correct': 'Pancreas'},
    269: {'question': 'What is the main function of the nervous system?', 'options': ['Control body movements', 'Transport nutrients', 'Produce hormones', 'Filter blood'], 'correct': 'Control body movements'},
    270: {'question': 'Which of the following is a non-renewable resource?', 'options': ['Solar energy', 'Wind energy', 'Coal', 'Hydropower'], 'correct': 'Coal'},
    271: {'question': 'What is the main cause of air pollution?', 'options': ['Deforestation', 'Industrial emissions', 'Agricultural runoff', 'Volcanic eruptions'], 'correct': 'Industrial emissions'},
    272: {'question': 'Which of the following is a primary pollutant?', 'options': ['Ozone', 'Carbon Monoxide', 'Sulfuric Acid', 'Nitric Acid'], 'correct': 'Carbon Monoxide'},
    273: {'question': 'What is the main cause of water pollution?', 'options': ['Industrial waste', 'Agricultural runoff', 'Sewage', 'All of the above'], 'correct': 'All of the above'},
    274: {'question': 'Which of the following is a greenhouse gas?', 'options': ['Oxygen', 'Nitrogen', 'Methane', 'Argon'], 'correct': 'Methane'},
    275: {'question': 'What is the main cause of soil erosion?', 'options': ['Deforestation', 'Overgrazing', 'Agricultural practices', 'All of the above'], 'correct': 'All of the above'},

    # Aptitude (25 Questions)
    276: {'question': 'If 2x + 5 = 15, what is the value of x?', 'options': ['5', '10', '7.5', '2.5'], 'correct': '5'},
    277: {'question': 'What is 25% of 200?', 'options': ['50', '25', '100', '75'], 'correct': '50'},
    278: {'question': 'If a train travels 300 km in 5 hours, what is its speed?', 'options': ['50 km/h', '60 km/h', '70 km/h', '80 km/h'], 'correct': '60 km/h'},
    279: {'question': 'What is the next number in the sequence: 2, 4, 6, 8, ___?', 'options': ['10', '12', '14', '16'], 'correct': '10'},
    280: {'question': 'If a shirt costs $20 and is discounted by 20%, what is the final price?', 'options': ['$16', '$18', '$15', '$14'], 'correct': '$16'},
    281: {'question': 'What is the square root of 144?', 'options': ['12', '14', '16', '18'], 'correct': '12'},
    282: {'question': 'If 3x - 7 = 14, what is the value of x?', 'options': ['7', '8', '9', '10'], 'correct': '7'},
    283: {'question': 'What is 15% of 300?', 'options': ['30', '45', '60', '75'], 'correct': '45'},
    284: {'question': 'If a car travels 240 km in 4 hours, what is its speed?', 'options': ['50 km/h', '60 km/h', '70 km/h', '80 km/h'], 'correct': '60 km/h'},
    285: {'question': 'What is the next number in the sequence: 5, 10, 15, 20, ___?', 'options': ['25', '30', '35', '40'], 'correct': '25'},
    286: {'question': 'If a book costs $25 and is discounted by 10%, what is the final price?', 'options': ['$22.50', '$23.50', '$24.50', '$25.50'], 'correct': '$22.50'},
    287: {'question': 'What is the cube of 3?', 'options': ['9', '27', '81', '243'], 'correct': '27'},
    288: {'question': 'If 4x + 8 = 24, what is the value of x?', 'options': ['4', '5', '6', '7'], 'correct': '4'},
    289: {'question': 'What is 20% of 500?', 'options': ['50', '100', '150', '200'], 'correct': '100'},
    290: {'question': 'If a bus travels 180 km in 3 hours, what is its speed?', 'options': ['50 km/h', '60 km/h', '70 km/h', '80 km/h'], 'correct': '60 km/h'},
    291: {'question': 'What is the next number in the sequence: 10, 20, 30, 40, ___?', 'options': ['50', '60', '70', '80'], 'correct': '50'},
    292: {'question': 'If a laptop costs $800 and is discounted by 15%, what is the final price?', 'options': ['$680', '$700', '$720', '$740'], 'correct': '$680'},
    293: {'question': 'What is the square of 12?', 'options': ['144', '169', '196', '225'], 'correct': '144'},
    294: {'question': 'If 5x - 10 = 20, what is the value of x?', 'options': ['6', '7', '8', '9'], 'correct': '6'},
    295: {'question': 'What is 30% of 400?', 'options': ['100', '120', '140', '160'], 'correct': '120'},
    296: {'question': 'If a train travels 360 km in 6 hours, what is its speed?', 'options': ['50 km/h', '60 km/h', '70 km/h', '80 km/h'], 'correct': '60 km/h'},
    297: {'question': 'What is the next number in the sequence: 15, 30, 45, 60, ___?', 'options': ['75', '90', '105', '120'], 'correct': '75'},
    298: {'question': 'If a phone costs $500 and is discounted by 25%, what is the final price?', 'options': ['$375', '$400', '$425', '$450'], 'correct': '$375'},
    299: {'question': 'What is the cube of 4?', 'options': ['16', '64', '128', '256'], 'correct': '64'},
    300: {'question': 'If 6x - 12 = 24, what is the value of x?', 'options': ['6', '7', '8', '9'], 'correct': '6'},
}

# Function to get 30 random questions
def get_random_questions():
    all_questions = list(quiz_questions.items())
    random.shuffle(all_questions)
    return dict(all_questions[:30])

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('quiz'))
        else:
            flash('Invalid email or password')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user is None:
            user = User(username=username, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect(url_for('quiz'))
        else:
            flash('Username or email already exists')
    return render_template('register.html')

@app.route('/quiz', methods=['GET', 'POST'])
@login_required
def quiz():
    if request.method == 'POST':
        score = 0
        for question_id, question_data in session.get('current_quiz', {}).items():
            user_answer = request.form.get(str(question_id))
            if user_answer == question_data['correct']:
                score += 1
        new_score = Score(score=score, user_id=current_user.id)
        db.session.add(new_score)
        db.session.commit()
        return redirect(url_for('results'))
    # Get 30 random questions and store them in the session
    session['current_quiz'] = get_random_questions()
    return render_template('quiz.html', questions=session['current_quiz'])

@app.route('/results')
@login_required
def results():
    scores = Score.query.filter_by(user_id=current_user.id).all()
    return render_template('results.html', scores=scores)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        # Create all database tables
        db.create_all()
    app.run(debug=True)