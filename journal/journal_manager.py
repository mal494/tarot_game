import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from journal.journal_entry import JournalEntry


class JournalCorruptError(Exception):
    """Raised when the journal file cannot be parsed as a list of entries."""

    def __init__(self, path: Path, backup_path: Optional[Path] = None, message: str = ""):
        self.path = path
        self.backup_path = backup_path
        super().__init__(
            message
            or f"Journal file is corrupted and was moved to a backup: {backup_path or path}"
        )


class JournalManager:
    """
    Handles saving, loading, deleting, and resetting tarot journal entries.
    Entries are stored as a JSON list.
    """

    def __init__(self, path: str):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self._write([])

    def _backup_corrupt_file(self) -> Path:
        backup_path = self.path.with_name(f"{self.path.stem}.corrupt.bak{self.path.suffix}")
        counter = 1
        while backup_path.exists():
            backup_path = self.path.with_name(
                f"{self.path.stem}.corrupt.{counter}.bak{self.path.suffix}"
            )
            counter += 1
        self.path.replace(backup_path)
        return backup_path

    def _read(self) -> List[Dict[str, Any]]:
        try:
            with self.path.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except json.JSONDecodeError as exc:
            backup_path = self._backup_corrupt_file()
            raise JournalCorruptError(
                self.path,
                backup_path,
                f"Journal file contains invalid JSON and was moved to {backup_path.name}.",
            ) from exc

        if not isinstance(data, list):
            backup_path = self._backup_corrupt_file()
            raise JournalCorruptError(
                self.path,
                backup_path,
                f"Journal file must contain a JSON list and was moved to {backup_path.name}.",
            )

        return data

    def _write(self, data: List[Dict[str, Any]]):
        tmp_path = self.path.with_suffix(f"{self.path.suffix}.tmp")
        with tmp_path.open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=2, ensure_ascii=False)
        tmp_path.replace(self.path)

    def load_entries(self) -> List[Dict[str, Any]]:
        return sorted(self._read(), key=lambda entry: entry.get("date", ""), reverse=True)

    def save_entry(
        self,
        intention: str,
        spread_type: str,
        cards: List[Dict[str, Any]],
        interpretation: str,
        date: Optional[str] = None,
    ) -> Dict[str, Any]:
        entry_kwargs = {
            "intention": intention,
            "spread_type": spread_type,
            "cards": cards,
            "interpretation": interpretation,
        }
        if date is not None:
            entry_kwargs["date"] = date

        entry = JournalEntry(**entry_kwargs).to_dict()

        entries = self._read()
        entries.append(entry)
        self._write(entries)
        return entry

    def update_entry(
        self,
        entry_id: str,
        intention: str,
        spread_type: str,
        cards: List[Dict[str, Any]],
        interpretation: str,
    ) -> Dict[str, Any]:
        entries = self._read()
        for index, entry in enumerate(entries):
            if entry.get("id") != entry_id:
                continue

            updated = {
                **entry,
                "intention": intention,
                "spread_type": spread_type,
                "cards": cards,
                "interpretation": interpretation,
            }
            entries[index] = updated
            self._write(entries)
            return updated

        raise KeyError(f"Journal entry not found: {entry_id}")

    def delete_entry(self, entry_id: str):
        self._write([entry for entry in self._read() if entry.get("id") != entry_id])

    def reset_journal(self):
        self._write([])
