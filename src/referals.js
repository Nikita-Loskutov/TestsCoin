// Функция для отображения рефералов
async function displayReferrals() {
    const userId = document.querySelector('meta[name="user-id"]').content;
    const referralsContainer = document.getElementById("referrals-list");
    const invitedFriendsCountElement = document.getElementById("invited-friends-count");

    try {
        const response = await fetch(`/invited_friends?user_id=${userId}`);
        const data = await response.json();

        if (response.ok && data.success) {
            const referrals = data.referrals;
            referralsContainer.innerHTML = ''; // Очистить контейнер перед добавлением новых элементов
            referrals.forEach(referral => {
                // Создаем блок для каждого реферала
                const referralBlock = document.createElement("div");
                referralBlock.className = "refblock";
                referralBlock.innerHTML = `
                    <img src="assets/user.png">
                    <h3>${referral.name}</h3>
                `;
                referralsContainer.appendChild(referralBlock);
            });

            invitedFriendsCountElement.innerText = referrals.length; // Обновить количество приглашенных друзей
        } else {
            console.error('Failed to load referrals:', data.error);
        }
    } catch (error) {
        console.error('Error fetching referrals:', error);
    }
}

// Вызываем функцию для отображения рефералов
displayReferrals();