# Excel Schema — `ACTIVE_WORKBOOK_PATH` (MODE SANDBOX)

## Skema File

File target adalah `ACTIVE_WORKBOOK_PATH` = `%USERPROFILE%\Documents\Hackaton - PPA - SANDBOX\Task_Tracker_PPA_TEST.xlsx` — salinan kerja pengujian, **bukan** master produksi. MASTER `Task_Tracker_PPA_V2.xlsx` berstatus **READ ONLY** dan bukan target tulis. Agent harus memeriksa file ini sebelum membuat preview atau update. File lama `Task_Tracker_PPA.xlsx` (V1) berstatus arsip dan tidak diubah. Workspace produksi `%USERPROFILE%\Documents\Hackaton - PPA\` **DILARANG ditulis** dalam mode sandbox.

## Sheet: Tasks

| Kolom | Tipe | Wajib | Deskripsi |
|-------|------|-------|-----------|
| A - Project ID | String | Ya | Identifier unik proyek (format: PPA-YYYY-NN) |
| B - Task ID | String | Ya | Identifier unik tugas (format: T-NNN) |
| C - Deskripsi Tugas | String | Ya | Uraian pekerjaan |
| D - PIC | String | Ya | Penanggung jawab — jabatan/tim (mis. Drafter, Admin, Koordinator, Tim MEP) atau individu; keduanya valid |
| E - Deadline | Date | Ya | Tanggal target selesai (format: YYYY-MM-DD) |
| F - Status Pekerjaan | Enum | Ya | Not Started / In Progress / Completed / On Hold |
| G - Prioritas | Enum | Tidak | High / Medium / Low |
| H - Sumber Informasi | String | Ya | Darimana tugas ini berasal (notulen, instruksi, dll.) |
| I - Catatan | String | Tidak | Catatan tambahan |

## Aturan Operasi Excel

### Sebelum Update
1. **Baca file aktual** — Selalu periksa file Excel aktual sebelum membuat preview. Jangan mengandalkan data dari memori percakapan saja.
2. **Periksa duplikasi** — Pastikan pasangan Project ID + Task ID belum ada di file sebelum menambah baris baru.
3. **Identifikasi baris** — Untuk update, identifikasi baris yang tepat berdasarkan Project ID dan Task ID.
4. **Baca ulang file aktual tepat sebelum eksekusi** — Kondisi file dapat berubah sejak preview dibuat.

### Saat Preview
- Tampilkan nilai sebelum dan sesudah untuk setiap perubahan
- Tampilkan posisi baris sebagai PROVISIONAL (estimasi, beri label "provisional") — bukan nomor final
- Nomor baris final dihitung ulang dari file aktual saat eksekusi
- Tandai baris baru vs baris yang diupdate
- Jangan membuat baris kosong (placeholder) untuk tugas yang Blocked

### Saat Eksekusi
- Verifikasi bahwa target adalah `ACTIVE_WORKBOOK_PATH` sebelum menulis; tolak path lain
- Baca ulang file aktual, lalu tentukan baris final hanya untuk tugas yang valid dan disetujui
- Tulis tugas yang disetujui berurutan menaik sesuai Task ID, tanpa menyisakan baris kosong
- Jangan menimpa data yang tidak terkait dengan tindakan yang disetujui
- Jangan menduplikasi data existing
- **Setelah `set_cell_range`, WAJIB panggil `save_file` pada `file_id` yang sama** — tanpa langkah ini perubahan hanya ada di memori editor dan tidak tersimpan ke disk. `save_file` bukan tool MCP: perintah CLI lengkapnya ada di `SKILL.md` Tahap 6 langkah 4 (butuh Bash + Python)
- `file_id` untuk `set_cell_range` maupun `save_file` adalah **`ACTIVE_FILE_ID`** yang dikembalikan `edsdk.py call open_file`, bukan `ACTIVE_WORKBOOK_PATH` yang disusun manual. Lihat "Kontrak `file_id`" di `SKILL.md`
- Setelah eksekusi, baca ulang file dari disk (openpyxl) untuk verifikasi, dan bandingkan SHA-256 sebelum vs sesudah

### Setelah Eksekusi
- Bandingkan hasil aktual dengan preview yang disetujui
- Jika ada perbedaan di luar ruang lingkup persetujuan, catat sebagai "Failed"
- Catat hasil di audit log

## Data Fiktif Contoh

Versi pertama menggunakan proyek dan kontak fiktif. Berikut contoh data yang mungkin ada di file:

| Project ID | Task ID | Deskripsi | PIC | Deadline | Status | Sumber |
|------------|---------|-----------|-----|----------|--------|--------|
| PPA-2026-01 | T-001 | Pengumpulan data awal PBG | Rina | 2026-10-30 | In Progress | Notulen rapat 2026-10-15 |
| PPA-2026-01 | T-002 | Verifikasi dokumen SLF | Andi | 2026-11-05 | Not Started | Notulen rapat 2026-10-15 |
| PPA-2026-02 | T-003 | Koordinasi survey lokasi | Budi | 2026-10-28 | Completed | Instruksi email 2026-10-10 |
| PPA-2026-02 | T-004 | Penyusunan laporan PBG | Sari | 2026-11-15 | On Hold | Notulen rapat 2026-10-20 |

## Catatan Penting

- File target adalah `ACTIVE_WORKBOOK_PATH` = `%USERPROFILE%\Documents\Hackaton - PPA - SANDBOX\Task_Tracker_PPA_TEST.xlsx`; MASTER `Task_Tracker_PPA_V2.xlsx` hanya baca; file `Task_Tracker_PPA.xlsx` (V1) adalah arsip dan tidak diubah. Struktur 9 kolom (A–I) sudah benar dan TIDAK diubah.
- Saat skill digunakan dalam percakapan nyata, agent harus memverifikasi struktur sheet yang ada sebelum operasi.
- Jika struktur sheet berbeda dari skema di atas, sesuaikan dan catat perbedaan di audit log.
- Buka workbook lewat `edsdk.py call open_file` (path garis miring `/`, `file_type=sheet`, `wait=true`), lalu baca dengan `mcp__sheetagent__read_table` memakai `file_id` hasil `open_file`. **Jangan** memakai `mcp__sheetagent__resolve_local_excel` untuk path absolut Windows — pada 5.9.3 tool itu menerima path tersebut tetapi mengembalikan `file_id` tanpa huruf drive (`/Users/...`), yang berbeda dari kunci `open_file`.
