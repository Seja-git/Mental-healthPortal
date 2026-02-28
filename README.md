# Health-Portal
My Digital mental health and psychological support system portal for students
🧠 Mental Wellness Portal
AI-Driven Mental Health Support & Counselling Platform
________________________________________
📌 Project Title
Mental Wellness Portal – AI-Driven Mental Health Support System
________________________________________
👩‍💻 Team Members
•	Sonali Singh
•	Komal Karle
•	Sejal Patil
________________________________________
❗ Problem Statement
Mental health issues among students are increasing due to academic pressure, social stress, and personal challenges. However:
•	Many students hesitate to seek help due to stigma.
•	There is a lack of accessible and anonymous support systems.
•	Manual appointment booking systems are inefficient.
•	Institutions lack proper data analytics to track mental health trends.
•	Crisis situations are not detected early.
There is a need for a secure, anonymous, and technology-driven mental health support platform that connects students with counsellors while providing self-assessment and crisis detection tools.
________________________________________
💡 Solution Approach
The Mental Wellness Portal is a full-stack web application designed to:
•	Provide anonymous mental health screenings (PHQ-9, GAD-7).
•	Detect crisis situations automatically.
•	Allow students to book counselling appointments.
•	Enable peer-support through moderated forum discussions.
•	Provide curated mental health resources.
•	Offer dashboards for counsellors and administrators.
•	Ensure secure authentication using JWT.
The system uses an AI-based keyword detection mechanism to identify crisis-related messages and alert support systems.
________________________________________
🛠 Tech Stack
🔹 Backend
•	Python
•	Flask
•	Flask-JWT-Extended
•	Flask-SQLAlchemy
•	SQLite
•	bcrypt (Password Hashing)
🔹 Frontend
•	HTML
•	CSS
•	JavaScript
•	React (if applicable)
🔹 Database
•	SQLite (Relational Database)
🔹 Authentication
•	JWT (JSON Web Tokens)
🔹 Other Tools
•	dotenv
•	CORS
•	Git & GitHub
•	VS Code
________________________________________
⚙ Installation Steps
1️⃣ Clone the Repository
git clone https://github.com/your-username/mental-wellness-portal.git
cd mental-wellness-portal
________________________________________
2️⃣ Create Virtual Environment (Recommended)
python -m venv venv
Activate:
Windows:
venv\Scripts\activate
Mac/Linux:
source venv/bin/activate
________________________________________
3️⃣ Install Dependencies
pip install flask flask-cors flask-sqlalchemy flask-jwt-extended bcrypt python-dotenv
________________________________________
4️⃣ Create .env File
Create a file named .env in root directory:
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
________________________________________
▶ How to Run
Start the Flask server:
python app.py
Server will run at:
http://127.0.0.1:5000
________________________________________
✨ Features
🔐 Authentication
•	Secure Signup & Login
•	JWT-based authentication
•	Role-based access (Student, Counsellor, Organization)
________________________________________
📊 Mental Health Assessments
•	PHQ-9 Depression Screening
•	GAD-7 Anxiety Screening
•	Score Calculation
•	Severity Classification
•	Historical Assessment Tracking
________________________________________
🚨 Crisis Detection System
•	Detects self-harm responses in PHQ-9
•	Keyword-based crisis chatbot detection
•	Generates Crisis Alerts
•	Displays emergency helpline numbers
________________________________________
📅 Appointment Booking
•	Online & In-Person Booking
•	Auto-generated Meet Links
•	Status Tracking (Pending, Confirmed, Completed)
•	Counsellor Dashboard
________________________________________
💬 Community Forum
•	Anonymous Posting
•	Moderation System
•	Like Feature
________________________________________
📝 Complaint & Feedback System
•	Anonymous Complaint Submission
•	Tracking Number Generation
•	Feedback Collection
________________________________________
📚 Resource Centre
•	Videos
•	Articles
•	Guides
•	Stress & Anxiety Management Content
•	View Tracking
________________________________________
📊 Admin Dashboard
•	Total Users
•	Assessment Trends
•	Crisis Alert Count
•	Appointment Statistics
•	Severity Distribution Analytics
________________________________________
🚀 Future Scope
•	Integration with AI Chatbot (NLP-based)
•	Real-time crisis SMS/email alerts
•	Mobile Application (Android/iOS)
•	Video call integration using Zoom API
•	Multi-language support
•	Machine Learning for risk prediction
•	Institution-wide mental health analytics
•	Anonymous peer volunteer matching
•	Cloud deployment (AWS / Azure / GCP)
________________________________________
🔒 Security Measures
•	Password hashing using bcrypt
•	JWT-based authentication
•	Role-based authorization
•	Anonymous identity system
•	Secure API routes
________________________________________
📈 Impact
This system aims to:
•	Reduce stigma around mental health.
•	Provide early detection of depression and anxiety.
•	Improve access to counselling services.
•	Help institutions monitor student well-being.
•	Save lives through early crisis intervention.
________________________________________
🏁 Conclusion
The Mental Wellness Portal is a scalable, secure, and AI-driven solution designed to support student mental health in educational institutions. It bridges the gap between students and professional help while maintaining anonymity and security.

