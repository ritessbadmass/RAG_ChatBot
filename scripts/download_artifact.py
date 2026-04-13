"""Script to download vector store artifact from GitHub Actions."""
import argparse
import logging
import os
import sys
import zipfile
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import requests

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def download_artifact(run_id: str, token: str, output_dir: str = "./data"):
    """
    Download vector store artifact from GitHub Actions.
    
    Args:
        run_id: GitHub Actions run ID
        token: GitHub Personal Access Token
        output_dir: Directory to extract artifact
    """
    # GitHub API endpoint
    repo = os.getenv('GITHUB_REPOSITORY', 'your-username/your-repo')
    api_url = f"https://api.github.com/repos/{repo}/actions/runs/{run_id}/artifacts"
    
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    logger.info(f"Fetching artifacts for run {run_id}...")
    
    # Get artifacts list
    response = requests.get(api_url, headers=headers)
    response.raise_for_status()
    
    artifacts = response.json().get('artifacts', [])
    
    # Find vector store artifact
    vector_store_artifact = None
    for artifact in artifacts:
        if artifact['name'].startswith('vector-store-'):
            vector_store_artifact = artifact
            break
    
    if not vector_store_artifact:
        logger.error("Vector store artifact not found!")
        return False
    
    logger.info(f"Found artifact: {vector_store_artifact['name']}")
    
    # Download artifact
    download_url = vector_store_artifact['archive_download_url']
    logger.info("Downloading artifact...")
    
    response = requests.get(download_url, headers=headers)
    response.raise_for_status()
    
    # Save zip file
    zip_path = Path(output_dir) / "vector_store.zip"
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(zip_path, 'wb') as f:
        f.write(response.content)
    
    logger.info(f"Downloaded to {zip_path}")
    
    # Extract
    vector_store_dir = Path(output_dir) / "vector_store"
    vector_store_dir.mkdir(parents=True, exist_ok=True)
    
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(vector_store_dir)
    
    logger.info(f"Extracted to {vector_store_dir}")
    
    # Clean up zip
    zip_path.unlink()
    
    logger.info("Done! Vector store ready to use.")
    return True


def main():
    parser = argparse.ArgumentParser(description="Download vector store from GitHub Actions")
    parser.add_argument("run_id", help="GitHub Actions run ID")
    parser.add_argument("--token", help="GitHub Personal Access Token", 
                       default=os.getenv('GITHUB_TOKEN'))
    parser.add_argument("--output", help="Output directory", default="./data")
    
    args = parser.parse_args()
    
    if not args.token:
        logger.error("GitHub token required. Set GITHUB_TOKEN environment variable or use --token")
        return 1
    
    success = download_artifact(args.run_id, args.token, args.output)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
