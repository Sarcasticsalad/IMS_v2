# IMS for Instagram Automation

#### 1) Create a virutal environment and activate it.
```
1) py -3.10 -m venv .venv
```
```
2) # Windows:
   .venv\Scripts\activate

   # Linux:
   source .venv/Scripts/activate
```

#### 2) Install the requirements.txt file
```
1) pip install -r requirements.txt
```

#### 3) Create the Django Project File Structure
```
1) django-admin startproject <project_name>
```

```
2) To create the apps within:
i) First enter inside your django project directory.
ii) Type: python manage.py startapp <app_name>
```

#### 4) Create a .env file and a media directory inside your django project
```
1) Properties of the .env file

SECRET_KEY=your_django_secret_key
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
INSTAGRAM_ACCESS_TOKEN=your_instagram_access_token
INSTAGRAM_PAGE_ID=your_instagram_page_id
MONGO_URI=mongodb://localhost:27017/<your_database_name>
```


