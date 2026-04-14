"""Run the Streamlit app locally for testing."""
import subprocess
import sys
import os

def main():
    """Run Streamlit app locally."""
    print("🚀 Starting Mutual Fund FAQ Assistant...")
    print("=" * 50)
    
    # Check if .env exists
    if not os.path.exists(".env"):
        print("⚠️  Warning: .env file not found. Make sure to set up your environment variables.")
        print("   Copy .env.example to .env and fill in your API keys.")
        print()
    
    # Run Streamlit
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "streamlit_app.py",
            "--server.port=8501",
            "--server.address=localhost",
            "--browser.gatherUsageStats=false"
        ], check=True)
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting Streamlit: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
