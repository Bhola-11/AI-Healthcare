"""
HealthSphere Master Clinical DDI Matrix Aggregator.
"""
from .clinical_ddi_part_01 import CLINICAL_DDI_PART_01
from .clinical_ddi_part_02 import CLINICAL_DDI_PART_02
from .clinical_ddi_part_03 import CLINICAL_DDI_PART_03
from .clinical_ddi_part_04 import CLINICAL_DDI_PART_04
from .clinical_ddi_part_05 import CLINICAL_DDI_PART_05
from .clinical_ddi_part_06 import CLINICAL_DDI_PART_06
from .clinical_ddi_part_07 import CLINICAL_DDI_PART_07
from .clinical_ddi_part_08 import CLINICAL_DDI_PART_08
from .clinical_ddi_part_09 import CLINICAL_DDI_PART_09
from .clinical_ddi_part_10 import CLINICAL_DDI_PART_10
from .clinical_ddi_part_11 import CLINICAL_DDI_PART_11
from .clinical_ddi_part_12 import CLINICAL_DDI_PART_12
from .clinical_ddi_part_13 import CLINICAL_DDI_PART_13
from .clinical_ddi_part_14 import CLINICAL_DDI_PART_14
from .clinical_ddi_part_15 import CLINICAL_DDI_PART_15
from .clinical_ddi_part_16 import CLINICAL_DDI_PART_16
from .clinical_ddi_part_17 import CLINICAL_DDI_PART_17
from .clinical_ddi_part_18 import CLINICAL_DDI_PART_18
from .clinical_ddi_part_19 import CLINICAL_DDI_PART_19
from .clinical_ddi_part_20 import CLINICAL_DDI_PART_20
from .clinical_ddi_part_21 import CLINICAL_DDI_PART_21
from .clinical_ddi_part_22 import CLINICAL_DDI_PART_22
from .clinical_ddi_part_23 import CLINICAL_DDI_PART_23
from .clinical_ddi_part_24 import CLINICAL_DDI_PART_24
from .clinical_ddi_part_25 import CLINICAL_DDI_PART_25

CLINICAL_DDI_RULES_MATRIX = []
CLINICAL_DDI_RULES_MATRIX.extend(CLINICAL_DDI_PART_01)
CLINICAL_DDI_RULES_MATRIX.extend(CLINICAL_DDI_PART_02)
CLINICAL_DDI_RULES_MATRIX.extend(CLINICAL_DDI_PART_03)
CLINICAL_DDI_RULES_MATRIX.extend(CLINICAL_DDI_PART_04)
CLINICAL_DDI_RULES_MATRIX.extend(CLINICAL_DDI_PART_05)
CLINICAL_DDI_RULES_MATRIX.extend(CLINICAL_DDI_PART_06)
CLINICAL_DDI_RULES_MATRIX.extend(CLINICAL_DDI_PART_07)
CLINICAL_DDI_RULES_MATRIX.extend(CLINICAL_DDI_PART_08)
CLINICAL_DDI_RULES_MATRIX.extend(CLINICAL_DDI_PART_09)
CLINICAL_DDI_RULES_MATRIX.extend(CLINICAL_DDI_PART_10)
CLINICAL_DDI_RULES_MATRIX.extend(CLINICAL_DDI_PART_11)
CLINICAL_DDI_RULES_MATRIX.extend(CLINICAL_DDI_PART_12)
CLINICAL_DDI_RULES_MATRIX.extend(CLINICAL_DDI_PART_13)
CLINICAL_DDI_RULES_MATRIX.extend(CLINICAL_DDI_PART_14)
CLINICAL_DDI_RULES_MATRIX.extend(CLINICAL_DDI_PART_15)
CLINICAL_DDI_RULES_MATRIX.extend(CLINICAL_DDI_PART_16)
CLINICAL_DDI_RULES_MATRIX.extend(CLINICAL_DDI_PART_17)
CLINICAL_DDI_RULES_MATRIX.extend(CLINICAL_DDI_PART_18)
CLINICAL_DDI_RULES_MATRIX.extend(CLINICAL_DDI_PART_19)
CLINICAL_DDI_RULES_MATRIX.extend(CLINICAL_DDI_PART_20)
CLINICAL_DDI_RULES_MATRIX.extend(CLINICAL_DDI_PART_21)
CLINICAL_DDI_RULES_MATRIX.extend(CLINICAL_DDI_PART_22)
CLINICAL_DDI_RULES_MATRIX.extend(CLINICAL_DDI_PART_23)
CLINICAL_DDI_RULES_MATRIX.extend(CLINICAL_DDI_PART_24)
CLINICAL_DDI_RULES_MATRIX.extend(CLINICAL_DDI_PART_25)

def check_ddi_interaction(drug_a, drug_b):
    results = []
    for rule in CLINICAL_DDI_RULES_MATRIX:
        if (rule['drug_a'].lower() == drug_a.lower() and rule['drug_b'].lower() == drug_b.lower()) or \
           (rule['drug_a'].lower() == drug_b.lower() and rule['drug_b'].lower() == drug_a.lower()):
            results.append(rule)
    return results
