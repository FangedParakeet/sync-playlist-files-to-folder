from pathlib import Path
from classes.track import Track
from classes.manifest import Manifest
from utils.logger import logger
import shutil
import os

class Playlist:
    def __init__(self, path: Path, library_dir: Path, dest_dir: Path, structure: str, mode: str, manifest: Manifest):
        self.path = path
        self.key = path.stem
        self.library_dir = library_dir
        self.dest_dir = dest_dir
        self.structure = structure
        self.mode = mode
        self.track_count = 0
        self.tracks: dict[str, str] = {}
        self.manifest = manifest
        self.copy()

    def get_tracks(self):
        return self.tracks

    def copy(self):
        logger.info(f"Copying playlist {self.key}...")
        
        tracks = self.get_tracks_from_playlist()
        logger.info(f"Found {len(tracks)} tracks")

        for raw_track in tracks:
            track = Track(raw_track, self.path.parent, self.library_dir, self.dest_dir, self.structure, self.manifest)
            track_target_path = track.get_target_path()
            track_source_path = track.get_source_path()

            if not track_target_path:
                logger.warning(f"Skipping missing track: {raw_track}")
                continue

            self.copy_track(track_source_path, track_target_path, self.mode)
            self.tracks[str(track_target_path)] = str(track_source_path)
            self.track_count += 1

        logger.info(f"Copied {self.track_count} tracks")
        
        self.write_playlist_file()
        logger.info(f"Wrote playlist file {self.key}.m3u8")

    def get_tracks_from_playlist(self):
        tracks = []
        try:
            with self.path.open("r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    tracks.append(Path(line))
        except Exception as e:
            logger.warning(f"Failed to read {self.path}: {e}")
        return tracks

    def copy_track(self, source: Path, destination: Path, mode: str):
        self.ensure_parent_dir_exists(destination)

        # If the destination already exists, we need to delete it, unless it's the same file
        if destination.exists() or destination.is_symlink():
            try:
                if destination.is_symlink():
                    existing_target = destination.resolve()
                    if existing_target == source:
                        return
                    destination.unlink()
                else:
                    if destination.stat().st_size == source.stat().st_size:
                        return
                    destination.unlink()
            except Exception:
                pass

        if mode == "copy":
            shutil.copy2(source, destination)
        else:
            try:
                os.symlink(source, destination)
            except FileExistsError:
                pass

    def write_playlist_file(self):
        file_path = self.dest_dir / f"{self.key}.m3u8"
        lines = ["#EXTM3U"]
        for target_path_str in self.tracks.keys():
            target_path = Path(target_path_str)
            try:
                rel = target_path.relative_to(self.dest_dir)
            except ValueError:
                rel = target_path.name
            lines.append(rel.as_posix())
        self.ensure_parent_dir_exists(file_path)
        file_path.write_text("\\n".join(lines) + "\\n", encoding="utf-8")

    def ensure_parent_dir_exists(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)



