from classes.manifest import Manifest
from classes.playlist import Playlist
from pathlib import Path

class SyncService:
    def __init__(self, manifest: Manifest, playlist_dir: Path, dest: Path, library_dir: Path, structure: str, mode: str, prune: bool):
        self.manifest = manifest
        self.playlist_dir = playlist_dir
        self.dest = dest
        self.library_dir = library_dir
        self.structure = structure
        self.mode = mode
        self.prune = prune

    def sync(self):
        playlist_files = self.get_playlist_files()
        for playlist_file in playlist_files:
            self.manifest.add_tracks(playlist_file.get_tracks())

        if self.prune:
            self.manifest.prune()

    def get_playlist_files(self):
        playlist_files = []
        for playlist_filename in self.playlist_dir.glob("*.m3u"):
            playlist_files.append(Playlist(playlist_filename, self.library_dir, self.dest, self.structure, self.mode))
        return playlist_files