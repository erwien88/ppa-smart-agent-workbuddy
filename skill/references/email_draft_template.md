# Email Draft Template — PPA Smart Office Agent

## Struktur Draft Email

Draft email yang disiapkan oleh agent harus mengikuti format berikut:

```
=========================================
DRAFT EMAIL (TIDAK DIKIRIM — PERLU APPROVAL)
=========================================

Kepada       : <email penerima atau [PERLU KONFIRMASI]>
Cc           : <email cc atau kosong>
Subjek       : <subjek email>

Isi Email:
-----------
<isi email dalam Bahasa Indonesia>

Salam,
<nama pengirim atau [PERLU KONFIRMASI]>
-----------

=========================================
Status: Draft — Menunggu Persetujuan
Catatan: Email ini hanya draf. Tidak akan dikirim nyata pada versi pertama.
=========================================
```

## Aturan Draft Email

1. **Penerima harus diketahui** — Jika identitas penerima tidak tersedia di sumber data, tandai sebagai `[PERLU KONFIRMASI]`. Jangan menebak identitas penerima.
2. **Bahasa Indonesia** — Semua draft email menggunakan Bahasa Indonesia.
3. **Hanya di chat** — Pada versi pertama, draft email hanya ditampilkan dalam percakapan. Tidak ada pengiriman email nyata.
4. **Persetujuan terpisah** — Persetujuan untuk draft email **tidak** mengizinkan update Excel atau tindakan lain.
5. **Sertakan konteks** — Setiap draft email harus menyebutkan:
   - Project ID yang relevan
   - Task ID yang relevan
   - Tujuan email (tindak lanjut, pengingat, permintaan info, dll.)
6. **Jangan mengarang progres** — Hanya sebutkan status yang terverifikasi dari data.
7. **Sumber data** — Cantumkan sumber data yang mendasari draft email di catatan di luar draft.

## Contoh Draft Email — Tindak Lanjut Tugas

```
=========================================
DRAFT EMAIL (TIDAK DIKIRIM — PERLU APPROVAL)
=========================================

Kepada       : [PERLU KONFIRMASI]
Cc           :
Subjek       : Tindak Lanjut Task T-005 — Pengumpulan Dokumen SLF (PPA-2026-01)

Isi Email:
-----------
Yth. Penanggung Jawab Task T-005,

Mengacu pada notulen rapat tanggal 22 Oktober 2026 untuk proyek PPA-2026-01,
diberitahukan bahwa Task T-005 (Pengumpulan Dokumen SLF) memiliki tenggat
waktu pada tanggal 1 November 2026.

Saat ini status tugas tercatat sebagai "Not Started". Mohon konfirmasi
progress terkini dan estimasi waktu penyelesaian.

Apabila ada hambatan atau informasi tambahan yang diperlukan, silakan
menghubungi koordinator proyek.

Salam,
[PERLU KONFIRMASI]
-----------

=========================================
Status: Draft — Menunggu Persetujuan
Sumber Data: Notulen rapat 2026-10-22, Task_Tracker_PPA_TEST.xlsx
Catatan:
- Identitas penerima tidak diketahui, perlu konfirmasi
- Email ini hanya draf, tidak akan dikirim nyata pada versi pertama
- Persetujuan draft ini tidak mengizinkan update Excel
=========================================
```

## Contoh Draft Email — Pengingat Deadline

```
=========================================
DRAFT EMAIL (TIDAK DIKIRIM — PERLU APPROVAL)
=========================================

Kepada       : [PERLU KONFIRMASI]
Cc           :
Subjek       : Pengingat: Task T-012 — Review Dokumen PBG (PPA-2026-02) Jatuh Tempo 5 November 2026

Isi Email:
-----------
Yth. Penanggung Jawab Task T-012,

Diberitahukan bahwa Task T-012 (Review Dokumen PBG) untuk proyek
PPA-2026-02 memiliki tenggat waktu pada tanggal 5 November 2026.

Sesuai data terbaru, status tugas tercatat sebagai "In Progress".
Mohon pastikan penyelesaian tepat waktu atau informasikan apabila
ada hambatan yang memerlukan tindak lanjut.

Salam,
[PERLU KONFIRMASI]
-----------

=========================================
Status: Draft — Menunggu Persetujuan
Sumber Data: Task_Tracker_PPA_TEST.xlsx (baris 12)
Catatan:
- Identitas penerima tidak diketahui, perlu konfirmasi
- Email ini hanya draf, tidak akan dikirim nyata pada versi pertama
=========================================
```
