from faq_bench.normalization import normalize_text


def test_normalization_rewrites_common_forms() -> None:
    value = normalize_text("Reset MFA for my ACCT!!!")
    assert "multi factor authentication" in value
    assert "account" in value
