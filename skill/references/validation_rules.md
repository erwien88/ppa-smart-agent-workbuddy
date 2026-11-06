# Validation Rules — PPA Smart Office Agent

## Aturan Validasi Data

Agent harus melakukan validasi berikut pada tahap VALIDASI sebelum membuat preview.

## 1. Kelengkapan Data

Periksa apakah semua field wajib terisi:

| Field | Wajib | Jika Tidak Tersedia |
|-------|-------|---------------------|
| Project ID | Ya | Tandai "Tidak Diketahui" — tindakan diblokir |
| Task ID | Ya | Tandai "Tidak Diketahui" — tindakan diblokir |
| PIC | Ya | Tandai "Tidak Diketahui" — tindakan draft email diblokir |
| Deadline | Ya | Tandai "Tidak Diketahui" — penulisan diblokir. Deadline relatif yang belum terkonfirmasi juga memblokir penulisan (lihat §5) |
| Status Pekerjaan | Ya | Default: "Not Started" jika tugas baru |
| Sumber Informasi | Ya | Wajib diisi dari konteks input |
| Deskripsi Tugas | Ya | Tandai "Tidak Diketahui" — tindakan diblokir |

Catatan: PIC berupa jabatan atau tim (Drafter, Admin, Koordinator, Tim MEP, dll.) adalah PIC valid dan diperlakukan konsisten — tidak memblokir pencatatan. Blokir PIC hanya berlaku untuk tindakan pesan eksternal ketika identitas penerima individu belum terkonfirmasi.

## 2. Deteksi Duplikasi

Sebelum menambahkan tugas baru:
- Identitas duplikasi adalah pasangan **Project ID + Task ID** — periksa file Excel aktual untuk pasangan yang sama
- Kemiripan deskripsi dengan Project ID yang sama hanyalah sinyal peringatan (possible duplicate): tandai dan minta konfirmasi user, jangan langsung blokir
- Jika pasangan Project ID + Task ID sudah ada: tandai sebagai "Duplikasi" dan jangan tambahkan

## 3. Deteksi Ketidaksesuaian Data

Periksa konsistensi dengan data existing:
- Project ID harus konsisten dengan format yang ada di file
- PIC harus terdaftar (jika ada daftar PIC) — jika tidak terdaftar, tandai sebagai "PIC tidak dikenal"
- Deadline harus berupa tanggal yang valid dan tidak di masa lampau (untuk tugas baru)
- Status pekerjaan harus salah satu dari: Not Started, In Progress, Completed, On Hold

## 4. Deteksi Instruksi Ambigu

Instruksi dianggap ambigu jika:
- Terdapat lebih dari satu interpretasi yang masuk akal
- Project ID atau Task ID tidak jelas
- Tindakan yang diminta tidak spesifik (misal: "update data proyek" tanpa detail)

**Aturan PIC:** PIC berupa jabatan atau tim (mis. "Tim MEP", "Drafter") VALID untuk pencatatan tugas — bukan kategori ambigu. Ambiguitas PIC hanya relevan untuk tindakan pesan eksternal: identitas penerima individu harus spesifik dan terkonfirmasi sebelum pesan dikirim; jika tidak, tandai [PERLU KONFIRMASI].

Jika instruksi ambigu:
- Jangan menebak
- Tandai sebagai "Ambigu"
- Minta klarifikasi dari user (klarifikasi BUKAN persetujuan tindakan)

## 5. Deteksi Informasi Tidak Lengkap

Informasi dianggap tidak lengkap jika:
- Field wajib tidak tersedia di sumber
- Sumber data tidak jelas atau tidak dapat diverifikasi
- Deadline tidak spesifik (misal: "segera", "bulan depan" tanpa tanggal)
- PIC tidak teridentifikasi

Jika informasi tidak lengkap:
- Nyatakan "Tidak Diketahui" untuk field yang hilang
- Jangan mengarang data
- Lanjutkan ke preview hanya jika field kritis tersedia, atau hentikan tindakan

**Aturan deadline relatif:**
- Deadline relatif yang dapat diinterpretasikan (mis. "Jumat sore") wajib ditandai "Interpretasi: <usulan tanggal/jam> — PERLU KONFIRMASI"; dilarang menuliskannya sebagai nilai final
- Tugas dengan deadline wajib yang belum tersedia atau belum terkonfirmasi tetap berstatus Draft/Blocked untuk penulisan ke Excel
- Persetujuan update Excel tidak otomatis mengonfirmasi deadline ambigu

## 6. Hasil Validasi

Setelah semua pemeriksaan, susun laporan validasi dengan format:

```
[LAPORAN VALIDASI]

--- BAGIAN 1: INPUT VALIDATION (kualitas data, per tugas) ---
Project ID / Task ID / PIC / Deadline : <nilai | Tidak Diketahui | Interpretasi — PERLU KONFIRMASI>
[x] Kelengkapan    : <Lulus/Gagal — detail>
[x] Format         : <Lulus/Gagal — detail>
[x] Duplikasi (Project ID + Task ID) : <Lulus/Gagal — detail>
[x] Sumber informasi : <Lulus/Gagal — detail>

--- BAGIAN 2: AGENT BEHAVIOR (perilaku agent) ---
[x] Penolakan instruksi tidak sah       : <Lulus/Gagal>
[x] Kontrol izin (persetujuan/tindakan) : <Lulus/Gagal>
[x] Batas akses (workspace, no email)   : <Lulus/Gagal>
[x] Eksekusi sesuai lingkup persetujuan : <Lulus/Gagal>
[x] Audit log jujur dan lengkap         : <Lulus/Gagal>

Status Validasi: <Lulus/Diblokir> (untuk penulisan)
Catatan: FAIL kualitas input tidak otomatis berarti agent gagal berperilaku.
```

## Aturan Kritis

- Jika pemeriksaan gagal pada field kritis (Project ID, Task ID, Deskripsi): **hentikan tindakan**.
- Jika data tidak tersedia: nyatakan "Tidak Diketahui", jangan mengarang.
- Klarifikasi dari user BUKAN persetujuan tindakan.
- Jangan menambahkan tugas yang gagal validasi ke Excel.
- Jangan menyiapkan draft email jika PIC tidak diketahui.
- FAIL pada Input Validation tidak otomatis berarti FAIL pada Agent Behavior — laporkan terpisah.
- Persetujuan update Excel tidak otomatis mengonfirmasi deadline ambigu.
- Duplikasi ditentukan oleh pasangan Project ID + Task ID.
