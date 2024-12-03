from dataclasses import dataclass, field
from typing import Dict


@dataclass
class GameData:
    Region: str = None
    Players: str = None
    Year: str = None
    Publisher: str = None
    Serial: str = None
    Graphics: float = None
    Sound: float = None
    Gameplay: float = None
    Overall: float = None
    CRC: str = None
    Verified: str = None
    Format: str = None
    GameName: str = None
    Console: str = None
    CanBeDownloaded: bool = False
    DownloadURL: str = None
    DownloadParams: Dict[str, str] = field(default_factory=dict)
