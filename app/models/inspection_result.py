from dataclasses import dataclass, field


@dataclass
class InspectionResult:
    item: str = field(init=False)
    value: str = field(init=False)
    unit: str = field(init=False)
