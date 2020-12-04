install Anaconda
install nodejs
install npm

// for backend
cd api
pip install -r requirements.txt
$env:FLASK_APP = "main.py"
flask run

// for frontend
cd frontend
npm i
npm start