import os
PROJECT_ROOT = project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

AZURE_TIME_LAPSE_URLS = f'{PROJECT_ROOT}/time_lapse/azure_urls/'
AZURE_CONFIG=f'{PROJECT_ROOT}/azure_blob_wblms_config.ini'