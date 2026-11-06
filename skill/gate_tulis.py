#!/usr/bin/env python
"""Gate tulis TC-19 — checkpoint integritas pra-penulisan (versi publik).

Skrip ini TIDAK PERNAH menulis ke workbook mana pun dalam mode pemeriksaan.
Ia hanya MEMUTUSKAN apakah sebuah path boleh ditulis, dan mencatat bukti.

Prinsip:
  * ALLOWLIST KETAT — hanya satu path yang boleh ditulis (workbook aktif SANDBOX).
  * FAIL-CLOSED — bila path atau identitas file tidak dapat dipastikan, hasilnya FAIL.
  * Tidak ada pemeriksaan keamanan yang dihapus.
  * Artefak produksi yang tidak dapat diakses dicatat NOT ACCESSIBLE / NOT CHECKED,
    dan TIDAK dianggap aman, tetapi juga TIDAK menjadi prasyarat keberhasilan gate.

Mode:
  --check                 periksa ACTIVE_PATH (default)
  --target PATH           periksa PATH apa pun (untuk pengujian penolakan)
  --probe PATH            hanya tampilkan fakta identitas file (diagnostik, read-only)
  --json                  keluaran mesin
  --snapshot --out FILE   tulis hash ke JSON (HANYA untuk pra-penulisan; bukan mode uji)
  --from-snapshot FILE    mode rantai (G1): muat snapshot langkah sebelumnya
  --expect-sha HEX        mode rantai (G1): hash yang diharapkan (WAJIB berpasangan)

Mode rantai (G1) memungkinkan beberapa penulisan sah dalam satu sesi TANPA
melonggarkan allowlist: allowlist tetap tepat satu entri (ACTIVE_PATH), dan
snapshot wajib menunjuk ACTIVE_PATH dengan SHA-256 yang sama dengan berkas
saat ini. Tanpa --from-snapshot, gate kembali ke mode baseline — perilaku lama,
tidak ada pemeriksaan yang dihapus atau dilemahkan.

BATAS YANG HARUS DINYATAKAN: gate adalah CHECKPOINT INTEGRITAS. Ia bukan
penegak persetujuan manusia dan bukan kontrol akses tingkat OS. editor_sdk
menulis tanpa membaca gate, sehingga pemanggilan save_file secara langsung
TIDAK dapat dicegah oleh skrip ini.

Exit code: 0 = PASS, 1 = FAIL, 2 = FATAL.
"""

import argparse
import datetime
import hashlib
import json
import os
import re
import sys

# ---------------------------------------------------------------------------
# A. LOKASI TARGET
# ---------------------------------------------------------------------------
# Publik: seluruh path diturunkan dari direktori home pengguna, sehingga tidak
# ada nama akun atau jalur mesin tertentu yang tertanam di kode. Timpa lewat
# variabel lingkungan bila workspace berada di lokasi lain.
USER_HOME = os.path.expanduser('~')
PROD_HOME = os.environ.get('PPA_PROD_HOME') or os.path.join(
    USER_HOME, 'Documents', 'Hackaton - PPA')

WORKSPACE_ROOT = os.environ.get('PPA_WORKSPACE_ROOT') or os.path.join(
    USER_HOME, 'Documents', 'Hackaton - PPA - SANDBOX')
ACTIVE_NAME = 'Task_Tracker_PPA_TEST.xlsx'
ACTIVE_PATH = os.path.join(WORKSPACE_ROOT, ACTIVE_NAME)

# Allowlist tulis: TEPAT satu entri. Menambah entri = melonggarkan gate.
ALLOWED_TARGETS = (ACTIVE_PATH,)

# MASTER dilindungi: DILARANG ditulis dalam kondisi apa pun — termasuk bila
# ACTIVE_PATH hilang atau rusak. Diperiksa eksplisit agar alasan penolakannya
# jelas, bukan sekadar "tidak ada di allowlist".
PROTECTED_MASTERS = {
    'MASTER_V2': os.path.join(WORKSPACE_ROOT, 'Task_Tracker_PPA_V2.xlsx'),
}

# Baseline awal workbook (acuan integritas).
# Workbook sandbox TIDAK disertakan dalam paket publik ini, sehingga nilai di
# bawah hanya berlaku pada lingkungan asal. Setel PPA_BASELINE_SHA ke SHA-256
# awal workbook Anda sendiri; tanpa itu gate akan (dan seharusnya) FAIL.
BASELINE_SHA = os.environ.get('PPA_BASELINE_SHA') or \
    'af3b532bcf40513d308426fe2b1f08519cfb1283238cfc4d52273f138a90bc32'

# Arsip di dalam workspace: harus tetap utuh, TIDAK boleh ditulis.
ARCHIVES = {
    'ARCHIVE_V1':     os.path.join(WORKSPACE_ROOT, 'Task_Tracker_PPA.xlsx'),
    'ARCHIVE_BACKUP': os.path.join(WORKSPACE_ROOT, 'Task_Tracker_PPA_BACKUP.xlsx'),
}

# Wilayah terlarang. Dipakai untuk memberi alasan penolakan yang jelas
# (allowlist sudah menolaknya lebih dulu).
FORBIDDEN_ROOTS = {
    'PROD_LOCAL': PROD_HOME,
    'EVALUATOR':  os.path.join(USER_HOME, 'Documents', 'Hackaton - PPA - EVALUATOR'),
    'ANCHOR':     os.path.join(USER_HOME, 'Documents', 'Hackaton - PPA - ANCHOR'),
}

# Artefak produksi yang idealnya ikut diverifikasi. Di lingkungan terisolasi
# ini ketiadaannya WAJAR dan tidak menggagalkan gate (lihat audit_environment).
PRODUCTION_ARTIFACTS = {
    'PROD_V2':       os.path.join(PROD_HOME, 'Task_Tracker_PPA_V2.xlsx'),
    'PROD_TEST':     os.path.join(PROD_HOME, 'Task_Tracker_PPA_TEST.xlsx'),
    'PROD_V1':       os.path.join(PROD_HOME, 'Task_Tracker_PPA.xlsx'),
    'PROD_BACKUP':   os.path.join(PROD_HOME, 'Task_Tracker_PPA_BACKUP.xlsx'),
    'BASELINE_EVAL': os.path.join(USER_HOME, 'Documents', 'Hackaton - PPA - EVALUATOR',
                                  'baseline', 'Task_Tracker_PPA_BASELINE.xlsx'),
}

DATASET_DIR = os.path.join(WORKSPACE_ROOT, 'dataset')
DATASET_EXPECTED_FILES = 23

SKILL_MD = os.path.join(
    os.path.expanduser('~'), '.workbuddy-ai', 'skills',
    'ppa-smart-office-agent-sandbox', 'SKILL.md')
SKILL_SHA_EXPECTED = '5aea85937bd20fdc6d2e4b5f9d4572b9e37f1643778af66615b7a4db5558fe83'

FILE_ATTRIBUTE_REPARSE_POINT = 0x400

# Bentuk SHA-256 yang sah untuk snapshot rantai.
SNAP_SHA_RE = re.compile(r'^[0-9a-f]{64}$')


# ---------------------------------------------------------------------------
# Utilitas
# ---------------------------------------------------------------------------
def norm(p):
    """Normalisasi absolut: kapitalisasi + pemisah path + segmen."""
    return os.path.normcase(os.path.normpath(os.path.abspath(p)))


def under(path, root):
    """True bila `path` berada di dalam `root` (batas komponen, bukan prefix string)."""
    p, r = norm(path), norm(root)
    return p == r or p.startswith(r + os.sep)


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def identity(path):
    """Fakta identitas fisik file. Melempar exception bila tidak dapat dipastikan."""
    st = os.lstat(path)
    return {
        'exists': True,
        'islink': os.path.islink(path),
        'isjunction': os.path.isjunction(path),
        'reparse': bool(getattr(st, 'st_file_attributes', 0) & FILE_ATTRIBUTE_REPARSE_POINT),
        'nlink': st.st_nlink,
        'ino': getattr(st, 'st_ino', None),
        'size': st.st_size,
        'realpath': os.path.realpath(path),
        'is_file': os.path.isfile(path),
    }


# ---------------------------------------------------------------------------
# Inti gate
# ---------------------------------------------------------------------------
def verify(target, expect_sha=None, snap=None):
    """Putuskan apakah `target` boleh ditulis. Fail-closed."""
    checks = []
    problems = []

    def add(name, ok, detail=''):
        checks.append({'check': name, 'result': 'PASS' if ok else 'FAIL', 'detail': detail})
        if not ok:
            problems.append('%s: %s' % (name, detail))

    res = {'target': target, 'checks': checks, 'problems': problems,
           'decision': None, 'sha256': None, 'identity': None,
           'mode': None, 'step': None, 'prev_sha': None}

    # 1. Tipe & kekosongan
    if not isinstance(target, str) or not target.strip():
        add('path diberikan', False, 'path kosong atau bukan string')
        res['decision'] = 'FAIL'
        return res
    add('path diberikan', True, target)

    raw = target.replace('/', '\\')

    # 2. Harus absolut (drive letter lokal, bukan relatif / UNC)
    is_abs = os.path.isabs(target) and not raw.startswith('\\\\')
    add('path absolut (drive lokal, bukan UNC)', is_abs,
        'path relatif atau UNC tidak diterima' if not is_abs else raw)
    if not is_abs:
        res['decision'] = 'FAIL'
        return res

    # 3. Tolak path traversal secara eksplisit (sebelum normalisasi menutupinya)
    parts = [s for s in raw.split('\\') if s not in ('', '.')]
    has_traversal = '..' in parts
    add('bebas segmen ".." (path traversal)', not has_traversal,
        'mengandung ".." -> ditolak' if has_traversal else 'bersih')
    if has_traversal:
        res['decision'] = 'FAIL'
        return res

    normalized = norm(target)
    res['normalized'] = normalized

    # 4. Harus di dalam WORKSPACE_ROOT
    in_ws = under(normalized, WORKSPACE_ROOT)
    add('berada di dalam WORKSPACE_ROOT', in_ws,
        normalized if in_ws else 'di luar %s' % WORKSPACE_ROOT)

    # 5. Alasan penolakan yang eksplisit untuk wilayah terlarang
    for label, root in FORBIDDEN_ROOTS.items():
        if under(normalized, root):
            add('bukan wilayah terlarang (%s)' % label, False,
                'path wilayah %s DITOLAK' % label)

    # 5b. MASTER dilindungi — penolakan eksplisit, bukan sekadar absen dari allowlist
    for label, mp in PROTECTED_MASTERS.items():
        if normalized == norm(mp):
            add('bukan MASTER terlindungi (%s)' % label, False,
                'MASTER %s DILARANG ditulis' % label)

    # 6. Allowlist ketat
    allowed = {norm(p) for p in ALLOWED_TARGETS}
    in_allow = normalized in allowed
    add('terdaftar di allowlist tulis', in_allow,
        ACTIVE_NAME if in_allow else 'bukan target yang diizinkan (allowlist: %s)'
        % ', '.join(sorted(os.path.basename(p) for p in ALLOWED_TARGETS)))

    if not (in_ws and in_allow):
        res['decision'] = 'FAIL'
        return res

    # 7. Keberadaan file
    if not os.path.exists(target):
        add('file target ada', False, 'tidak ditemukan')
        res['decision'] = 'FAIL'
        return res
    add('file target ada', True, target)

    # 8. Identitas fisik (fail-closed bila gagal dibaca)
    try:
        ident = identity(target)
    except OSError as e:
        add('identitas file dapat dipastikan', False,
            '%s: %s' % (type(e).__name__, e))
        res['decision'] = 'FAIL'
        return res
    res['identity'] = ident
    add('identitas file dapat dipastikan', True, 'lstat OK')

    add('bukan file biasa', ident['is_file'], 'isfile=%s' % ident['is_file'])
    add('bukan symlink', not ident['islink'], 'islink=%s' % ident['islink'])
    add('bukan junction', not ident['isjunction'], 'isjunction=%s' % ident['isjunction'])
    add('bukan reparse point', not ident['reparse'], 'reparse=%s' % ident['reparse'])
    real_ok = norm(ident['realpath']) == normalized
    add('realpath tidak berbelok', real_ok,
        ident['realpath'] if not real_ok else 'sama dengan target')
    add('bukan hardlink (st_nlink == 1)', ident['nlink'] == 1,
        'st_nlink=%s' % ident['nlink'])

    if problems:
        res['decision'] = 'FAIL'
        return res

    # 9. Integritas isi: baseline (langkah pertama) atau rantai snapshot (G1)
    try:
        h = sha256_file(target)
    except OSError as e:
        add('SHA-256 dapat dihitung', False, '%s: %s' % (type(e).__name__, e))
        res['decision'] = 'FAIL'
        return res
    res['sha256'] = h
    add('SHA-256 dapat dihitung', True, h)

    if snap is None:
        # Mode baseline — perilaku lama dipertahankan apa adanya.
        res['mode'] = 'baseline'
        res['step'] = 1
        res['prev_sha'] = BASELINE_SHA
        add('SHA-256 sesuai baseline awal', h == BASELINE_SHA,
            h if h != BASELINE_SHA else BASELINE_SHA)
    else:
        # Mode rantai — snapshot langkah sebelumnya mengikat target & kondisi.
        res['mode'] = 'chained'
        res['step'] = int(snap.get('step', 0)) + 1
        res['prev_sha'] = snap['sha256']
        add('snapshot menunjuk target ini', True, snap['active_path'])
        add('SHA-256 berkas == snapshot (langkah sebelumnya)',
            h == snap['sha256'],
            'berkas=%s snapshot=%s' % (h[:16], str(snap['sha256'])[:16]))
        add('--expect-sha == snapshot.sha256',
            str(expect_sha) == str(snap['sha256']),
            'expect=%s snapshot=%s' % (str(expect_sha)[:16], str(snap['sha256'])[:16]))
        add('SHA-256 berkas == --expect-sha', h == str(expect_sha),
            'berkas=%s expect=%s' % (h[:16], str(expect_sha)[:16]))

    res['decision'] = 'FAIL' if problems else 'PASS'
    return res


def load_snapshot(path):
    """Muat & validasi snapshot rantai (G1). Fail-closed: (None, alasan) bila tidak sah."""
    try:
        with open(path, encoding='utf-8') as f:
            snap = json.load(f)
    except OSError as e:
        return None, 'snapshot tidak dapat dibaca (%s)' % type(e).__name__
    except ValueError as e:
        return None, 'snapshot bukan JSON valid (%s)' % type(e).__name__
    if not isinstance(snap, dict):
        return None, 'snapshot bukan objek JSON'
    for k in ('active_path', 'sha256', 'identity'):
        if k not in snap:
            return None, 'snapshot tidak memuat field "%s"' % k
    if norm(snap['active_path']) != norm(ACTIVE_PATH):
        return None, 'snapshot menunjuk path lain: %s' % snap['active_path']
    if not SNAP_SHA_RE.match(str(snap['sha256'])):
        return None, 'sha256 snapshot tidak valid (harus 64 hex lowercase)'
    return snap, ''


def probe(target):
    """Diagnostik identitas saja. Tidak menerapkan allowlist, tidak menulis."""
    out = {'target': target}
    try:
        out['identity'] = identity(target)
    except OSError as e:
        out['identity'] = {'error': '%s: %s' % (type(e).__name__, e)}
    return out


def audit_environment():
    """Audit artefak di luar kendali gate.

    Artefak yang tidak dapat diakses TIDAK dihitung sebagai pelanggaran,
    tetapi juga TIDAK dicap aman: statusnya NOT ACCESSIBLE / NOT CHECKED.
    """
    rows = []
    for label, p in PRODUCTION_ARTIFACTS.items():
        row = {'label': label, 'path': p, 'status': None, 'sha256': None, 'note': ''}
        try:
            if not os.path.exists(p):
                row['status'] = 'NOT FOUND'
                row['note'] = 'tidak ada di lingkungan ini (bukan bukti aman)'
            else:
                row['sha256'] = sha256_file(p)
                row['status'] = 'ACCESSIBLE'
                row['note'] = 'terbaca — hash dicatat, bukan divalidasi terhadap acuan'
        except PermissionError as e:
            code = getattr(e, 'winerror', None) or getattr(e, 'errno', None) or 'denied'
            row['status'] = 'NOT ACCESSIBLE'
            row['note'] = 'PermissionError [%s] — tidak diverifikasi (bukan bukti aman)' % code
        except OSError as e:
            row['status'] = 'NOT ACCESSIBLE'
            row['note'] = '%s — tidak diverifikasi' % type(e).__name__
        rows.append(row)

    archives = []
    for label, p in ARCHIVES.items():
        row = {'label': label, 'path': p, 'status': None, 'sha256': None}
        try:
            row['sha256'] = sha256_file(p)
            row['status'] = 'READ-ONLY HASHED'
        except OSError as e:
            row['status'] = 'NOT CHECKED'
            row['note'] = type(e).__name__
        archives.append(row)

    ds = {'dir': DATASET_DIR, 'expected': DATASET_EXPECTED_FILES, 'found': None, 'status': None}
    try:
        n = 0
        for _root, _dirs, files in os.walk(DATASET_DIR):
            n += len(files)
        ds['found'] = n
        ds['status'] = 'OK' if n == DATASET_EXPECTED_FILES else 'MISMATCH'
    except OSError as e:
        ds['status'] = 'NOT CHECKED'
        ds['note'] = type(e).__name__

    sk = {'path': SKILL_MD, 'expected': SKILL_SHA_EXPECTED, 'sha256': None, 'status': None}
    try:
        sk['sha256'] = sha256_file(SKILL_MD)
        sk['status'] = 'OK' if sk['sha256'] == SKILL_SHA_EXPECTED else 'MISMATCH'
    except OSError as e:
        sk['status'] = 'NOT CHECKED'
        sk['note'] = type(e).__name__

    return {'production': rows, 'archives': archives, 'dataset': ds, 'skill': sk}


def print_report(res, env=None):
    print('=' * 74)
    print('GATE TULIS TC-19 — MODE PEMERIKSAAN (READ-ONLY)')
    print('=' * 74)
    print('WORKSPACE_ROOT :', WORKSPACE_ROOT)
    print('ALLOWLIST      :', ', '.join(ALLOWED_TARGETS))
    print('MASTER (LARANG):', ', '.join(sorted(os.path.basename(p) for p in PROTECTED_MASTERS.values())))
    print('TARGET         :', res['target'])
    if res.get('mode'):
        print('MODE           : %s (langkah %s)' % (res['mode'], res.get('step')))
    if res.get('normalized'):
        print('NORMALISASI    :', res['normalized'])
    print('-' * 74)
    for c in res['checks']:
        print('  [%-4s] %-46s %s' % (c['result'], c['check'], c['detail']))
    if res.get('identity'):
        i = res['identity']
        print('-' * 74)
        print('IDENTITAS      : isfile=%s islink=%s isjunction=%s reparse=%s nlink=%s inode=%s' % (
            i.get('is_file'), i.get('islink'), i.get('isjunction'),
            i.get('reparse'), i.get('nlink'), i.get('ino')))
        print('REALPATH       :', i.get('realpath'))
    if res.get('sha256'):
        print('SHA-256        :', res['sha256'])
        print('BASELINE       :', BASELINE_SHA)
    print('-' * 74)
    print('KEPUTUSAN      :', res['decision'])
    if res['problems']:
        print('PELANGGARAN    :')
        for p in res['problems']:
            print('   - ' + p)

    if env:
        print('-' * 74)
        print('AUDIT LINGKUNGAN (tidak memengaruhi keputusan gate)')
        print('  Artefak produksi:')
        for r in env['production']:
            print('    %-15s %-15s %s' % (r['label'], r['status'], r['note'] or r['sha256'] or ''))
        print('  Arsip workspace (read-only hash):')
        for r in env['archives']:
            print('    %-15s %-16s %s' % (r['label'], r['status'], r['sha256'] or ''))
        d = env['dataset']
        print('  Dataset        : %s (%s/%s file)' % (d['status'], d['found'], d['expected']))
        s = env['skill']
        print('  Skill SKILL.md : %s %s' % (s['status'], s['sha256'] or s.get('note', '')))
    print('=' * 74)


def main():
    ap = argparse.ArgumentParser(description='Gate tulis TC-19 (read-only).')
    ap.add_argument('--check', action='store_true', help='periksa ACTIVE_PATH (default)')
    ap.add_argument('--target', help='periksa path tertentu')
    ap.add_argument('--probe', help='diagnostik identitas path (tanpa allowlist)')
    ap.add_argument('--json', action='store_true', help='keluaran JSON')
    ap.add_argument('--snapshot', action='store_true', help='tulis hash ke JSON (pra-penulisan)')
    ap.add_argument('--out', help='path keluaran snapshot')
    ap.add_argument('--from-snapshot', help='mode rantai: snapshot JSON langkah sebelumnya (G1)')
    ap.add_argument('--expect-sha', help='mode rantai: SHA-256 yang diharapkan (G1)')
    args = ap.parse_args()

    if args.probe:
        out = probe(args.probe)
        print(json.dumps(out, indent=2, default=str))
        return 0

    # Guard G1: kedua opsi rantai hanya sah dipakai BERSAMA.
    if bool(args.expect_sha) != bool(args.from_snapshot):
        print('FATAL: --expect-sha dan --from-snapshot harus dipakai BERSAMA.')
        print('       Tidak ada mode "percaya saja".')
        return 2

    snap = None
    if args.from_snapshot:
        snap, why = load_snapshot(args.from_snapshot)
        if snap is None:
            print('FATAL: snapshot tidak sah — %s' % why)
            return 2

    target = args.target or ACTIVE_PATH
    res = verify(target, expect_sha=args.expect_sha, snap=snap)
    env = audit_environment() if not args.target else None

    if args.json:
        print(json.dumps({'result': res, 'environment': env}, indent=2, default=str))
    else:
        print_report(res, env)

    if args.snapshot:
        # Hanya jalur eksplisit; tidak dipakai dalam mode uji.
        if res['decision'] != 'PASS':
            print('SNAPSHOT DITOLAK: gate tidak PASS')
            return 1
        out = args.out or 'snapshot_gate.json'
        payload = {
            'active_path': ACTIVE_PATH,
            'sha256': res['sha256'],
            'identity': res['identity'],
            'mode': res.get('mode'),
            'step': res.get('step'),
            'prev_sha': res.get('prev_sha'),
            'written_at': datetime.datetime.now().isoformat(timespec='seconds'),
        }
        with open(out, 'w', encoding='utf-8') as f:
            json.dump(payload, f, indent=2, default=str)
        print('snapshot ->', out)
        print('  mode=%s step=%s prev_sha=%s' % (
            payload['mode'], payload['step'], str(payload['prev_sha'])[:16]))

    return 0 if res['decision'] == 'PASS' else 1


if __name__ == '__main__':
    sys.exit(main())
