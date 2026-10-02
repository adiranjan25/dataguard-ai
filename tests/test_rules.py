import pandas as pd

from dataguard.rules import evaluate_custom_rules


def test_custom_rules():
    df=pd.DataFrame({"id":[1,1,3],"state":["TX","XX","NY"],"amount":[2,-1,10]})
    rules=[{"type":"unique","column":"id"},{"type":"accepted_values","column":"state","values":["TX","NY"]},
           {"type":"between","column":"amount","min":0}]
    codes={x.code for x in evaluate_custom_rules(df,rules)}
    assert {"RULE_UNIQUE","RULE_ACCEPTED_VALUES","RULE_BETWEEN"} <= codes
