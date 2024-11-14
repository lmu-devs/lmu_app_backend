from babel.numbers import format_decimal

def abbreviate_number(number, locale='de_DE'):
    """
    Abbreviate a number using abbreviations with Babel (default: German). Use en_US for English.
    """
    if number >= 1_000_000_000:
        return f"{format_decimal(number / 1_000_000_000, locale=locale):.1f} Mrd"
    elif number >= 1_000_000:
        return f"{format_decimal(number / 1_000_000, locale=locale):.1f} Mio"
    elif number >= 1_000:
        return f"{format_decimal(number / 1_000, locale=locale):.1f} Tsd"
    else:
        return format_decimal(number, locale=locale)

