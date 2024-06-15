from datetime import datetime, timedelta


async def subs_calculation(date, q_day):
    date = datetime.strptime(date, "%d-%m-%Y")
    date_end = date + timedelta(days=q_day)
    current_date = datetime.now()
    remaining_days = (date_end - current_date).days + 1

    if remaining_days > 0:
        return remaining_days
    elif remaining_days == 0:
        return "Подписка истекает сегодня."
    else:
        return "Подписка истекла."


if __name__ == "__main__":
    print(subs_calculation('15-06-2024', 5))
