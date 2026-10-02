import pytest
from dataguard.sources import _safe_ident
def test_safe_ident():
    assert _safe_ident("public.customers") == "public.customers"
    with pytest.raises(ValueError):
        _safe_ident("customers; drop table x")
