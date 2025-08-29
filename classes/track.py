from pathlib import Path
import hashlib

class Track:
    def __init__(self, raw_path: Path, playlist_dir: Path, library_dir: Path, dest_dir: Path, structure: str):
        self.raw_path = raw_path
        self.source_path = self.normalize_track_path(raw_path, playlist_dir) or self.normalize_track_path(raw_path, library_dir)
        self.target_path = self.create_target_track_path(self.source_path) if self.source_path and self.source_path.exists() else None
        self.library_dir = library_dir
        self.dest_dir = dest_dir
        self.structure = structure

    def get_source_path(self):
        return self.source_path

    def get_target_path(self):
        return self.target_path

    def create_target_track_path(self, source_path: Path):
        subpath = None
        if self.structure == "mirror" and self.library_dir:
            rel = self.create_relative_path_under_library(source_path)
            if rel:
                subpath = rel
        if subpath is None:
            if self.structure == "flat":
                subpath = Path(source_path.name)
            elif self.structure == "artist":
                artist = source_path.parent.name
                subpath = Path(artist) / source_path.name
            elif self.structure == "artist_album":
                artist = source_path.parents[1].name if len(source_path.parents) >= 2 else source_path.parent.name
                album = source_path.parent.name
                subpath = Path(artist) / album / source_path.name
            else:
                subpath = Path(source_path.name)

        target_dir = self.dest_dir / subpath.parent if hasattr(subpath, "parent") else self.dest_dir
        target_path = self.deduplicate_target(target_dir, self.safe_name(subpath), source_path)

        return target_path


    def normalize_track_path(self, path: Path, basepath_hint: Path | None):
        track_path = path
        if not track_path.is_absolute():
            if basepath_hint:
                track_path = (basepath_hint / track_path).expanduser().resolve()
            else:
                track_path = track_path.expanduser().resolve()
        else:
            track_path = track_path.expanduser()
        try:
            track_path = track_path.resolve()
        except Exception:
            pass
        if track_path.exists():
            return track_path
        return None

    def deduplicate_target(self, target_dir: Path, suggested_name: str, source_path: Path) -> Path:
        candidate = target_dir / suggested_name
        if not candidate.exists():
            return candidate
        stem = candidate.stem
        suffix = "".join(candidate.suffixes) or ""
        h = hashlib.sha1(str(source_path).encode("utf-8")).hexdigest()[:8]
        new_name = f"{stem}__{h}{suffix}"
        return target_dir / new_name


    def create_relative_path_under_library(self, src_abs: Path):
        if not self.library_dir:
            return None
        try:
            return src_abs.relative_to(self.library_dir)
        except ValueError:
            return None

    def safe_name(self, path: Path) -> str:
        return path.name
