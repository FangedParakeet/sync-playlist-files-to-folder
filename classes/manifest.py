from pathlib import Path
import json
from utils.logger import logger

class Manifest:
    FILE_NAME = ".synced_files_manifest.json"

    def __init__(self, dest: Path):
        self.dest_dir = dest
        self.dest = dest / self.FILE_NAME
        self.previous_data: dict[str, str] = self.load()
        self.current_data: dict[str, str] = {}

    def get_manifest_reverse_lookup(self):
        return {v: k for k, v in self.previous_data.items()}

    def add_tracks(self, tracks: dict[str, str]):
        self.current_data.update(tracks)

    def load(self):
        file_path = self.dest
        if not file_path.exists():
            return {}
        try:
            data = json.loads(file_path.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                return {}
            return data.get("managed", {})
        except Exception:
            return {}

    def save(self):
        logger.info(f"Saving manifest...")
        data = {"managed": self.current_data}
        tmp = self.dest_dir / (self.FILE_NAME + ".tmp")
        tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
        tmp.replace(self.dest)  # atomic on the same filesystem

    def prune(self):
        logger.info(f"Deleting removed tracks from previous manifest...")
        to_remove = set(self.previous_data.keys()) - set(self.current_data.keys())
        for target_path in to_remove:
            path = Path(target_path)
            try:
                if path.exists() or path.is_symlink():
                    path.unlink()
                    # cleanup empty dirs
                    try:
                        parent = path.parent
                        while parent != self.dest_dir and parent.exists():
                            if not any(parent.iterdir()):
                                parent.rmdir()
                                parent = parent.parent
                            else:
                                break
                    except Exception:
                        pass
            except Exception as e:
                logger.warning(f"Failed to remove {path}: {e}")

