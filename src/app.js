document.addEventListener('DOMContentLoaded', async () => {
    const hamster = document.getElementById('hamster');
    const scoreElement = document.getElementById('score');
    const coinsToUpElement = document.getElementById('coins-to-up');
    const progressBar = document.querySelector('.level-progress');
    const levelText = document.querySelector('.level-text');
    const tapProfitElement = document.querySelector('#tap ~ .stat-value');
    const hourProfitElement = document.querySelector('#hourse ~ .stat-value');
    const userId = document.querySelector('meta[name="user-id"]').content;

    let score = 0;
    let profitPerTap = 1;
    let profitPerHour = 0;
    let level = 1;

    // Уровневые пороги
    const levelThresholds = [
        0,          // Уровень 1
        5000,       // Уровень 2
        25000,      // Уровень 3
        100000,     // Уровень 4
        1000000,    // Уровень 5
        2000000,    // Уровень 6
        10000000,   // Уровень 7
        50000000,   // Уровень 8
        1000000000, // Уровень 9
        10000000000 // Уровень 10

    ];

    // Функция расчета текущего уровня
    function calculateLevel(score) {
        for (let i = levelThresholds.length - 1; i >= 0; i--) {
            if (score >= levelThresholds[i]) {
                return i + 1;
            }
        }
        return 1;
    }

    // Функция расчета прогресса
    function calculateProgress(score, level) {
        const currentLevelThreshold = levelThresholds[level - 1];
        const nextLevelThreshold = levelThresholds[level] || currentLevelThreshold;

        const progress = ((score - currentLevelThreshold) / (nextLevelThreshold - currentLevelThreshold)) * 100;
        return Math.min(Math.max(progress, 0), 100);
    }

    // Функция расчета монет до следующего уровня
    function calculateCoinsToNextLevel(score, level) {
        const nextLevelThreshold = levelThresholds[level] || Infinity;
        const coinsToNextLevel = nextLevelThreshold;

        // Если максимальный уровень достигнут
        return coinsToNextLevel > 0 ? coinsToNextLevel : 0;
    }

    // Функция обновления уровня, прогресса и монет для апа
    function updateLevelProgressAndCoins() {
        const newLevel = calculateLevel(score);

        // Уровень не должен понижаться
        if (newLevel > level) {
            level = newLevel;
        }

        if (level >= levelThresholds.length) {
            // Максимальный уровень
            levelText.innerText = `Level ${level}/10`;
            progressBar.style.width = `100%`; // Полный прогресс бар
            coinsToUpElement.innerText = "Maximum level"; // Текст для максимального уровня
        } else {
            // Рассчитываем прогресс и монеты до следующего уровня
            const progress = calculateProgress(score, level);
            const coinsToNextLevel = calculateCoinsToNextLevel(score, level);

            levelText.innerText = `Level ${level}/10`;
            progressBar.style.width = `${progress}%`;
            coinsToUpElement.innerText = coinsToNextLevel; // Обновляем монеты до следующего уровня
        }
    }


    // Функция получения данных пользователя
    async function fetchUserData() {
        try {
            const response = await fetch(`/user_data?user_id=${userId}`);
            const data = await response.json();

            if (response.ok && data.success) {
                score = data.coins;
                profitPerTap = data.profit_per_tap;
                profitPerHour = data.profit_per_hour;

                scoreElement.innerText = score;
                tapProfitElement.innerText = `+${profitPerTap}`;
                hourProfitElement.innerText = profitPerHour;

                updateLevelProgressAndCoins();

                console.log('User data loaded successfully:', data);
            } else {
                console.error('Failed to load user data:', data.error);
            }
        } catch (error) {
            console.error('Error fetching user data:', error);
        }
    }

    // Функция для обновления монет на сервере
    async function updateCoinsOnServer() {
        try {
            const response = await fetch('/update_coins', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'User-ID': userId
                },
                body: JSON.stringify({ coins: score })
            });

            const data = await response.json();

            if (!response.ok || !data.success) {
                console.error('Error updating coins:', data.error || 'Unknown error');
            } else {
                console.log('Coins updated successfully:', data);
            }
        } catch (error) {
            console.error('Network error while updating coins:', error);
        }
    }

    // Обработчик клика на хомяка
    hamster.addEventListener('click', (event) => {
        const rect = hamster.getBoundingClientRect();
        const offsetX = event.clientX - rect.left - rect.width / 2;
        const offsetY = event.clientY - rect.top - rect.height / 2;
        const DEG = 40;
        const tiltX = (offsetY / rect.height) * DEG;
        const tiltY = (offsetX / rect.width) * -DEG;

        hamster.style.setProperty('--tiltX', `${tiltX}deg`);
        hamster.style.setProperty('--tiltY', `${tiltY}deg`);

        setTimeout(() => {
            hamster.style.setProperty('--tiltX', `0deg`);
            hamster.style.setProperty('--tiltY', `0deg`);
        }, 300);
        score += profitPerTap;
        scoreElement.innerText = score;

        updateLevelProgressAndCoins();
        updateCoinsOnServer();

        // Анимация "+X"
        const plusOne = document.createElement('div');
        plusOne.className = 'floating-plus-one';
        plusOne.innerText = `+${profitPerTap}`;
        plusOne.style.left = `${event.clientX}px`;
        plusOne.style.top = `${event.clientY}px`;

        document.body.appendChild(plusOne);

        setTimeout(() => {
            document.body.removeChild(plusOne);
        }, 1000);
    });

    // Авто-добавление пассивного дохода
//    setInterval(() => {
//        score += profitPerHour / 3600; // Добавляем доход каждую секунду
//        score = Math.floor(score);
//        scoreElement.innerText = score;
//
//        updateLevelProgressAndCoins();
//        updateCoinsOnServer();
//    }, 1000);

    // Загрузка данных при старте
    await fetchUserData();
});
