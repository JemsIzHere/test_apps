from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class Material:
    name: str
    quantity: int
    link: str
    price: float
    prerequisites: list["Material"] = field(default_factory=list)

    def is_purchasable(self) -> bool:
        return self.price > 0

    def is_quest_reward(self) -> bool:
        return self.price == 0