from dotenv import load_dotenv
import os

import supabase

load_dotenv()

UrlApi = os.getenv("IB_URLAPI")
ApiKey = os.getenv("IB_APIKEY")


ApiSupebase: supabase.Client = supabase.create_client(supabase_url=UrlApi, supabase_key=ApiKey)