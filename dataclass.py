from dataclasses import dataclass, field
from typing import List, Dict, Optional

@dataclass
class CharacterImage:
    id: int
    url: str

@dataclass
class Item:
    id: int
    unique_id: str
    name: str
    description: str
    item_type: str
    strength_bonus: int
    defense_bonus: int
    health_bonus: int
    dodge_bonus: float
    critical_chance_bonus: float
    agility_bonus: int
    aura: Optional[str]
    no_bg_image_url: Optional[str]
    base_image_url: Optional[str]
