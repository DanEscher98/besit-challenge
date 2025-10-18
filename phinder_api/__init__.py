import os
from dotenv import load_dotenv

load_dotenv()

VT_APIKEY = os.getenv("APIKEY_VIRUSTOTAL")
if not VT_APIKEY:
    raise RuntimeError("APIKEY_VIRUSTOTAL not found in environment (.env)")

VT_APIURL = os.getenv("APIURL_VIRUSTOTAL")
