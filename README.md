# Moments - ML-Enhanced Photo Sharing Application

## ML Features
This application has been enhanced with Google Cloud Vision API to provide :
1. **Automatic Alternative Text Generation** - For accessibility
2. **Smart Image Search** - Search photos by detected objects

Demo: http://moments.helloflask.com

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- Google Cloud account with Vision API enabled
- Git

### Installation Steps

1. **Clone the repository**

   git clone https://github.com/saakshipatel/moments.git
   
   cd moments

3. **Set up Python environment**

   python -m venv venv
   source venv/bin/activate  
   # On Windows: venv\Scripts\activate

4. **Install dependencies**

   pip install -r requirements.txt
   pip install google-cloud-vision python-dotenv Pillow

5. **Configure Google Cloud Vision API**

   Go to Google Cloud Console
   Create a new project or select existing and Enable Cloud Vision API
   Download credentials JSON file
   Save as google-credentials.json in project root

6. **Set up environment variables**

   Create a .env file in project root :
   GOOGLE_APPLICATION_CREDENTIALS=google-credentials.json

7. **Initialize the database**

   flask init-app
   flask lorem  

8. **Run the application**

   flask run
   Visit: http://127.0.0.1:5000

9. **Test Credentials**

   Email : admin@helloflask.com
   Password : moments

10. **Project Structure**

   ml_service.py - Google Vision API integration
   models.py - Database models with ML fields
   blueprints/main.py - Routes including upload and search
   templates/ - HTML templates with alt text support

11. **Security Note**

   Never commit google-credentials.json or .env to version control!

11. **Commit Your Changes**

   Check what files will be committed
   git status

   # Make sure google-credentials.json is NOT in the list
   # If it appears, add to .gitignore first

   git add .
   git commit -m "Add ML-powered alt text and image search using Google Cloud Vision API"
   git push origin main
   Get your commit hash:
   bashgit log -1 --format="%H"

