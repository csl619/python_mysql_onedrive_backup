
# MySQL Database Backup

A script to run the backup process on a MySQL database and then upload to Microsoft OneDrive for Business.


## Installation

#### Setting up Virtual Environment
On cloning the repository, you will need to navigate to the repository folder and set up a virtual environment:
```
python3 -m venv venv **creates the virtual environment called venv**
```

Once the virtual environment is created, activate it and install the required packages via the requirements.txt file, deactivate the virtual environment once packages installed.

```
source venv/bin/activate
pip3 install -r requirements.txt
deactivate
```
#### Database Settings

The following settings need adding to your .env file in relation to your MySql Server. A sample of the .env file can be found in the repository called `sample.dotenv`
```
DB_USER=testuser                 **your MySQL username**
DB_PASSWORD='test1234'           **your MySQL password**
DB_NAME=test_db                  **your MySQL database name**
DB_BACKUP_FOLDER='test_db'       **the name of your backup folder used within OneDrive**
DB_BACKUP_FOLDER_PATH='/backups' **the folder where you want your backup files to be stored on your server**
```
#### Business OneDrive App Registration
For the system to work you will need to have registered a new application via Microsoft Azure to access the Microsoft Graph API used for linking to OneDrive. The steps for this are as follows:

* Go to the [Azure App registrations page](https://aka.ms/AppRegistrations/?referrer=https%3A%2F%2Fdev.onedrive.com).
* When prompted, sign in with your account credentials.
* Find My applications and click Add an app.
* Enter your app's name and click Create application.

Once you have set up the application you will be directed to a summary page with the essential information relating to the app. Take note of the **Application (client) ID**, **Directory (tenant) ID** and add these to the .env file as `OD_CLIENT_ID` and `OD_TENANT_ID` respectively.
    ![App Essential Page](https://imgur.com/lmM4aVu.png)

Next you need to create a client secret by clicking on `Add a certificate or secret` under **Client credentials**(shown in the image above). This will open a tab to add a new client secret, enter a description and choose an expiry from the dropdown (I recommend to set this to 24 months to reduce the need to recreate this regularly.) and click **Add**. This will submit and display the value and secret ID for the new client secret(sample shown below). Take note of the **Value** column and add this to the .env file as `OD_CLIENT_SECRET`

![App Essential Page](https://imgur.com/KoAZ02c.png)

The final step is to configure the API permissions granted for the application. Under Manage on the left menu bar click **API Permissions** and then the button for **Add a permission**.

* Choose Microsoft Graph at the top of the tab that opens up.
* Select Delegated permissions and then tick the following items:
    ```
    Files.ReadWrite
    Files.ReadWriteAll
    Sites.ReadWriteAll
    User.Read
    ```
* Click **Add permissions**

Your .env file should now include the following:
```
OD_CLIENT_ID=''       **Application (client) ID from above**
OD_CLIENT_SECRET=''   **Client secret value from above**
OD_TENANT_ID=''       **Application (client) ID from above**
OD_REDIRECT=''        **Redirect URL (can be set to localhost)**
OD_SITE_NAME=''       **Your site name within Onedrive**
```

## Running the backups

To run the process you just need to call the following command from your terminal:
```
bash database_backup.sh
```

Or this can be set up as a Cron job to run at your desired interval.
