from typing import Dict

from app.db.enums import AvailableCourse


module_count_map: Dict[AvailableCourse, int] = {
    AvailableCourse.BEGINNER_ARABIC: 30,
    AvailableCourse.INTERMEDIATE_ARABIC: 30,
    AvailableCourse.ADVANCED_ARABIC: 30
}