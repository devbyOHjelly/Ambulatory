from __future__ import annotations

from dataclasses import dataclass
from typing import List

import pandas as pd


@dataclass
class Facility:
    name: str
    kind: str
    owner: str
    lat: float
    lon: float
    service_line: str
    volume: int
    npi: str | None = None
    taxonomy: str | None = None
    zip5: str | None = None  # 5-digit ZIP / ZCTA for leakage joins


# Used when nppes_florida_facilities.csv has not been built yet
FACILITIES_FALLBACK: List[Facility] = [
    Facility("Miami Ambulatory Hub", "Ambulatory", "Orlando Health", 25.7617, -80.1918, "Cardiology", 8600),
    Facility("Orlando Care Center", "Ambulatory", "Orlando Health", 28.5383, -81.3792, "Primary Care", 7200),
    Facility("Tampa Bay Clinic", "Ambulatory", "Orlando Health", 27.9506, -82.4572, "Urgent Care", 6400),
    Facility("Jacksonville Medical", "Inpatient", "Orlando Health", 30.3322, -81.6557, "Cardiology", 9100),
    Facility("Broward Diagnostics", "Lab", "Orlando Health", 26.1224, -80.1373, "Diagnostics", 4900),
    Facility("Miami Regional Health", "Inpatient", "Competitor", 25.7743, -80.1937, "Cardiology", 12500),
    Facility("Central Florida Hospital", "Inpatient", "Competitor", 28.5410, -81.3818, "Primary Care", 11400),
    Facility("Gulf Coast Med Group", "Ambulatory", "Competitor", 27.9480, -82.4590, "Urgent Care", 9300),
    Facility("North Florida Health", "Inpatient", "Competitor", 30.3270, -81.6600, "Cardiology", 11800),
    Facility("Quest Diagnostics FL", "Lab", "Competitor", 26.1200, -80.1400, "Diagnostics", 6100),
]

facilities: List[Facility] = FACILITIES_FALLBACK


flows = pd.DataFrame(
    [
        {"origin": "Palm Beach", "type": "Inbound", "service_line": "Cardiology", "patients": 510, "lat": 26.7153, "lon": -80.0534},
        {"origin": "Kissimmee", "type": "Inbound", "service_line": "Primary Care", "patients": 420, "lat": 28.2919, "lon": -81.4076},
        {"origin": "St. Petersburg", "type": "Inbound", "service_line": "Urgent Care", "patients": 390, "lat": 27.7676, "lon": -82.6403},
        {"origin": "Miami Core", "type": "Outbound", "service_line": "Cardiology", "patients": 310, "lat": 25.7617, "lon": -80.1918},
        {"origin": "Orlando Core", "type": "Outbound", "service_line": "Primary Care", "patients": 280, "lat": 28.5383, "lon": -81.3792},
        {"origin": "Tampa Core", "type": "Outbound", "service_line": "Urgent Care", "patients": 260, "lat": 27.9506, "lon": -82.4572},
    ]
)


opportunities = pd.DataFrame(
    [
        {
            "zone": "South Florida Expansion Zone",
            "score": 90.4,
            "rationale": "Strong leakage recovery potential and high ambulatory demand density.",
        },
        {
            "zone": "I-4 Corridor Growth Zone",
            "score": 86.7,
            "rationale": "Coverage gap between Orlando/Tampa with high service-line demand.",
        },
        {
            "zone": "Northeast Florida Access Zone",
            "score": 82.9,
            "rationale": "Competitive pressure is high while access convenience remains limited.",
        },
    ]
)
