from supabase import create_client
from config.settings import base


supabase = create_client(base.SUPABASE_URL, base.SUPABASE_KEY)