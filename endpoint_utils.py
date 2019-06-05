from ftplib import FTP
from config.config import Configuration as conf
import requests


# Function to generate folders under ftp:
def generateFtpFolders(submissionId, studyTags):
    server = conf.FTP['ftpServer']
    user = conf.FTP['ftpUser']
    passwd = conf.FTP['ftpPassword']

    with FTP(host=server) as ftp:
        ftp.login(user=user, passwd=passwd)

        # Creating folder for the submission:
        try:
            ftp.cwd('deposition/{}'.format(submissionId))
        except:
            ftp.mkd('deposition/{}'.format(submissionId))
            ftp.cwd('deposition/{}'.format(submissionId))

        # Try to create folders for all stdy tags:
        for tag in studyTags:
            try:
                ftp.mkd(tag.replace(" ", "_"))
            except:
                pass

        # Get a list of folders:
        # TODO: check if all tags were created.


def updateFileValidation(submissionId, status, message):
    url = '{}:{}/updateFileValidationStatus/submission_id/{}/status/{}/message/{}'.format(conf.serviceAppAddress, conf.serviceAppPort,
                                                                                      submissionId, status, message)
    return __submit_POST(url)

def updateFileUpload(submissionId, filename):
    url = '{}:{}/updateSubmission/{}/submission_id/{}'.format(conf.serviceAppAddress, conf.serviceAppPort, filename, submissionId)
    return __submit_POST(url)

def __submit_POST(url):
    r = requests.post(url)

    if r.ok:
        if 'successful' in r.text:
            return 0
        else:
            print(r.text)
            return 1
    print(r.text)
    return 1

