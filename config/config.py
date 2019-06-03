import os

class Configuration():

    # Path where the template files are saved:
    rootPath = os.path.dirname(os.path.realpath(__file__))
    uploadFolder = '{}/../uploadedTemplates'.format(rootPath)  #'/Users/dsuveges/Project/gwas-template-services/uploadedTemplates'

    # Credentials for the private sftp:
    FTP = {
        'ftpServer' : 'ftp.address',
        'ftpUser' : 'username',
        'ftpPassword' : 'passwd'
    }

    #
