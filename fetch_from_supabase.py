# scripts/fetch_from_supabase.py

import os
import json
from supabase import create_client

# Get environment variables from GitHub Secrets
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
TARGET_USER_ID = os.getenv("USER_ID")  # <-- Add this in GitHub Secrets

# Basic validation
if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY or not TARGET_USER_ID:
    raise ValueError("Missing Supabase credentials or target user ID")

# Create Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

# Fetch session data for Bigbasket for the given user
response = (
    supabase
    .table("user_sessions")
    .select("session_data")
    .eq("store", "Bigbasket")
    .eq("user_id", TARGET_USER_ID)
    .limit(1)
    .execute()
)

# Validate response
if not response.data or not response.data[0]["session_data"]:
    raise ValueError("No session_data found for Bigbasket for the given user")

# Save to bb.json
with open("bb.json", "w") as f:
    json.dump(response.data[0]["session_data"], f)

print("✅ Saved bb.json")
