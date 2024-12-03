from mongoengine import Document, StringField, FloatField, BooleanField, DictField
from dataclasses import dataclass, field
from typing import Dict


@dataclass
class GameData():
    Region: str = None
    Players: str = None
    Year: str = None
    Publisher: str = None
    Serial: str = None
    Graphics: float = None
    Sound: float = None
    Gameplay: float = None
    Format: str = None
    Version: str = None
    GameName: str = None
    Console: str = None
    CanBeDownloaded: bool = False
    DownloadURL: str = None
    DownloadParams: Dict[str, str] = field(default_factory=dict)


class GameDataDocument(Document):
    Region = StringField(required=False)
    Players = StringField(required=False)
    Year = StringField(required=False)
    Publisher = StringField(required=False)
    Serial = StringField(required=False)
    Graphics = FloatField(required=False)
    Sound = FloatField(required=False)
    Gameplay = FloatField(required=False)
    Format = StringField(required=False)
    Version = StringField(required=False)
    # Adiciona o índice único
    GameName = StringField(required=False, unique=True)
    Console = StringField(required=False)
    CanBeDownloaded = BooleanField(required=False, default=False)
    DownloadURL = StringField(required=False)
    DownloadParams = DictField(required=False)

    meta = {
        'collection': 'games',
        'indexes': [
            'GameName',  # Garantir que há um índice único em GameName
        ]
    }
