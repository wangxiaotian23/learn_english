#!/usr/bin/env python3
"""拆分后 a/b 两册共用旧 STORAGE_KEY 导致进度混串：
改为每册独立键，并把旧共享键里的 id 按本册词号范围迁移进来（幂等）。"""
import re, sys

RANGES = {
    'ielts_part1a.html': (1, 300), 'ielts_part1b.html': (301, 600),
    'ielts_part2a.html': (601, 900), 'ielts_part2b.html': (901, 1200),
    'ielts_part3a.html': (1201, 1500), 'ielts_part3b.html': (1501, 1800),
    'ielts_part4a.html': (1801, 2100), 'ielts_part4b.html': (2101, 2400),
    'ielts_part5a.html': (2401, 2700), 'ielts_part5b.html': (2701, 3000),
}
OLD_KEYS = {'1': 'ielts_mastered_part1', '2': 'ielts_mastered_part2',
            '3': 'ielts_mastered_part3', '4': 'ielts_mastered_part4',
            '5': 'ielts_mastered_part5'}

MIGRATION = """  (function migrateSharedKey() {
    try {
      if (localStorage.getItem(STORAGE_KEY) !== null) return;
      var old = JSON.parse(localStorage.getItem('__OLD__') || '[]');
      var lo = __LO__, hi = __HI__;
      var mine = old.filter(function (x) { return x >= lo && x <= hi; });
      localStorage.setItem(STORAGE_KEY, JSON.stringify(mine));
    } catch (e) {}
  })();
"""

for fname, (lo, hi) in RANGES.items():
    path = '/Users/wxl/PycharmProjects/learn_english/ielts/' + fname
    html = open(path, encoding='utf-8').read()
    m = re.search(r"const STORAGE_KEY = '(ielts_mastered_part\d)([ab])?';", html)
    if not m:
        print(f'SKIP {fname}: no STORAGE_KEY found'); continue
    if m.group(2):
        print(f'SKIP {fname}: already split ({m.group(0)})'); continue
    part_no = m.group(1)[-1]
    new_key = f'ielts_mastered_part{part_no}{fname[-6]}'
    html = html.replace(m.group(0), f"const STORAGE_KEY = '{new_key}';", 1)
    mig = (MIGRATION.replace('__OLD__', OLD_KEYS[part_no])
                    .replace('__LO__', str(lo)).replace('__HI__', str(hi)))
    anchor = f"const STORAGE_KEY = '{new_key}';"
    idx = html.index(anchor) + len(anchor)
    html = html[:idx] + '\n' + mig.rstrip('\n') + html[idx:]
    open(path, 'w', encoding='utf-8').write(html)
    print(f'OK   {fname}: {OLD_KEYS[part_no]} -> {new_key} (ids {lo}-{hi})')
