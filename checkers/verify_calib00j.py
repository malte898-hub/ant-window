#!/usr/bin/env python3
"""verify_calib00j.py — BUILD_PLAN v4.0 (noise bracket) Part B rules. stdlib only. Claude, 2026-10-14.
Usage: python3 -I verify_calib00j.py grid.csv [--out VERIFY.md]
grid.csv columns: agent (jev|llm|ant), noise (jev: coin eps e.g. 0.1/0.3; llm: temperature; ant: blank),
                  variant (A|B), ttl, seed, frac_short_last50, invalid (True/False), api_error_rate, parse_fail_rate_depart, parse_fail_rate_return
Rules (v4.0 §6):
 Validity: ants A2.5>=0.85, B2.5>=0.85, B3<=0.25 (medians); seeds 500-511 only, once per arm-cell; <=2 invalid per arm.
 Invalid run: invalid=True, api_error_rate>0.10 or parse_fail>0.10. Counted against its prediction (B2.5 invalid = not switched, B3 invalid = not locked).
 Switched = frac>=0.8 (B2.5). Locked = frac<=0.3 (B3). AUC = P(B2.5 run > B3 run), ties 0.5.
 JEV eps0.30 BOUNDARY RESTORED: AUC>=0.90 AND locked>=10/12 AND switched>=7/12 AND A2.5 median>=0.75.
 JEV DOSE CONFIRMED: RESTORED at 0.30 AND eps0.10 AUC<=0.75.  Else at 0.30: AUC<=0.70 -> NOT RESTORED; between -> INCONCLUSIVE.
 LLM (chosen temperature) uses the v1.8.2 relative rules: ceiling=median A2.5 valid>=0.75; rel=frac/ceiling;
   PASS: U>=120/144, median rel B2.5>=0.90, median rel B3<=0.60. KILL: U<=100 or median rel B2.5<0.70. Else INCONCLUSIVE. ceiling<0.75 -> UNINTERPRETABLE.
Tested 2026-10-14: simulated-true grid -> RESTORED+DOSE / llama PASS; eps-0 null grid -> NOT RESTORED / llama UNINTERPRETABLE; duplicate seed -> UNINTERPRETABLE.
"""
import csv, sys, statistics as st
def fl(x):
    try: return float(x)
    except: return 0.0
def main():
    a=sys.argv[1:]; path=a[0]; out=a[a.index('--out')+1] if '--out' in a else None
    rows=list(csv.DictReader(open(path,newline='')))
    L=[]; p=L.append; p("# calib-00j — verdict (verify_calib00j.py, v4.0 rules)\n")
    inv=lambda r: r.get('invalid') in ('True','true','1') or max(fl(r.get('api_error_rate')),fl(r.get('parse_fail_rate_depart')),fl(r.get('parse_fail_rate_return')))>0.10
    def cell(ag,nz,v,t): return [r for r in rows if r.get('agent')==ag and (nz is None or abs(fl(r.get('noise'))-nz)<1e-9) and r['variant']==v and abs(fl(r['ttl'])-t)<1e-9]
    ant={c:[fl(r['frac_short_last50']) for r in cell('ant',None,*c)] for c in [('A',2.5),('B',2.5),('B',3)]}
    am={c:(st.median(v) if v else None) for c,v in ant.items()}
    ants_ok=None not in am.values() and am[('A',2.5)]>=0.85 and am[('B',2.5)]>=0.85 and am[('B',3)]<=0.25
    p(f"Ants: A2.5 {am[('A',2.5)]} · B2.5 {am[('B',2.5)]} · B3 {am[('B',3)]} → {'OK' if ants_ok else 'FAIL'}")
    bad=[r['seed'] for r in rows if r.get('agent') in ('jev','llm') and not 500<=int(fl(r['seed']))<=511]
    if bad: p(f"**STOP: seeds outside 500–511: {sorted(set(bad))}**")
    def arm(ag,nz,needA):
        A=cell(ag,nz,'A',2.5); B25=cell(ag,nz,'B',2.5); B3=cell(ag,nz,'B',3)
        n_inv=sum(inv(r) for r in A+B25+B3)
        S=set(range(500,512)); sd=lambda c: sorted(int(fl(r['seed'])) for r in c)==sorted(S)
        short=[not sd(B25), not sd(B3), needA and not sd(A)]   # exactly seeds 500-511, once each
        return A,B25,B3,n_inv,any(short)
    def auc(x,y): return sum((i>j)+0.5*(i==j) for i in x for j in y)/max(1,len(x)*len(y))
    # JEV
    res={}
    for nz,needA in ((0.30,True),(0.10,False)):
        A,B25,B3,ni,short=arm('jev',nz,needA)
        x=[0.0 if inv(r) else fl(r['frac_short_last50']) for r in B25]
        y=[1.0 if inv(r) else fl(r['frac_short_last50']) for r in B3]
        Am=st.median([fl(r['frac_short_last50']) for r in A if not inv(r)]) if A else float('nan')
        res[nz]=dict(auc=auc(x,y),sw=sum(v>=0.8 for v in x),lk=sum(v<=0.3 for v in y),A=Am,ni=ni,short=short,nB=len(B25),nC=len(B3))
        r_=res[nz]; p(f"Jev eps {nz:.2f}: AUC {r_['auc']:.3f} · switched {r_['sw']}/{r_['nB']} · locked {r_['lk']}/{r_['nC']} · A2.5 median {r_['A']:.3f} · invalid {ni}{' · **CELL COUNT ≠ 12**' if short else ''}")
    j=res[0.30]; j1=res[0.10]
    if not ants_ok or bad or j['short'] or j1['short'] or j['ni']>2 or j1['ni']>2: jv='UNINTERPRETABLE (validity)'
    elif j['auc']>=0.90 and j['lk']>=10 and j['sw']>=7 and j['A']>=0.75:
        jv='BOUNDARY RESTORED + DOSE CONFIRMED' if j1['auc']<=0.75 else 'BOUNDARY RESTORED (dose not confirmed: eps0.10 AUC>0.75)'
    elif j['auc']<=0.70: jv='NOT RESTORED'
    else: jv='INCONCLUSIVE'
    p(f"\n## Jev verdict\n\n**{jv}**\n")
    # LLM
    A,B25,B3,ni,short=arm('llm',None,True)
    temps=sorted(set(r.get('noise') for r in A+B25+B3))
    if not (A or B25 or B3): p("## llama verdict\n\n(no llm rows)\n")
    else:
        Aok=[fl(r['frac_short_last50']) for r in A if not inv(r)]
        ceil=st.median(Aok) if Aok else 0.0
        rel=lambda r,d: d if inv(r) else (fl(r['frac_short_last50'])/ceil if ceil>0 else 0.0)
        x=[rel(r,0.0) for r in B25]; y=[rel(r,1.0) for r in B3]
        U=sum((i>k)+0.5*(i==k) for i in x for k in y); m25=st.median(x) if x else 0; m3=st.median(y) if y else 1
        p(f"llama temperature(s) {temps}: ceiling {ceil:.3f} · U {U:g}/{len(x)*len(y)} · rel B2.5 {m25:.3f} · rel B3 {m3:.3f} · invalid {ni}")
        if len(temps)!=1: lv='UNINTERPRETABLE (more than one temperature in llm rows)'
        elif not ants_ok or bad or short or ni>2 or ceil<0.75: lv='UNINTERPRETABLE (validity: ants, seeds, counts, invalid>2 or ceiling<0.75)'
        elif U<=100 or m25<0.70: lv='KILL'
        elif U>=120 and m25>=0.90 and m3<=0.60: lv='PASS — boundary restored at this temperature'
        else: lv='INCONCLUSIVE'
        p(f"\n## llama verdict\n\n**{lv}**\n")
    s="\n".join(L)+"\n"; print(s)
    if out: open(out,'w').write(s)
main()
