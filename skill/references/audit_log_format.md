# Audit Log Format — PPA Smart Office Agent

## Struktur Audit Log

Setiap entri audit log harus mencakup field berikut:

```
[AUDIT LOG #<nomor>]
Timestamp T0 (simulasi) : <YYYY-MM-DD HH:MM:SS TZ>
Timestamp aktual (sistem): <YYYY-MM-DD HH:MM:SS TZ>
Tindakan        : <deskripsi tindakan>
Identitas Tugas : <Project ID + Task ID, atau N/A>
Status Agent    : <Draft|Pending Approval|Approved|Executed|Blocked|Failed>
File/Penerima   : <file atau penerima terdampak>
Persetujuan     : <referensi persetujuan user yang mendasari, atau N/A (belum ada)>
Baris           : <"Provisional (estimasi)" di tahap preview | "Aktual: <nomor>" hanya setelah eksekusi terverifikasi>
Nilai Sebelum   : <nilai data sebelum perubahan, atau N/A>
Nilai Sesudah   : <nilai data setelah perubahan, atau N/A>
Hasil Verifikasi: <Berhasil|Gagal|N/A (belum diverifikasi)>
Catatan         : <penjelasan>
Sumber Data     : <darimana data berasal>
```

## Contoh Entri Audit Log — Eksekusi Berhasil

> **Disclaimer:** Seluruh contoh di bawah bersifat **ilustratif** untuk menunjukkan format — **bukan** catatan historis, bukan bukti kejadian aktual, dan bukan klaim eksekusi nyata. Tanggal, nomor entri, dan nilai hanya pengisi format. Placeholder `[tidak tercatat — contoh ilustratif]` dipakai karena timestamp aktual contoh tidak diketahui.

```
[AUDIT LOG #001]
Timestamp T0 (simulasi) : 2026-10-23 09:15:00 WIB
Timestamp aktual (sistem): [tidak tercatat — contoh ilustratif]
Tindakan        : Tambah task baru "Pengumpulan dokumen IMB" ke Task_Tracker_PPA_TEST.xlsx
Identitas Tugas : PPA-2026-01 / T-015
Status Agent    : Executed
File/Penerima   : Task_Tracker_PPA_TEST.xlsx (Sheet: Tasks)
Persetujuan     : Disetujui user 2026-10-23 09:10 (kategori: pencatatan tugas baru)
Baris           : Aktual: 15
Nilai Sebelum   : N/A (baris baru)
Nilai Sesudah   : Project ID: PPA-2026-01 | Task ID: T-015 | PIC: Andi | Deadline: 2026-11-01 | Status: Not Started
Hasil Verifikasi: Berhasil
Catatan         : Baris baru ditambahkan sesuai preview yang disetujui. Verifikasi membaca ulang file, data sesuai.
Sumber Data     : Notulen rapat 2026-10-22
```

## Contoh Entri Audit Log — Eksekusi Gagal

```
[AUDIT LOG #002]
Timestamp T0 (simulasi) : 2026-10-23 09:20:00 WIB
Timestamp aktual (sistem): [tidak tercatat — contoh ilustratif]
Tindakan        : Update status task T-003 dari "Not Started" ke "In Progress"
Identitas Tugas : PPA-2026-01 / T-003
Status Agent    : Failed
File/Penerima   : Task_Tracker_PPA_TEST.xlsx (Sheet: Tasks)
Persetujuan     : Disetujui user 2026-10-23 09:18 (kategori: perubahan data existing)
Baris           : Aktual: 3 (target; tidak berubah)
Nilai Sebelum   : Status: Not Started
Nilai Sesudah   : Status: Not Started (tidak berubah)
Hasil Verifikasi: Gagal
Catatan         : Eksekusi gagal karena file Excel sedang dikunci oleh proses lain. Tindakan dikembalikan ke status Draft untuk dicoba ulang.
Sumber Data     : Instruksi user dalam percakapan
```

## Contoh Entri Audit Log — Tindakan Diblokir

```
[AUDIT LOG #003]
Timestamp T0 (simulasi) : 2026-10-23 09:25:00 WIB
Timestamp aktual (sistem): [tidak tercatat — contoh ilustratif]
Tindakan        : Kirim email tindak lanjut ke PIC task T-005
Identitas Tugas : PPA-2026-01 / T-005
Status Agent    : Blocked
File/Penerima   : Penerima: [PERLU KONFIRMASI]
Persetujuan     : N/A (belum ada — tindakan diblokir sebelum approval)
Baris           : N/A
Nilai Sebelum   : N/A
Nilai Sesudah   : N/A
Hasil Verifikasi: N/A (belum diverifikasi)
Catatan         : Tindakan diblokir karena identitas penerima tidak diketahui. Tidak boleh menebak identitas penerima. Draft email disiapkan, menunggu konfirmasi penerima.
Sumber Data     : Notulen rapat 2026-10-22
```

## Contoh Entri Audit Log — Tahap Preview (Provisional)

```
[AUDIT LOG #004]
Timestamp T0 (simulasi) : 2026-10-23 21:42:00 WIB
Timestamp aktual (sistem): [tidak tercatat — contoh ilustratif]
Tindakan        : Siapkan preview penambahan task T-005 ke Task_Tracker_PPA_TEST.xlsx
Identitas Tugas : PPA-2026-02 / T-005
Status Agent    : Pending Approval
File/Penerima   : Task_Tracker_PPA_TEST.xlsx (Sheet: Tasks)
Persetujuan     : N/A (menunggu persetujuan user)
Baris           : Provisional (estimasi; dihitung ulang saat eksekusi)
Nilai Sebelum   : N/A (baris baru)
Nilai Sesudah   : N/A (belum dieksekusi — lihat preview)
Hasil Verifikasi: N/A (belum diverifikasi)
Catatan         : Preview ditampilkan; menunggu persetujuan eksplisit user.
Sumber Data     : Notulen simulasi penguji #010
```

## Aturan Audit Log

1. **Catat semua tindakan** — baik yang berhasil maupun yang gagal/diblokir.
2. **Jujur** — Jangan menyembunyikan kegagalan atau masalah.
3. **Kronologis** — Entri log harus berurutan sesuai waktu.
4. **Lengkap** — Semua field harus diisi, gunakan "N/A" jika tidak relevan.
5. **Tidak menulis ke file eksternal** — Pada versi pertama, audit log disimpan dalam percakapan saja; jangan mengklaim log persisten.
6. **Verifikasi sebelum log** — Status "Executed" hanya jika verifikasi lulus; jika verifikasi gagal, gunakan "Failed".
7. **Provisional vs aktual** — Baris di tahap preview wajib berlabel "Provisional"; nomor baris aktual hanya dicatat setelah eksekusi terverifikasi.
8. **Append-only untuk temuan historis** — Temuan FAIL historis tidak dihapus atau diubah; koreksi ditulis sebagai entri baru yang mereferensikan entri awal.
9. **Dilarang mengklaim verifikasi yang belum dilakukan** — Field Hasil Verifikasi wajib diisi "N/A (belum diverifikasi)" sampai verifikasi benar-benar dilakukan.
10. **Timestamp ganda (T0 vs aktual)** — Setiap entri wajib mencatat `Timestamp T0 (simulasi)` dan `Timestamp aktual (sistem)` secara terpisah. T0 adalah acuan validasi (mis. penilaian deadline); timestamp aktual adalah waktu nyata entri dibuat. Bila keduanya berbeda, keduanya WAJIB dicantumkan — menulis hanya jam sistem sambil mengklaim T0 adalah audit tidak jujur. Untuk entri nyata, timestamp aktual harus berasal dari waktu kejadian yang benar-benar tercatat, **bukan nilai yang dikarang**; bila tidak tercatat, tulis `[tidak tercatat]`. Urutan kronologis (aturan #3) mengikuti T0.
