"""
HealthSphere Master WHO ATC Aggregator.
"""
from .who_atc_part_01 import WHO_ATC_PART_01
from .who_atc_part_02 import WHO_ATC_PART_02
from .who_atc_part_03 import WHO_ATC_PART_03
from .who_atc_part_04 import WHO_ATC_PART_04
from .who_atc_part_05 import WHO_ATC_PART_05
from .who_atc_part_06 import WHO_ATC_PART_06
from .who_atc_part_07 import WHO_ATC_PART_07
from .who_atc_part_08 import WHO_ATC_PART_08
from .who_atc_part_09 import WHO_ATC_PART_09
from .who_atc_part_10 import WHO_ATC_PART_10
from .who_atc_part_11 import WHO_ATC_PART_11
from .who_atc_part_12 import WHO_ATC_PART_12
from .who_atc_part_13 import WHO_ATC_PART_13
from .who_atc_part_14 import WHO_ATC_PART_14
from .who_atc_part_15 import WHO_ATC_PART_15
from .who_atc_part_16 import WHO_ATC_PART_16
from .who_atc_part_17 import WHO_ATC_PART_17
from .who_atc_part_18 import WHO_ATC_PART_18
from .who_atc_part_19 import WHO_ATC_PART_19
from .who_atc_part_20 import WHO_ATC_PART_20
from .who_atc_part_21 import WHO_ATC_PART_21
from .who_atc_part_22 import WHO_ATC_PART_22
from .who_atc_part_23 import WHO_ATC_PART_23
from .who_atc_part_24 import WHO_ATC_PART_24
from .who_atc_part_25 import WHO_ATC_PART_25

WHO_ATC_FORMULARY_DATABASE = []
WHO_ATC_FORMULARY_DATABASE.extend(WHO_ATC_PART_01)
WHO_ATC_FORMULARY_DATABASE.extend(WHO_ATC_PART_02)
WHO_ATC_FORMULARY_DATABASE.extend(WHO_ATC_PART_03)
WHO_ATC_FORMULARY_DATABASE.extend(WHO_ATC_PART_04)
WHO_ATC_FORMULARY_DATABASE.extend(WHO_ATC_PART_05)
WHO_ATC_FORMULARY_DATABASE.extend(WHO_ATC_PART_06)
WHO_ATC_FORMULARY_DATABASE.extend(WHO_ATC_PART_07)
WHO_ATC_FORMULARY_DATABASE.extend(WHO_ATC_PART_08)
WHO_ATC_FORMULARY_DATABASE.extend(WHO_ATC_PART_09)
WHO_ATC_FORMULARY_DATABASE.extend(WHO_ATC_PART_10)
WHO_ATC_FORMULARY_DATABASE.extend(WHO_ATC_PART_11)
WHO_ATC_FORMULARY_DATABASE.extend(WHO_ATC_PART_12)
WHO_ATC_FORMULARY_DATABASE.extend(WHO_ATC_PART_13)
WHO_ATC_FORMULARY_DATABASE.extend(WHO_ATC_PART_14)
WHO_ATC_FORMULARY_DATABASE.extend(WHO_ATC_PART_15)
WHO_ATC_FORMULARY_DATABASE.extend(WHO_ATC_PART_16)
WHO_ATC_FORMULARY_DATABASE.extend(WHO_ATC_PART_17)
WHO_ATC_FORMULARY_DATABASE.extend(WHO_ATC_PART_18)
WHO_ATC_FORMULARY_DATABASE.extend(WHO_ATC_PART_19)
WHO_ATC_FORMULARY_DATABASE.extend(WHO_ATC_PART_20)
WHO_ATC_FORMULARY_DATABASE.extend(WHO_ATC_PART_21)
WHO_ATC_FORMULARY_DATABASE.extend(WHO_ATC_PART_22)
WHO_ATC_FORMULARY_DATABASE.extend(WHO_ATC_PART_23)
WHO_ATC_FORMULARY_DATABASE.extend(WHO_ATC_PART_24)
WHO_ATC_FORMULARY_DATABASE.extend(WHO_ATC_PART_25)

def get_atc_entry(atc_code):
    for item in WHO_ATC_FORMULARY_DATABASE:
        if item['atc_code'] == atc_code: return item
    return None
