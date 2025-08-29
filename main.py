import argparse

def main():
    ap = argparse.ArgumentParser(description="Build a Resilio-syncable folder from one or more .m3u playlists using symlinks (or copies).")
    ap.add_argument("--m3u", action="append", required=True, help="Path to a .m3u/.m3u8 playlist (can be repeated).")
    ap.add_argument("--dest", required=True, help="Destination sync folder to populate (Resilio should watch this).")
    ap.add_argument("--library-root", default=None, help="Path to your Music library root (e.g., ~/Music/Music/Media/Music) to mirror subfolders under dest.")
    ap.add_argument("--structure", choices=["flat", "artist", "artist_album", "mirror"], default="artist_album",
                    help="How to arrange files under dest. 'mirror' tries to mirror paths under --library-root.")
    ap.add_argument("--mode", choices=["symlink", "copy"], default="symlink", help="Create symlinks (default) or copy files.")
    ap.add_argument("--prune", action="store_true", help="Remove files in dest that are no longer in the provided playlists (only files previously created by this script).")
    ap.add_argument("--write-m3u", action="store_true", help="Also write a single combined playlist .m3u8 into dest.")
    ap.add_argument("--per-playlist", action="store_true", help="Write separate .m3u8 files per input playlist into dest.")
    ap.add_argument("--m3u-dir", default=None, help="Optional subfolder (under --dest) to place generated .m3u8 files (e.g., 'Playlists').")
    args = ap.parse_args()

if __name__ == "__main__":
    main()