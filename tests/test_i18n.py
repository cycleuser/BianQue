from bianque import i18n


def test_default_language_is_zh():
    assert i18n.get_language() == "zh"


def test_available_languages_count():
    langs = i18n.available_languages()
    assert len(langs) == 10
    codes = [c for c, _ in langs]
    for expected in ("zh", "en", "ja", "fr", "ru", "de", "pt", "es", "ko", "it"):
        assert expected in codes


def test_tr_english_falls_back_to_key():
    i18n.set_language("en")
    assert i18n.tr("Overview") == "Overview"


def test_tr_chinese():
    i18n.set_language("zh")
    assert i18n.tr("Overview") == "硬件总览"
    assert i18n.tr("Pass") == "通过"


def test_tr_format_args():
    i18n.set_language("zh")
    assert i18n.tr("Tested {0} / {1} keys", 3, 10) == "已测 3 / 10 键"
    i18n.set_language("en")
    assert i18n.tr("Tested {0} / {1} keys", 3, 10) == "Tested 3 / 10 keys"


def test_all_locales_translate_key_status():
    for code, _ in i18n.available_languages():
        i18n.set_language(code)
        # Every locale must translate the status keys (non-empty, non-key).
        for key in ("Pass", "Fail", "Unknown", "Skipped"):
            value = i18n.tr(key)
            assert value, f"{code} missing {key}"


def test_set_language_restored():
    i18n.set_language("zh")
