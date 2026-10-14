#!/usr/bin/env python3
"""verify_calib00g.py — BUILD_PLAN v3.1.1 (calib-00g, live Jev) §5 rules. stdlib only. Claude, 2026-10-14.
Usage: python3 -I verify_calib00g.py grid.csv [--decisions decisions.csv] [--intervals registered|boot] [--boot jev_sim_boot.csv] [--out VERIFY.md]
grid.csv columns used: agent (jev|ant), variant (A|B), ttl, seed, frac_short_last50, api_error_rate (jev), invalid (optional).
decisions.csv (optional, for the secondary mechanism stat): run_id or (variant,ttl,seed), tick, chosen (short|long).
Rules: VALID = ants A2.5>=0.85, B2.5>=0.85, B3<=0.25 (medians) AND invalid Jev cells <= 3.
       INCOMPLETE if any Jev cell (A2.5, B2.5, B3) has < 21 valid runs, or seeds outside 300-323.
       Medians on valid runs. Counts (B2.5 >=0.8, <=0.3): invalid runs count toward neither (miss).
       Hit = inside the registered 90% interval (no tolerance). 5/5 CONFIRMED, 3-4 PARTIAL, <=2 REFUTED.
Default intervals = registered §4 table (recomputable from jev_sim_pool.csv). '--intervals boot' uses jev_sim_boot.csv
(5th-95th percentile across 200 probe-label-pair bootstraps) — only if HITL adopts it before data.
Tested 2026-10-14 on synthetic grids: draw from jev_sim_pool -> PARTIAL 4/5 (registered) / CONFIRMED 5/5 (boot);
B values shifted -0.15 -> REFUTED; 4 invalid Jev cells -> STOP/INCOMPLETE.
"""
import csv, sys, statistics as st, collections
REG={'A25_median':(0.980,0.989),'B25_median':(0.756,0.857),'B3_median':(0.016,0.027),'B25_ge08':(8,16),'B25_le03':(1,7)}
def fl(x):
    try: return float(x)
    except: return 0.0
def boot_intervals(path):
    rows=list(csv.DictReader(open(path)))
    def q(k):
        v=sorted(float(r[k]) for r in rows); n=len(v); return (v[int(.05*n)], v[min(n-1,int(.95*n))])
    return {'A25_median':q('A25'),'B25_median':q('B25'),'B3_median':q('B3'),'B25_ge08':q('sw'),'B25_le03':q('lk')}
def main():
    a=sys.argv[1:]; path=a[0]
    opt=lambda k,d=None: a[a.index(k)+1] if k in a else d
    out=opt('--out'); mode=opt('--intervals','registered')
    IV=REG if mode=='registered' else boot_intervals(opt('--boot','jev_sim_boot.csv'))
    rows=list(csv.DictReader(open(path,newline='')))
    L=[]; p=L.append
    p(f"# calib-00g — verdict (verify_calib00g.py, v3.1.1 rules, intervals: {mode})\n")
    def cell(agent,v,t): return [r for r in rows if r.get('agent')==agent and r['variant']==v and abs(fl(r['ttl'])-t)<1e-9]
    inv=lambda r: r.get('invalid') in ('True','true','1') or fl(r.get('api_error_rate'))>0.10
    ant={c:[fl(r['frac_short_last50']) for r in cell('ant',*c)] for c in [('A',2.5),('B',2.5),('B',3)]}
    antmed={c:(st.median(v) if v else None) for c,v in ant.items()}
    ants_ok=all(antmed[c] is not None for c in antmed) and antmed[('A',2.5)]>=0.85 and antmed[('B',2.5)]>=0.85 and antmed[('B',3)]<=0.25
    p(f"Ants: A2.5 {antmed[('A',2.5)]} · B2.5 {antmed[('B',2.5)]} · B3 {antmed[('B',3)]} → {'OK' if ants_ok else 'FAIL'}\n")
    J={c:cell('jev',*c) for c in [('A',2.5),('B',2.5),('B',3)]}
    allj=[r for v in J.values() for r in v]
    ninv=sum(inv(r) for r in allj)
    bad_seed=[r['seed'] for r in allj if not (300<=int(fl(r['seed']))<=323)]
    valid={c:[fl(r['frac_short_last50']) for r in v if not inv(r)] for c,v in J.items()}
    nvalid={c:len(v) for c,v in valid.items()}
    p(f"Jev cells: { {f'{c[0]}{c[1]}':len(v) for c,v in J.items()} } · valid { {f'{c[0]}{c[1]}':n for c,n in nvalid.items()} } · invalid total {ninv}")
    if bad_seed: p(f"**Seeds outside 300–323: {sorted(set(bad_seed))}**")
    if not ants_ok or ninv>3:
        verdict='STOP / INCOMPLETE (validity failed: ants or >3 invalid Jev cells)'
    elif bad_seed or any(n<21 for n in nvalid.values()):
        verdict='INCOMPLETE (valid Jev runs < 21 in a cell, or wrong seeds)'
    else:
        verdict=None
    B25all=J[('B',2.5)]
    stats={'A25_median':st.median(valid[('A',2.5)]) if valid[('A',2.5)] else float('nan'),
           'B25_median':st.median(valid[('B',2.5)]) if valid[('B',2.5)] else float('nan'),
           'B3_median':st.median(valid[('B',3)]) if valid[('B',3)] else float('nan'),
           'B25_ge08':sum(1 for r in B25all if not inv(r) and fl(r['frac_short_last50'])>=0.8),
           'B25_le03':sum(1 for r in B25all if not inv(r) and fl(r['frac_short_last50'])<=0.3)}
    hits=0
    p("\n| Statistic | Live | 90% interval | Hit |\n|---|---|---|---|")
    for k,v in stats.items():
        lo,hi=IV[k]; h=lo<=v<=hi; hits+=h
        p(f"| {k} | {v:.3f} | {lo:.3f}–{hi:.3f} | {'✓' if h else '✗'} |" if isinstance(v,float) else f"| {k} | {v} | {lo:g}–{hi:g} | {'✓' if h else '✗'} |")
    if verdict is None:
        verdict='SIMULATOR CONFIRMED (Jev, this world)' if hits==5 else ('PARTIAL' if hits>=3 else 'SIMULATOR REFUTED')
    p(f"\n## Verdict\n\n**{verdict}** — hits {hits}/5\n")
    dpath=opt('--decisions')
    if dpath:
        d=collections.defaultdict(list)
        for r in csv.DictReader(open(dpath,newline='')):
            if r.get('variant')!='B': continue
            t=int(fl(r['tick']))
            if 40<=t<50: d[(r.get('ttl'),r.get('seed'))].append(1 if r['chosen']=='short' else 0)
        sh=[sum(v)/len(v) for v in d.values() if v]
        if sh: p(f"Secondary: P(short) ticks 40–49 in B runs — median {st.median(sh):.3f} (predicted ≤ 0.10), range {min(sh):.2f}–{max(sh):.2f}, n {len(sh)}")
    s="\n".join(L)+"\n"; print(s)
    if out: open(out,'w').write(s)
main()
