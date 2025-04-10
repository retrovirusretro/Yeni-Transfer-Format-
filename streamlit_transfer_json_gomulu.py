
import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from io import BytesIO
from datetime import datetime
import math
import json
import tempfile
pip install streamlit gspread oauth2client pandas xlsxwriter


st.set_page_config(page_title="Transfer Öneri Uygulaması", layout="wide")
st.title("📦 Tam Otomatik Transfer Önerisi (Google Sheets + Gömülü Anahtar)")

# Google Sheets bağlantısı sabit
sheet_url = "https://docs.google.com/spreadsheets/d/1All5NRDzBanBReZ37krwBtpId6vBCb7x/edit?usp=sharing"

# JSON kimlik bilgileri gömülü
SERVICE_ACCOUNT_DICT = {
  "type": "service_account",
  "project_id": "streamlit-transfer",
  "private_key_id": "10be900f941b39322749a20843c63abb03368b45",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDZcxXH4Luu824U\nD6Z7FJlETqEnKr9n8o6kmeaM8OivCL5xZnBambZnOdVjTpJUVQEE4vDp5afkaBa+\n0+/QtXq2Wt6ftBLiJ/jYmoOJpntQSkkiLR9KwJs4DovxExPOcIby+cjFT6SGExND\nPa0BrtiETghxJe0LfyBQZHlQrDrW4Q8q0SC4uWcOgAixLk5LCYKXAlJWD11IsE0S\n6PIpCgPU1p+z9aOB1d5SU1R849CFX3qY1CRp2FEo5JIREP7UzAWeUDkCeyQ/YtmF\nshBXfq1FFPe8HJkxUE5YNiDXkvRZcOjqzxVpolwnryD+/cg1O2muim1GLqnH38XE\nj3fdPzYRAgMBAAECggEASDr/xazDe0pWSuil8uV1QejihBmhifxa4JdUq4WMrTO4\n2v9dm+LKYcCmvr2HQucXlxFxWCiWm/rtb0cENq5JzFAj+iW9Tg1cDktJHUzFUnbS\nkz0s005mYPkICDS/lAfx870AMXaSnoywjdnrYY88Ubp/+GHSO0rnp3ywhZkoVF7C\nGXVdvrIh6Ni8tUxFMGte1K/9sY29oxvEed2JyA8goRIRni0jG9J4Ee5krn9E7cu6\ntcqwimjTuewM+1aIVhOApCh/G0jQpoBcUygbOrSrx1FEYtSxVHo4505ESuSt7FZa\nRkyCpsB7Tcq10Mnga1M7mGhELzaB/G0GxfQAg3CJ9wKBgQD3PsEaRGSstuxehcIk\n3zO2s2X1cU8xMNw3GbDk6l0uWS/I1hkpd/s6VBzYeO/67UKIbIP94hNTU/yI6NKh\nS1rE2sB10r0UkrQ4NJGy778eMP4vbyLSZ47FnwfZmujg1V3LqcT4HASdSWevXvU8\nyp5i+mYw4eJCrg48csNd46QA1wKBgQDhJjzTqID11YIi7aHQo95py8O0tqjo2QWO\nrxeifwTJlHrPLEnobpRrabskkRFjFCazUuW9eBt4RnigcISM4rGNQI1s0KTI6Fgd\n9NaOqBSHIpCCXYhA68gdbb87QgnvwT6lmsF86UsxVq9nMEMj3XwnOqApv0qwezqQ\njsp6oi3bVwKBgQCpdiq2jUAPnUT/OGCsEwwH4og0pVgpGBsn7QTwsa3yUZDN7+jJ\nIoJgJTysJqAddbdPeEkzn1utlngVgrazdMme+WxGlY2hZzf8+hMO+QIeeGgQLPVK\nD06tJuYjgOizCatDJ3ZotBN5ltFpQwWFiD7tCkE2qewB1fjN977uQFOtewKBgQDT\nfI92YbmBMeTj2kM9MDAjQHu8rDdNQU2vEVkqEhX1I7uYDwn9gqF3pAFd/8ZNQwh3\nOU8EAmYLPGbijc50aBxPimtN405mSZk7ylgf+FIP/a+wRRtPoCqBOi1/BDFBPEwU\nUqGdK6at2bc5PmRStCGC19bKYB1QWPBSCU64ks5wUQKBgH1591F3CyUtcu5UFDXQ\nESYsFpXebReNA6QC+yDQei5WlxTJfNicVzBJMTLz+VIsNuw6Kh4kUBBSPIOJYma+\nlDd3ROx6IrpKXOLQRaLhZg2+uOgwbPIg9xN/F+Sidv5Et9dCwqkvpbnBN7CDEH/a\ntJW2u3TLEu6NQy09PfMZ3CQ9\n-----END PRIVATE KEY-----\n",
  "client_email": "streamlit-transfer-your-projec@streamlit-transfer.iam.gserviceaccount.com",
  "client_id": "117883762799746558046",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/streamlit-transfer-your-projec%40streamlit-transfer.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}

# Geçici bir json dosyası oluştur
with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".json") as tmpfile:
    json.dump(SERVICE_ACCOUNT_DICT, tmpfile)
    tmpfile.flush()
    creds = ServiceAccountCredentials.from_json_keyfile_name(tmpfile.name, ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"])
    client = gspread.authorize(creds)

# Buradan itibaren daha önceki tüm transfer algoritması kodu çalıştırılabilir (aynen öncekiyle devam edeceğiz)
st.success("✅ Kimlik doğrulama tamamlandı. Kodun geri kalan kısmına entegre edebilirim.")
