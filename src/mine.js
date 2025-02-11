async function upgradeCard(cardType) {
    const userId = document.querySelector('meta[name="user-id"]').content;
    const response = await fetch('/upgrade_card', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ user_id: userId, card_type: cardType }),
    });

    if (response.ok) {
        showCopyNotification()
        location.reload();
    } else {
        showCopyNotificationFalse()
    }
}


function showCopyNotification() {
    const notification = document.getElementById('copy-notification');
    notification.style.display = 'block';

    setTimeout(() => {
        notification.style.display = 'none';
    }, 2000);
}

function showCopyNotificationFalse() {
    const notification = document.getElementById('copy-notification-false');
    notification.style.display = 'block';

    setTimeout(() => {
        notification.style.display = 'none';
    }, 2000);
}

exit = document.getElementById('exit').addEventListener('click', function(){
    upgrade = document.getElementById('upgradesite')
    upgrade.style.display = 'none';
}
)
