import unicodedata


class TextHelper:
    @classmethod
    def normalize_str_file_path(cls, file_path: str) -> str:
        return cls.remove_all_accent_marks(file_path).replace('.', '_')

    @staticmethod
    def remove_all_accent_marks(text: str) -> str:
        accents = (
            'COMBINING CIRCUMFLEX ACCENT',
            'CIRCUMFLEX ACCENT',
            'COMBINING ACUTE ACCENT',
            'COMBINING GRAVE ACCENT',
            'LATIN SMALL LETTER N WITH TILDE',
            'LATIN CAPITAL LETTER N WITH TILDE',
        )
        accents = set(map(unicodedata.lookup, accents))
        chars = [c for c in unicodedata.normalize('NFD', text) if c not in accents]
        return unicodedata.normalize('NFC', ''.join(chars))
