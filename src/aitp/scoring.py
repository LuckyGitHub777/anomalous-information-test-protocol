from __future__ import annotations

import math
from typing import Iterable


def _require_string_ids(record: dict) -> None:
    for key in ("true_target_id","judge_rank_1"):
        if not isinstance(record.get(key),str) or not record.get(key):
            raise ValueError(f"{key} must be a non-empty string")


def exact_rank1_summary(records: Iterable[dict]) -> dict:
    valid=[r for r in records if r.get("protocol_status")=="VALID"]
    if not valid: raise ValueError("no audited VALID trials")
    for r in valid: _require_string_ids(r)
    counts={int(r["candidate_count"]) for r in valid}
    if len(counts)!=1: raise ValueError("primary exact rank-1 scorer requires constant candidate_count")
    k=counts.pop(); n=len(valid); hits=sum(r["true_target_id"]==r["judge_rank_1"] for r in valid); p0=1.0/k
    p_tail=sum(math.comb(n,x)*(p0**x)*((1-p0)**(n-x)) for x in range(hits,n+1))
    return {"valid_trials":n,"rank1_hits":hits,"observed_hit_rate":hits/n,"null_hit_rate":p0,"exact_one_sided_binomial_p":p_tail,"interpretation_boundary":"Statistical unusualness alone does not establish source identity or mechanism."}


def _fisher_table_probability(a:int,b:int,c:int,d:int)->float:
    n=a+b+c+d; r1=a+b; c1=a+c
    return math.comb(c1,a)*math.comb(n-c1,r1-a)/math.comb(n,r1)


def fisher_exact_two_sided(a:int,b:int,c:int,d:int)->float:
    n=a+b+c+d; r1=a+b; c1=a+c; lo=max(0,r1-(n-c1)); hi=min(r1,c1); p_obs=_fisher_table_probability(a,b,c,d); total=0.0
    for x in range(lo,hi+1):
        p=_fisher_table_probability(x,r1-x,c1-x,n-r1-c1+x)
        if p<=p_obs+1e-15: total+=p
    return min(1.0,total)


def compare_rank1_conditions(records: Iterable[dict],condition_a:str,condition_b:str)->dict:
    valid=[r for r in records if r.get("protocol_status")=="VALID" and r.get("condition") in {condition_a,condition_b}]
    for r in valid: _require_string_ids(r)
    rows={}
    for cond in [condition_a,condition_b]:
        subset=[r for r in valid if r.get("condition")==cond]
        if not subset: raise ValueError(f"no valid trials for condition {cond}")
        hits=sum(r["true_target_id"]==r["judge_rank_1"] for r in subset); rows[cond]=(hits,len(subset)-hits,len(subset))
    a,b,na=rows[condition_a]; c,d,nb=rows[condition_b]
    return {"condition_a":condition_a,"condition_b":condition_b,"a_hits":a,"a_misses":b,"b_hits":c,"b_misses":d,"a_hit_rate":a/na,"b_hit_rate":c/nb,"fisher_exact_two_sided_p":fisher_exact_two_sided(a,b,c,d),"interpretation_boundary":"Condition differences do not identify a mechanism or source. Use only if this comparison was preregistered."}
