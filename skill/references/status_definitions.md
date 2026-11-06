# Status Definitions — PPA Smart Office Agent

## A. Status Pekerjaan (Work Status)

Status pekerjaan mencerminkan kondisi pekerjaan aktual di lapangan/proyek.

| Status | Definisi | Kriteria |
|--------|----------|----------|
| Not Started | Pekerjaan belum dimulai | Task sudah dibuat, belum ada aktivitas pelaksanaan |
| In Progress | Pekerjaan sedang berjalan | Sudah ada aktivitas pelaksanaan, belum selesai |
| Completed | Pekerjaan selesai | Semua deliverable terpenuhi dan terverifikasi |
| On Hold | Pekerjaan ditangguhkan | Ada hambatan atau menunggu keputusan/keterangan tambahan |

## B. Status Tindakan Agent (Agent Action Status)

Status tindakan agent mencerminkan status dari setiap tindakan yang akan atau sudah dilakukan oleh agent.

| Status | Definisi | Kriteria |
|--------|----------|----------|
| Draft | Tindakan sedang disiapkan | Agent sedang menyusun preview atau draft tindakan |
| Pending Approval | Menunggu persetujuan manusia | Preview telah ditampilkan, menunggu keputusan user |
| Approved | Disetujui oleh manusia | User memberikan persetujuan eksplisit untuk tindakan tersebut |
| Executed | Tindakan telah dieksekusi | Tindakan telah dilakukan dan hasil telah diverifikasi |
| Blocked | Tindakan terhambat | Ada hambatan teknis, data tidak lengkap, atau dependensi belum terpenuhi |
| Failed | Tindakan gagal | Eksekusi gagal atau hasil verifikasi tidak sesuai |

## Aturan Transisi Status

### Work Status
- Not Started → In Progress: Saat aktivitas pelaksanaan dimulai
- In Progress → Completed: Saat semua deliverable terverifikasi
- In Progress → On Hold: Saat ada hambatan atau keputusan tertunda
- On Hold → In Progress: Saat hambatan teratasi
- Completed → In Progress: **Tidak diizinkan** (gunakan task baru jika revisi diperlukan)

### Agent Action Status
- Draft → Pending Approval: Saat preview ditampilkan ke user
- Pending Approval → Approved: Saat user memberikan persetujuan eksplisit
- Pending Approval → Blocked: Jika data baru mengubah kelayakan tindakan
- Approved → Executed: Setelah eksekusi berhasil dan verifikasi lulus
- Approved → Failed: Jika eksekusi gagal atau verifikasi tidak lulus
- Approved → Blocked: Jika kondisi berubah sebelum eksekusi
- Blocked → Draft: Setelah hambatan teratasi, buat draft baru
- Failed → Draft: Setelah koreksi dilakukan, buat draft baru

## Catatan Penting

- Status "Approved" hanya berlaku untuk satu tindakan spesifik, bukan rangkaian tindakan.
- Persetujuan untuk update Excel **tidak** mengizinkan pengiriman email.
- Persetujuan untuk draft email **tidak** mengizinkan update Excel.
- Setiap tindakan eksternal membutuhkan persetujuan eksplisit terpisah.
- Klarifikasi pertanyaan **bukan** persetujuan tindakan.
