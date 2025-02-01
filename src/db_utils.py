from models import session, User

from models import session, User


def add_user(user_id, username, ref_link=None, referrer_id=None):
    try:
        existing_user = get_user(user_id)
        if existing_user:
            print(f"User {username} already exists in the database.")
            return existing_user

        user = User(user_id=user_id, username=username, ref_link=ref_link)
        session.add(user)
        session.commit()
        print(f"User {username} added successfully.")

        # Обновляем информацию о пригласившем, если есть referrer_id
        if referrer_id:
            update_invited_friends(referrer_id, user_id)

        return user
    except Exception as e:
        session.rollback()
        print(f"Error adding user {username}: {e}")
        return None


def update_invited_friends(referrer_id, invitee_user_id):
    try:
        referrer = get_user(referrer_id)
        invitee = get_user(invitee_user_id)
        if referrer and invitee:
            referrer.invited_friends += 1
            if referrer.friends_usernames:
                referrer.friends_usernames += f",{invitee.username}"
            else:
                referrer.friends_usernames = invitee.username
            session.commit()
            print(f"User {referrer.username} invited {invitee.username} successfully.")
        else:
            print(f"Referrer or invitee not found.")
    except Exception as e:
        session.rollback()
        print(f"Error updating invited friends: {e}")

def award_referral_bonus(invitee_user_id, referrer_id, premium=False):
    try:
        invitee = get_user(invitee_user_id)
        referrer = get_user(referrer_id)
        if invitee and referrer:
            bonus = 25000 if premium else 5000
            invitee.coins += bonus
            referrer.coins += bonus

            update_user_coins(invitee_user_id, bonus)
            update_user_coins(referrer_id, bonus)
            session.commit()
            print(f"Awarded {bonus} coins to {invitee.username} and {referrer.username}.")
        else:
            print("Invitee or referrer not found.")
    except Exception as e:
        session.rollback()
        print(f"Error awarding referral bonus: {e}")


def get_user(user_id):
    try:
        return session.query(User).filter_by(user_id=user_id).first()
    except Exception as e:
        print(f"Error fetching user with user_id={user_id}: {e}")
        return None


def update_user_coins(user_id, coins):
    try:
        user = get_user(user_id)
        if user:
            user.coins = coins
            session.commit()
            print(f"User {user.username}'s coins updated to {coins}.")
        else:
            print(f"No user found with user_id={user_id}.")
    except Exception as e:
        session.rollback()
        print(f"Error updating coins for user {user_id}: {e}")

def update_profit_per_hour(user_id, profit):
    try:
        user = get_user(user_id)
        if user:
            user.profit_per_hour = profit
            session.commit()
            print(f"User {user.username}'s profit_per_hour updated to {profit}.")
        else:
            print(f"No user found with user_id={user_id}.")
    except Exception as e:
        session.rollback()
        print(f"Error updating profit_per_hour for user {user_id}: {e}")

def update_profit_per_tap(user_id, profit):
    try:
        user = get_user(user_id)
        if user:
            user.profit_per_tap = profit
            session.commit()
            print(f"User {user.username}'s profit_per_tap updated to {profit}.")
        else:
            print(f"No user found with user_id={user_id}.")
    except Exception as e:
        session.rollback()
        print(f"Error updating profit_per_tap for user {user_id}: {e}")

# Debugging Helper
if __name__ == "__main__":
    # Example usage
    user_id = 1
    username = "test_user"
    ref_link = "http://example.com/ref/1"

    # Add user
    add_user(user_id, username, ref_link)

    # Update coins
    update_user_coins(user_id, 100)

    # Fetch user and print
    user = get_user(user_id)
    if user:
        print(user)

    # Update profit
    update_profit_per_hour(user_id, 50.0)
    update_profit_per_tap(user_id, 2.5)