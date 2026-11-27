document.addEventListener('DOMContentLoaded', function () {
    const form = document.querySelector('[data-quiz-form]');
    if (!form) {
        return;
    }

    const countdown = document.querySelector('[data-countdown]');
    const saveStatus = document.querySelector('[data-save-status]');
    const csrfToken = form.querySelector('[name=csrfmiddlewaretoken]').value;
    const navigationButtons = form.querySelectorAll('[data-question-target]');
    const questionCards = form.querySelectorAll('.question-card[id]');
    let pendingSaves = Promise.resolve();
    let saveFailed = false;
    let isFinishing = false;
    let timerId = null;

    function markAnswered(question) {
        const navigationButton = form.querySelector(
            `[data-question-target="${question.id}"]`,
        );
        if (!navigationButton) {
            return;
        }

        navigationButton.classList.remove('btn-outline-primary');
        navigationButton.classList.add('btn-secondary');
        navigationButton.setAttribute(
            'aria-label',
            `Soal ${navigationButton.textContent.trim()}, sudah dijawab`,
        );
    }

    function markCurrent(question) {
        navigationButtons.forEach(function (button) {
            button.classList.remove('is-current');
            button.removeAttribute('aria-current');
        });

        const currentButton = form.querySelector(
            `[data-question-target="${question.id}"]`,
        );
        if (currentButton) {
            currentButton.classList.add('is-current');
            currentButton.setAttribute('aria-current', 'step');
        }
    }

    if (questionCards.length > 0) {
        markCurrent(questionCards[0]);
        const questionObserver = new IntersectionObserver(function (entries) {
            const visibleQuestions = entries
                .filter(function (entry) {
                    return entry.isIntersecting;
                })
                .sort(function (first, second) {
                    return first.boundingClientRect.top - second.boundingClientRect.top;
                });
            if (visibleQuestions.length > 0) {
                markCurrent(visibleQuestions[0].target);
            }
        }, {
            rootMargin: '-230px 0px -180px 0px',
        });
        questionCards.forEach(function (question) {
            questionObserver.observe(question);
        });
    }

    navigationButtons.forEach(function (button) {
        button.addEventListener('click', function () {
            const target = document.getElementById(button.dataset.questionTarget);
            if (!target) {
                return;
            }

            markCurrent(target);
            target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            target.focus({ preventScroll: true });
        });
    });

    form.querySelectorAll('input[type="radio"]:checked').forEach(function (input) {
        const question = input.closest('fieldset[id]');
        if (question) {
            markAnswered(question);
        }
    });

    function submitAttempt() {
        if (isFinishing) {
            return;
        }

        isFinishing = true;
        window.clearInterval(timerId);
        form.querySelectorAll('input[type="radio"]').forEach(function (input) {
            input.disabled = true;
        });
        pendingSaves.then(function () {
            form.submit();
        });
    }

    form.addEventListener('change', function (event) {
        if (!(event.target instanceof HTMLInputElement) || event.target.type !== 'radio') {
            return;
        }

        const question = event.target.closest('fieldset[id]');
        if (!question) {
            return;
        }

        markAnswered(question);
        saveFailed = false;
        saveStatus.textContent = 'Menyimpan jawaban...';
        pendingSaves = pendingSaves
            .then(function () {
                return fetch(form.dataset.saveUrl, {
                    method: 'POST',
                    credentials: 'same-origin',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'X-CSRFToken': csrfToken,
                    },
                    body: new URLSearchParams({
                        question_id: question.id.replace('question_', ''),
                        option_id: event.target.value,
                    }),
                }).then(function (response) {
                    if (response.status === 410) {
                        saveStatus.textContent = 'Waktu habis. Mengirim jawaban...';
                        submitAttempt();
                        return;
                    }
                    if (!response.ok) {
                        throw new Error('Jawaban tidak dapat disimpan.');
                    }
                    saveStatus.textContent = 'Jawaban tersimpan.';
                });
            })
            .catch(function () {
                saveFailed = true;
                saveStatus.textContent =
                    'Jawaban belum tersimpan. Periksa koneksi lalu pilih kembali jawaban.';
            });
    });

    form.addEventListener('submit', function (event) {
        if (isFinishing) {
            return;
        }

        event.preventDefault();
        if (saveFailed) {
            saveStatus.textContent =
                'Jawaban belum tersimpan. Periksa koneksi lalu coba lagi.';
            return;
        }

        submitAttempt();
    });

    let remainingSeconds = Number(countdown.dataset.remainingSeconds);
    function renderCountdown() {
        const minutes = Math.floor(remainingSeconds / 60);
        const seconds = remainingSeconds % 60;
        countdown.textContent = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
        if (remainingSeconds <= 60) {
            countdown.closest('.timer-panel').classList.add('is-urgent');
        }
    }

    renderCountdown();
    if (remainingSeconds <= 0) {
        submitAttempt();
        return;
    }

    timerId = window.setInterval(function () {
        remainingSeconds -= 1;
        renderCountdown();
        if (remainingSeconds <= 0) {
            window.clearInterval(timerId);
            saveStatus.textContent = 'Waktu habis. Mengirim jawaban...';
            submitAttempt();
        }
    }, 1000);
});
