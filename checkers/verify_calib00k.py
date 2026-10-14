#!/usr/bin/env python3
"""verify_calib00k.py — BUILD_PLAN v4.2 (minimum coin dose, calib-00k). stdlib only. Claude, 2026-10-14.
Usage: python3 -I verify_calib00k.py grid.csv [--out VERIFY.md]
grid.csv columns: agent (jev|ant), noise (jev coin eps 0.02/0.05/0.10; ant blank), variant, ttl, seed, frac_short_last50,
                  invalid, api_error_rate, model_id, n_depart_calls (Jev calls), n_coin (coin decisions).
Rules (v4.2 §5-6):
 Validity: ants Z6 medians A2.5>=0.85, B2.5>=0.85, B3<=0.25; Jev seeds 600-611 exactly once per arm-cell (B2.5, B3);
           <=2 invalid per arm; one model_id; coin rate n_coin/(n_coin+n_depart_calls) pooled per arm within [0.8, 1.2] x eps.
 Invalid run counts against: B2.5 invalid = not switched; B3 invalid = not locked.
 Per dose: S = B2.5 runs >= 0.8 (switched); L = B3 runs <= 0.3 (locked).
   SPLIT  = S >= 7 and L >= 10   (memory decides: short memory switches, long memory stays)
   FROZEN = S <= 3 and L >= 10   (too little exploration)
   NOISY  = L <= 9               (exploration breaks the long-memory lock)
   else PARTIAL.
 Minimum dose = lowest eps with SPLIT.
 Explorer-model test (pre-registered, D=36): S 90% intervals 0.02: 1-6 · 0.05: 4-10 · 0.10: 8-12.
   MODEL HOLDS if all 3 inside; MODEL REFUTED if >=2 outside; else MODEL MIXED.
Tested 2026-10-14 on synthetic grids: model-true -> min 0.05 / HOLDS; frozen -> no split / REFUTED; lock broken -> NOISY.
"""
import csv, sys, statistics as st
PRED={0.02:(1,6),0.05:(4,10),0.10:(8,12)}
def fl(x):
    try: return float(x)
    except: return 0.0
def main():
    a=sys.argv[1:]; path=a[0]; out=a[a.index('--out')+1] if '--out' in a else None
    rows=list(csv.DictReader(open(path,newline='')))
    L=[]; p=L.append; p("# calib-00k — verdict (verify_calib00k.py, v4.2 rules)\n")
    inv=lambda r: r.get('invalid') in ('True','true','1') or fl(r.get('api_error_rate'))>0.10
    def cell(ag,nz,v,t): return [r for r in rows if r.get('agent')==ag and (nz is None or abs(fl(r.get('noise'))-nz)<1e-9) and r['variant']==v and abs(fl(r['ttl'])-t)<1e-9]
    am={c:(st.median([fl(r['frac_short_last50']) for r in cell('ant',None,*c)]) if cell('ant',None,*c) else None) for c in [('A',2.5),('B',2.5),('B',3)]}
    ants_ok=None not in am.values() and am[('A',2.5)]>=0.85 and am[('B',2.5)]>=0.85 and am[('B',3)]<=0.25
    p(f"Ants Z6: A2.5 {am[('A',2.5)]} · B2.5 {am[('B',2.5)]} · B3 {am[('B',3)]} → {'OK' if ants_ok else 'FAIL'}")
    jev=[r for r in rows if r.get('agent')=='jev']
    models=sorted(set(r.get('model_id') for r in jev))
    bad=sorted(set(r['seed'] for r in jev if not 600<=int(fl(r['seed']))<=611))
    if bad: p(f"**Seeds outside 600–611: {bad}**")
    if len(models)!=1: p(f"**More than one model_id: {models}**")
    S_ok=sorted(range(600,612)); valid=ants_ok and not bad and len(models)==1
    res={}; minimum=None
    p("\n| eps | coin rate | S switched (B2.5) | L locked (B3) | invalid | dose verdict | model 90% S | in? |\n|---|---|---|---|---|---|---|---|")
    for e in (0.02,0.05,0.10):
        B25=cell('jev',e,'B',2.5); B3=cell('jev',e,'B',3)
        seeds_ok=sorted(int(fl(r['seed'])) for r in B25)==S_ok and sorted(int(fl(r['seed'])) for r in B3)==S_ok
        ni=sum(inv(r) for r in B25+B3)
        nc=sum(fl(r.get('n_coin')) for r in B25+B3); nj=sum(fl(r.get('n_depart_calls')) for r in B25+B3)
        rate=nc/(nc+nj) if nc+nj else 0.0; rate_ok=0.8*e<=rate<=1.2*e
        S=sum(1 for r in B25 if not inv(r) and fl(r['frac_short_last50'])>=0.8)
        Lk=sum(1 for r in B3 if not inv(r) and fl(r['frac_short_last50'])<=0.3)
        ok=seeds_ok and ni<=2 and rate_ok
        if not ok: valid=False
        v='SPLIT' if (S>=7 and Lk>=10) else ('FROZEN' if (S<=3 and Lk>=10) else ('NOISY' if Lk<=9 else 'PARTIAL'))
        lo,hi=PRED[e]; inside=lo<=S<=hi
        res[e]=(v,inside)
        if v=='SPLIT' and minimum is None: minimum=e
        p(f"| {e:.2f} | {rate:.3f}{'' if rate_ok else ' **OUT**'} | {S}/12 | {Lk}/12 | {ni}{'' if seeds_ok else ' **SEEDS**'} | {v} | {lo}–{hi} | {'✓' if inside else '✗'} |")
    if not valid:
        p("\n## Verdict\n\n**UNINTERPRETABLE (validity: ants, seeds, model, invalid > 2, or coin rate)**\n")
    else:
        outs=sum(not i for _,i in res.values())
        mv='MODEL HOLDS' if outs==0 else ('MODEL REFUTED' if outs>=2 else 'MODEL MIXED')
        md=f"minimum splitting dose = {minimum:.2f}" if minimum is not None else "no dose splits (incl. 0.10 replicate)"
        p(f"\n## Verdict\n\n**{md}** · explorer model: **{mv}**\n")
    s="\n".join(L)+"\n"; print(s)
    if out: open(out,'w').write(s)
main()
