## Step 1:
- Run the command `pip install -r requirements.txt` in the `Fire_Detection` directory.
## Step 2:
- Enable two-factor authentication for the Google account that will be sending alerts via email.
- Find the App passwords section in the two-factor authentication settings or through the search bar.
- Create an app password and use it as the password for the email account that will send emails (the password consists of 16 characters and does not include spaces).
- Access the config_.py file via the path `Fire_Detection\sources` and modify the `sender_email_` and `password_` variables to be the email address and the newly created password, respectively.
## Step 3:
- Run the command `python fd_app.py in Fire_Detection\sources`.
