"""
AquaIntelli - Host Tunneler
Uses ngrok to create a public URL for your local AquaIntelli instance.
"""
import os
import sys
import time
from pyngrok import ngrok, conf
from dotenv import load_dotenv

# Load env vars
load_dotenv()

def start_tunnel():
    print("\n" + "="*60)
    print("   AquaIntelli - DeepCloud Tunneler")
    print("="*60)

    # 1. Get Auth Token
    token = os.getenv("NGROK_AUTH_TOKEN")
    if not token:
        print("\n[!] NGROK_AUTH_TOKEN not found in .env")
        print("    Get one at: https://dashboard.ngrok.com/get-started/your-authtoken")
        token = input("\nEnter your ngrok Authtoken: ").strip()
        if not token:
            print("Error: Authtoken is required.")
            return

    # 2. Configure ngrok
    try:
        # Use a secondary safe path to avoid non-ASCII parent folder issues
        bin_dir = "C:\\Users\\Public\\ngrok_bin"
        if not os.path.exists(bin_dir):
            try:
                os.makedirs(bin_dir)
            except:
                bin_dir = os.path.join(os.getcwd(), "ngrok_bin") # fallback
        conf.get_default().config_path = os.path.join(bin_dir, "ngrok.yml")
        conf.get_default().ngrok_path = os.path.join(bin_dir, "ngrok.exe")
        conf.get_default().auth_token = token
        # 3. Start Tunnel
        # AquaIntelli runs on port 8001 (from .env)
        port = int(os.getenv("PORT", 8001))
        
        print(f"\n[>] Opening tunnel to localhost:{port}...")
        public_url = ngrok.connect(port, "http")
        
        print("\n" + "="*60)
        print("   SUCCESS! AquaIntelli is now PUBLIC")
        print(f"   URL: {public_url}")
        print("="*60)
        print("\n   Keep this window open to maintain the connection.")
        print("   Press CTRL+C to stop hosting.")
        
        # Maintain process
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n[!] Shutting down tunnel...")
        ngrok.kill()
    except Exception as e:
        print(f"\n[!] Error starting ngrok: {e}")
        if "Authentication failed" in str(e):
            print("    Check if your Authtoken is correct.")

if __name__ == "__main__":
    start_tunnel()
