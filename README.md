
# MySQL Database Backup

A script to run the backup process on a MySQL database and then upload to Microsoft OneDrive for Business.


## Installation

#### Setting up Virtual Environment
On cloning the repository, you will need to navigate to the repository folder and set up a virtual environment:

    python3 -m venv venv **creates the virtual environment called venv**

Once the virtual environment is created, activate it and install the required packages via the requirements.txt file, deactivate the virtual environment once packages installed.

    source venv/bin/activate

    pip3 install -r requirements.txt

    deactivate

#### Database Settings

 The following settings need adding to your .env file to connect to your MySql Server. A sample of the .env file can be found in the repository called `sample.dotenv`

    `DB_USER` **your MySQL username**
    `DB_PASSWORD` **your MySQL password**
    `DB_NAME` **your MySQL database name**
    `DB_BACKUP_FOLDER` **the name of your backup folder used within OneDrive**
#### Business OneDrive App Registration
For the system to work you will need to have access to a Office365 Azure Active Directory and register a new application to access the Microsoft Graph API used for linking to OneDrive. The steps for this are as follows:

* Sign in to the [Azure Portal](https://portal.azure.com/#home)

* On the top bar, click on menu icon (top left corner) and choose Azure Active Directory.

* Once the page loads select `App Registrations` from the left menu bar.
    ![App Registration](https://imgur.com/AnpHfUO)

```
 `DB_USER` **your MySQL username**
 `DB_PASSWORD` **your MySQL password**
 `DB_NAME` **your MySQL database name**
 `DB_BACKUP_FOLDER` **the name of your backup folder used within OneDrive**
```

## Environment Variables

To run this project, you will need to add the following environment variables to your .env file. A sample copy of the .env file can be found in the repository called sample.dotenv.


###### ONEDRIVE SETTINGS
    `OD_CLIENT_ID`
    `OD_CLIENT_SECRET`
    `OD_TENANT_ID`
    `OD_REDIRECT`
    `OD_SITE_URL`
    `OD_DRIVE_ID`

##### DISCORD WEBHOOK DETAILS
    `WH_USER`
    `BACKUP_WH`
