# Panduan Agent - Quizify

Dokumen ini menjadi panduan kerja bagi AI agent dan kontributor saat mengembangkan Quizify. Perbarui dokumen ini jika keputusan produk atau arsitektur berubah.

## Tujuan proyek

Quizify adalah proyek website kuis. Kebutuhan produk, target pengguna, desain, dan fitur MVP belum ditentukan. Jangan menganggap fitur di bagian "Arah MVP yang diusulkan" sebagai keputusan final; klarifikasi kebutuhan yang berdampak besar sebelum mengimplementasikannya.

## Kondisi proyek saat ini

- Backend menggunakan Django 6.1.3.
- Project Django: `config`.
- App yang tersedia: `quizzes`.
- Database lokal: SQLite (`db.sqlite3`).
- Konfigurasi utama ada di `config/settings.py`; saat ini hanya URL admin yang terdaftar.
- `quizzes` belum dimasukkan ke `INSTALLED_APPS`.
- Model, view, dan test aplikasi masih berupa kerangka kosong.
- Frontend belum diimplementasikan; keputusan teknologinya tercantum di bagian "Keputusan frontend".
- Belum ada template aplikasi, dependensi proyek yang dikunci, atau spesifikasi produk.
- Folder `venv` tersedia secara lokal; jangan menganggap folder tersebut sebagai dependensi yang harus di-commit.

## Arah MVP yang diusulkan

Validasi alur produk dengan pemilik proyek sebelum membangun fitur yang memerlukan keputusan bisnis. Jika disetujui, urutan MVP yang masuk akal:

1. Halaman beranda dan daftar kuis yang tersedia.
2. Halaman detail kuis dan mulai mengerjakan kuis.
3. Pertanyaan pilihan ganda dan validasi jawaban di server.
4. Penghitungan skor dan halaman hasil.
5. Pembuatan serta pengelolaan kuis oleh admin/editor.
6. Akun pengguna dan riwayat pengerjaan hanya jika memang dibutuhkan.

Sebelum implementasi, tentukan minimal: siapa yang membuat kuis, siapa yang mengerjakan, apakah pengguna perlu login, tipe pertanyaan, aturan skor, dan apakah hasil/jawaban benar langsung ditampilkan.

## Keputusan frontend

- Gunakan Django Templates untuk rendering halaman.
- Gunakan Bootstrap 5 untuk styling dan responsive layout.
- Gunakan JavaScript untuk interaksi seperti timer dan navigasi soal.
- Setiap kuis memiliki batas waktu tetap 10 menit; timer dimulai saat peserta memulai kuis dan mengirim jawaban tersimpan saat waktu habis.
- Gunakan template inheritance dengan `base.html`.
- Pisahkan file CSS dan JavaScript ke folder `static`.
- Jangan menggunakan React atau frontend framework terpisah kecuali diminta secara eksplisit.

## Arsitektur aplikasi

Utamakan pemisahan tanggung jawab ala MVC agar kode mudah dibaca dan dirawat. Django menggunakan pola Model-Template-View (MTV), yang dapat dipetakan ke MVC seperti berikut:

- **Model** (`models.py`): struktur data, relasi, dan aturan domain yang terkait data.
- **Controller**: Django view (`views.py`) menangani request/response, validasi alur, dan koordinasi antara model dengan template. Hindari menaruh logika bisnis yang kompleks langsung di view.
- **View/presentation**: Django Templates merender antarmuka; CSS dan JavaScript berada di `static`.

Jangan menambahkan lapisan controller atau service terpisah secara otomatis. Jika logika bisnis tumbuh kompleks atau digunakan di beberapa alur, pisahkan ke modul/helper yang jelas di dalam app `quizzes` dan ikuti pola Django yang sudah ada.

## Pendekatan pembelajaran

- Kembangkan fitur secara bertahap; jangan mengimplementasikan seluruh MVP sekaligus.
- Sebelum mengubah kode, jelaskan tujuan perubahan serta file yang akan dibuat atau diubah.
- Jika pengguna meminta kode untuk suatu file, berikan isi file secara lengkap, bukan potongan yang terlepas dari konteks.
- Jangan mengubah kode yang sudah berjalan tanpa alasan yang relevan dengan permintaan.
- Selesaikan dan periksa tahap yang sedang dikerjakan sebelum melanjutkan ke fitur berikutnya. Jangan menganggap persetujuan untuk satu tahap sebagai persetujuan untuk mengerjakan tahap selanjutnya.

## Alur kerja pengembangan

1. **Pahami permintaan** — periksa kode dan tes terkait sebelum mengubah file. Pisahkan fakta yang sudah ada dari asumsi baru.
2. **Tentukan cakupan** — untuk keputusan produk atau perilaku yang ambigu, tanyakan kepada pemilik proyek. Untuk perubahan kecil yang sudah jelas, lanjutkan tanpa memperluas cakupan.
3. **Rancang perubahan terkecil** — jaga pemisahan tanggung jawab sesuai bagian "Arsitektur aplikasi". Hindari menambahkan framework, paket, atau lapisan arsitektur tanpa kebutuhan nyata.
4. **Implementasikan satu tahap** — sebelum mengubah kode, jelaskan tujuan dan file yang terdampak. Jaga perubahan tetap fokus. Untuk perubahan model, buat dan periksa migrasi; jangan mengubah atau menghapus data lokal secara destruktif.
5. **Uji tahap tersebut** — tambahkan tes untuk perilaku baru/perbaikan, lalu jalankan pemeriksaan Django dan tes yang relevan. Jangan mulai fitur berikutnya sebelum tahap saat ini selesai dan diperiksa.
6. **Laporkan** — jelaskan tujuan dan file yang dibuat/diubah, rangkum keputusan/asumsi penting, serta sebutkan hasil pemeriksaan yang benar-benar dijalankan.

## Pedoman teknis

- Gunakan Django conventions dan struktur app `quizzes`; daftarkan app di `INSTALLED_APPS` saat fitur app mulai dipakai.
- Tempatkan model/domain kuis di app yang sesuai. Pertahankan penamaan URL dengan `name` dan gunakan `{% url %}` di template jika template ditambahkan.
- Simpan kunci jawaban untuk penilaian di server; jangan mengirimkannya ke browser sebelum aturan produk secara eksplisit mengizinkan.
- Hitung skor dan validasi input di server, bukan hanya di JavaScript.
- Gunakan CSRF protection untuk form yang mengubah data dan otorisasi yang sesuai untuk operasi pengelolaan kuis.
- Gunakan migrasi Django untuk perubahan skema database. Jangan mengedit `db.sqlite3` secara langsung.
- Jangan menaruh secret atau kredensial di source code. Konfigurasi development dan production harus dibedakan sebelum deployment.
- Antarmuka baru harus responsif, dapat digunakan dengan keyboard, dan memiliki label/error form yang jelas.
- Jangan menambahkan fitur, dependensi, atau perubahan format database yang tidak diminta.

## Perintah development

Jalankan dari root proyek menggunakan interpreter virtual environment yang tersedia:

```powershell
.\venv\Scripts\python.exe manage.py check
.\venv\Scripts\python.exe manage.py test
.\venv\Scripts\python.exe manage.py runserver
```

Saat model berubah:

```powershell
.\venv\Scripts\python.exe manage.py makemigrations
.\venv\Scripts\python.exe manage.py migrate
```

Jika virtual environment atau dependensi berubah, perbarui dokumentasi dependensi proyek yang sesuai. Saat ini belum ada manifest dependensi proyek yang diketahui.

## Selesai jika

- Perubahan memenuhi cakupan yang diminta tanpa merusak alur yang sudah ada.
- Perubahan model disertai migrasi yang sesuai.
- Tes dan `manage.py check` yang relevan lulus, atau keterbatasan validasi disebutkan dengan jelas.
- Tidak ada secret, perubahan database lokal yang tidak diminta, atau dependensi tak terpakai yang tertinggal.
