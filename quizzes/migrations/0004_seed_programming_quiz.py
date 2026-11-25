from django.db import migrations


QUIZ_TITLE = 'Pemrograman Dasar hingga Menengah'
QUIZ_DESCRIPTION = (
    '10 soal tentang variabel, logika, perulangan, fungsi, struktur data, '
    'dan analisis algoritma.'
)
QUESTIONS = [
    (
        'Jika angka = 7 lalu angka = angka + 5, berapa nilai akhir angka?',
        ['10', '12', '35', '75'],
        1,
    ),
    (
        'Apa hasil dari ekspresi logika NOT (TRUE AND FALSE)?',
        ['TRUE', 'FALSE', 'NULL', 'Error'],
        0,
    ),
    (
        'Jika total dimulai dari 0 lalu ditambah i untuk i = 1, 2, 3, 4, '
        'berapa nilai akhir total?',
        ['4', '6', '10', '15'],
        2,
    ),
    (
        'Apa fungsi utama perintah return di dalam sebuah fungsi?',
        [
            'Mengirim nilai kembali dari fungsi dan mengakhiri eksekusinya',
            'Menampilkan nilai langsung ke layar',
            'Mengulang fungsi tanpa batas',
            'Menghapus semua variabel program',
        ],
        0,
    ),
    (
        'Dalam bahasa dengan indeks list dimulai dari 0, indeks elemen pertama adalah ...',
        ['0', '1', '-1', 'Sama dengan jumlah seluruh elemen'],
        0,
    ),
    (
        'Struktur data map berisi {"nama": "Ayu"}. Nilai yang diakses dengan kunci "nama" adalah ...',
        ['Ayu', 'nama', 'Map', 'Tidak ada nilai'],
        0,
    ),
    (
        'Mengapa fungsi rekursif perlu memiliki kondisi dasar (base case)?',
        [
            'Agar pemanggilan rekursif berhenti pada kondisi tertentu',
            'Agar fungsi selalu berjalan lebih dari sekali',
            'Agar semua variabel menjadi global',
            'Agar fungsi tidak menerima parameter',
        ],
        0,
    ),
    (
        'Sebuah algoritma menjalankan dua perulangan bersarang, masing-masing '
        'sebanyak n kali. Bagaimana kompleksitas waktunya?',
        ['O(n)', 'O(log n)', 'O(n^2)', 'O(1)'],
        2,
    ),
    (
        'Dalam kasus terburuk, berapa kompleksitas pencarian linear pada list '
        'dengan n elemen?',
        ['O(1)', 'O(log n)', 'O(n)', 'O(n^2)'],
        2,
    ),
    (
        'Pernyataan yang tepat tentang binary search adalah ...',
        [
            'Memerlukan data terurut dan membagi ruang pencarian menjadi dua '
            'di setiap langkah',
            'Dapat digunakan pada data acak tanpa urutan dengan kompleksitas O(1)',
            'Selalu memeriksa setiap elemen satu per satu',
            'Hanya dapat digunakan pada struktur data map',
        ],
        0,
    ),
]


def seed_programming_quiz(apps, schema_editor):
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
        ('quizzes', '0003_alter_quizattempt_options_quizattempt_started_at_and_more'),
    ]

    operations = [
        migrations.RunPython(seed_programming_quiz, migrations.RunPython.noop),
    ]
