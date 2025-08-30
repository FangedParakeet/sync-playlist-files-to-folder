import argparse
import os
import sys
from dotenv import load_dotenv
from services.sync_service import SyncService
from classes.manifest import Manifest
from utils.logger import logger
from pathlib import Path

# Load environment variables from .env file
load_dotenv()

def main():
    ap = argparse.ArgumentParser(description="Build a Resilio-syncable folder from one or more .m3u playlists using symlinks (or copies).")
    ap.add_argument("--playlist-dir", default=os.environ.get("PLAYLIST_DIR"), help="Path to directory containing .m3u/.m3u8 playlists to copy.")
    ap.add_argument("--dest", default=os.environ.get("SYNC_DESTINATION_DIR"), help="Destination sync folder to populate (Resilio should watch this).")
    ap.add_argument("--library-dir", default=os.environ.get("LIBRARY_DIR"), help="Path to your Music library root (e.g., ~/Music/Music/Media/Music) to mirror subfolders under dest.")
    ap.add_argument("--structure", choices=["artist_album", "mirror"], default="artist_album",
                    help="How to arrange files under dest. 'mirror' tries to mirror paths under --library-dir.")
    ap.add_argument("--mode", choices=["symlink", "copy"], default="symlink", help="Create symlinks (default) or copy files.")
    ap.add_argument("--prune", action="store_true", default=True, help="Remove files in dest that are no longer in the provided playlists (only files previously created by this script).")
    args = ap.parse_args()

    logger.info(f"Starting playlist sync with args: {args}")

    # Validate required arguments
    if not args.playlist_dir:
        logger.error("--playlist-dir is required. Set PLAYLIST_DIR environment variable or provide --playlist-dir argument.")
        sys.exit(1)
    
    if not args.dest:
        logger.error("--dest is required. Set SYNC_DESTINATION_DIR environment variable or provide --dest argument.")
        sys.exit(1)
    
    if not args.library_dir:
        logger.error("--library-dir is required. Set LIBRARY_DIR environment variable or provide --library-dir argument.")
        sys.exit(1)

    playlist_dir = Path(args.playlist_dir).expanduser().resolve()
    dest = Path(args.dest).expanduser().resolve()
    library_dir = Path(args.library_dir).expanduser().resolve()

    # Validate that directories exist
    if not playlist_dir.exists():
        logger.error(f"Playlist directory does not exist: {playlist_dir}")
        sys.exit(1)
    
    if not library_dir.exists():
        logger.error(f"Library directory does not exist: {library_dir}")
        sys.exit(1)

    manifest = Manifest(dest)
    sync_service = SyncService(manifest, playlist_dir, dest, library_dir, args.structure, args.mode, args.prune)
    sync_service.sync()
    
    logger.info("Playlist sync complete")

if __name__ == "__main__":
    main()