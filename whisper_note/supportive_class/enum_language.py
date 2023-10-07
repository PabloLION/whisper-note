from enum import Enum
from typing import cast

import deepl


class Language(Enum):
    ES = "Spanish"
    EN = "English"
    EN_US = "American_English"
    EN_GB = "British_English"
    CN = "Chinese_Simplified"
    # Aliases
    ZH_CN = "Chinese_Simplified"
    ZH_TW = "Chinese_Traditional"
    ZH = "Chinese_Simplified"

    def standardize(self) -> "Language":
        return {
            Language.ZH_CN: Language.CN,
            Language.ZH_TW: Language.CN,
            Language.ZH: Language.CN,
        }.get(self, self)

    def to_deepl_language(self) -> deepl.Language:
        return cast(
            deepl.Language,
            {
                Language.ES: deepl.Language.SPANISH,
                Language.EN: deepl.Language.ENGLISH,
                Language.EN_US: deepl.Language.ENGLISH_AMERICAN,
                Language.EN_GB: deepl.Language.ENGLISH_BRITISH,
                Language.CN: deepl.Language.CHINESE,
            }[self.standardize()],
        )
