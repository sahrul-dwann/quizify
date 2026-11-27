from django.db import migrations, models


QUIZ_TITLE = 'JavaScript Basic'
QUIZ_DESCRIPTION = (
    '20 soal dasar JavaScript tentang variabel, tipe data, operator, '
    'array, object, fungsi, dan DOM.'
)
QUESTIONS = [
    (
        'Kata kunci mana yang digunakan untuk membuat variabel yang nilainya '
        'dapat diubah dan cakupannya berada di dalam blok?',
        ['let', 'const', 'return', 'static'],
        0,
    ),
    (
        'Apa yang terjadi jika nilai variabel yang dideklarasikan dengan '
        '`const` diubah?',
        [
            'Nilainya berubah seperti biasa',
            'JavaScript melempar TypeError',
            'Variabel otomatis menjadi `let`',
            'Program selalu mengembalikan `null`',
        ],
        1,
    ),
    (
        'Apa hasil dari `typeof "Halo"`?',
        ['"text"', '"string"', '"char"', '"object"'],
        1,
    ),
    (
        'Apa perbedaan utama antara operator `==` dan `===`?',
        [
            '`===` membandingkan nilai dan tipe tanpa konversi tipe',
            '`==` hanya dapat membandingkan angka',
            '`===` selalu mengubah kedua nilai menjadi string',
            'Tidak ada perbedaan',
        ],
        0,
    ),
    (
        'Apa hasil dari ekspresi JavaScript `2 + "3"`?',
        ['5', '"23"', '23 sebagai number', 'NaN'],
        1,
    ),
    (
        'Apa hasil dari `Number("42")`?',
        ['String "42"', 'Angka 42', 'Boolean true', 'NaN'],
        1,
    ),
    (
        'Apa hasil dari `Boolean(0)`?',
        ['true', 'false', '0', 'null'],
        1,
    ),
    (
        'Manakah contoh literal array yang benar di JavaScript?',
        ['("merah", "biru")', '{"merah", "biru"}', '["merah", "biru"]', '<"merah", "biru">'],
        2,
    ),
    (
        'Pada array JavaScript, indeks elemen pertama adalah ...',
        ['0', '1', '-1', 'Bergantung pada isi array'],
        0,
    ),
    (
        'Apa hasil dari `["apel", "jeruk"].length`?',
        ['1', '2', '10', 'undefined'],
        1,
    ),
    (
        'Method apa yang menambahkan satu atau lebih elemen ke akhir array?',
        ['shift()', 'push()', 'pop()', 'slice()'],
        1,
    ),
    (
        'Jika `const user = { nama: "Ayu" }`, bagaimana cara mengakses nilai '
        'properti `nama`?',
        ['user->nama', 'user.nama', 'user[nama()]', 'nama.user'],
        1,
    ),
    (
        'Apa fungsi kata kunci `return` di dalam fungsi?',
        [
            'Mengembalikan nilai dari fungsi dan mengakhiri pemanggilan fungsi',
            'Menampilkan nilai ke halaman web',
            'Mengulang fungsi dari awal',
            'Mendeklarasikan variabel global',
        ],
        0,
    ),
    (
        'Manakah contoh arrow function yang menjumlahkan `a` dan `b`?',
        [
            'const tambah = (a, b) => a + b;',
            'const tambah => (a, b) a + b;',
            'function => tambah(a, b) { a + b }',
            'const tambah = (a, b) then a + b;',
        ],
        0,
    ),
    (
        'Berapa kali perulangan berikut dijalankan? '
        '`for (let i = 0; i < 3; i++)`',
        ['2 kali', '3 kali', '4 kali', 'Tidak pernah'],
        1,
    ),
    (
        'Apa hasil dari `5 !== "5"`?',
        ['true', 'false', '5', 'TypeError'],
        0,
    ),
    (
        'Method apa yang memeriksa apakah sebuah nilai merupakan array?',
        ['Array.isArray(nilai)', 'nilai.isArray()', 'typeof nilai === "array"', 'is_array(nilai)'],
        0,
    ),
    (
        'Perintah apa yang umum digunakan untuk menampilkan informasi di '
        'console browser?',
        ['console.log()', 'window.printText()', 'document.writeConsole()', 'alert.log()'],
        0,
    ),
    (
        'Apa yang dikembalikan oleh `document.querySelector("#judul")`?',
        [
            'Elemen pertama yang cocok dengan selector CSS tersebut',
            'Semua elemen yang cocok dalam bentuk array',
            'Teks dari seluruh halaman',
            'Selalu membuat elemen baru dengan id tersebut',
        ],
        0,
    ),
    (
        'Apa hasil dari `typeof true`?',
        ['"boolean"', '"bool"', '"number"', '"true"'],
        0,
    ),
]


def seed_javascript_basic_quiz(apps, schema_editor):
    database = schema_editor.connection.alias
    Quiz = apps.get_model('quizzes', 'Quiz')
    Question = apps.get_model('quizzes', 'Question')
    AnswerOption = apps.get_model('quizzes', 'AnswerOption')

    quizzes = Quiz.objects.using(database)
    if quizzes.filter(title=QUIZ_TITLE).exists():
        return

    quiz = quizzes.create(
        title=QUIZ_TITLE,
        description=QUIZ_DESCRIPTION,
        duration_minutes=15,
        is_published=True,
    )
    for order, (question_text, option_texts, correct_index) in enumerate(QUESTIONS, 1):
        question = Question.objects.using(database).create(
            quiz_id=quiz.pk,
            text=question_text,
            order=order,
        )
        AnswerOption.objects.using(database).bulk_create(
            [
                AnswerOption(
                    question_id=question.pk,
                    text=option_text,
                    is_correct=index == correct_index,
                )
                for index, option_text in enumerate(option_texts)
            ]
        )


class Migration(migrations.Migration):

    dependencies = [
        ('quizzes', '0004_seed_programming_quiz'),
    ]

    operations = [
        migrations.AddField(
            model_name='quiz',
            name='duration_minutes',
            field=models.PositiveIntegerField(default=10),
        ),
        migrations.RunPython(
            seed_javascript_basic_quiz,
            migrations.RunPython.noop,
        ),
    ]
