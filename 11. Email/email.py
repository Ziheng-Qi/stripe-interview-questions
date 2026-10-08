import email


def parse_users(user_requests):
    users_data = []
    for request in user_requests:

        name, plan, begin_date, duration = (
            request["name"],
            request["plan"],
            request["begin_date"],
            request["duration"],
        )
        # print(request)
        # print(name, plan, begin_date, duration)
        users_data.append(
            {
                "name": name,
                "plan": plan,
                "begin_date": begin_date,
                "duration": duration,
            }
        )

    users_data.sort(key=lambda x: x["begin_date"])
    return users_data


def create_email_events(users_data):
    email_events = []
    for user in users_data:
        name, plan, begin_date, duration = (
            user["name"],
            user["plan"],
            user["begin_date"],
            user["duration"],
        )
        # create Welcome
        time = begin_date
        email_events.append(
            {
                "time": time,
                "name": name,
                "plan": plan,
                "type": "Welcome",
            }
        )
        # ceate Upcoming expiration
        time = begin_date + duration - 15
        email_events.append(
            {
                "time": time,
                "name": name,
                "plan": plan,
                "type": "Upcoming expiration",
            }
        )
        # ceate Expired
        time = begin_date + duration
        email_events.append(
            {
                "time": time,
                "name": name,
                "plan": plan,
                "type": "Expired",
            }
        )

    email_events.sort(key=lambda x: x["time"])
    return email_events


def send_emails(user_requests):
    users_data = parse_users(user_requests)
    email_events = create_email_events(users_data)

    for event in email_events:
        print(
            f"{event['time']}: [{event['type']}] {event['name']}, subscribe in plan {event['plan']}"
        )


def create_email_events_with_changes(users_data, changes):
    email_events = []
    for user in users_data:
        name, plan, begin_date, duration = (
            user["name"],
            user["plan"],
            user["begin_date"],
            user["duration"],
        )
        # create Welcome
        time = begin_date
        email_events.append(
            {
                "time": time,
                "name": name,
                "plan": plan,
                "type": "Welcome",
            }
        )
        # ceate Upcoming expiration
        time = begin_date + duration - 15
        email_events.append(
            {
                "time": time,
                "name": name,
                "plan": plan,
                "type": "Upcoming expiration",
            }
        )
        # ceate Expired
        time = begin_date + duration
        email_events.append(
            {
                "time": time,
                "name": name,
                "plan": plan,
                "type": "Expired",
            }
        )
    for change in changes:
        name, new_plan, change_date = (
            change["name"],
            change["new_plan"],
            change["change_date"],
        )
        email_events.append(
            {
                "time": change_date,
                "name": name,
                "plan": new_plan,
                "type": "Changed",
            }
        )
        for event in email_events:
            if event["time"] < change_date:
                continue

            if event["name"] == name:
                event["plan"] = new_plan

    email_events.sort(key=lambda x: x["time"])
    return email_events


def send_emails_with_changes(user_requests, change_requests):
    users_data = parse_users(user_requests)
    email_events = create_email_events_with_changes(users_data, change_requests)

    for event in email_events:
        print(
            f"{event['time']}: [{event['type']}] {event['name']}, subscribe in plan {event['plan']}"
        )


def create_email_events_with_changes_ext(users_data, changes):
    email_events = []
    for user in users_data:
        name, plan, begin_date, duration = (
            user["name"],
            user["plan"],
            user["begin_date"],
            user["duration"],
        )
        # create Welcome
        time = begin_date
        email_events.append(
            {
                "time": time,
                "name": name,
                "plan": plan,
                "type": "Welcome",
            }
        )
        # ceate Upcoming expiration
        time = begin_date + duration - 15
        email_events.append(
            {
                "time": time,
                "name": name,
                "plan": plan,
                "type": "Upcoming expiration",
            }
        )
        # ceate Expired
        time = begin_date + duration
        email_events.append(
            {
                "time": time,
                "name": name,
                "plan": plan,
                "type": "Expired",
            }
        )
    for change in changes:
        name, change_date = (
            change["name"],
            change["change_date"],
        )
        if "new_plan" in change:
            new_plan = change["new_plan"]
            email_events.append(
                {
                    "time": change_date,
                    "name": name,
                    "plan": new_plan,
                    "type": "Changed",
                }
            )
            for event in email_events:
                if event["time"] < change_date:
                    continue

                if event["name"] == name:
                    event["plan"] = new_plan
        elif "extension" in change:
            extension = change["extension"]
            email_events.append(
                {
                    "time": change_date,
                    "name": name,
                    "plan": plan,
                    "type": "Renewed",
                }
            )
            temp = email_events
            for event in temp:
                if event["time"] < change_date:
                    continue

                if event["name"] == name and event["type"] == "Expired":
                    event["time"] += extension
                    # add new "Upcoming expiration" event
                    email_events.append(
                        {
                            "time": event["time"] - 15,
                            "name": name,
                            "plan": plan,
                            "type": "Upcoming expiration",
                        }
                    )

    email_events.sort(key=lambda x: x["time"])
    return email_events


def send_emails_with_changes_ext(user_requests, change_requests):
    users_data = parse_users(user_requests)
    email_events = create_email_events_with_changes_ext(users_data, change_requests)

    for event in email_events:
        print(
            f"{event['time']}: [{event['type']}] {event['name']}, subscribe in plan {event['plan']}"
        )


def parse_users_expiry(user_requests):
    users_data = []
    for request in user_requests:

        name, plan, begin_date, duration, expiry = (
            request["name"],
            request["plan"],
            request["begin_date"],
            request["duration"],
            request["expiry"],
        )
        # print(request)
        # print(name, plan, begin_date, duration)
        users_data.append(
            {
                "name": name,
                "plan": plan,
                "begin_date": begin_date,
                "duration": duration,
                "expiry": expiry,
            }
        )

    users_data.sort(key=lambda x: x["begin_date"])
    return users_data


def create_email_events_with_changes_ext_expiry(users_data, changes):
    email_events = []
    for user in users_data:
        name, plan, begin_date, duration, expiry = (
            user["name"],
            user["plan"],
            user["begin_date"],
            user["duration"],
            user["expiry"],
        )
        # create Welcome
        time = begin_date
        email_events.append(
            {
                "time": time,
                "name": name,
                "plan": plan,
                "type": "Welcome",
            }
        )
        # ceate Upcoming expiration
        time = begin_date + duration - expiry
        email_events.append(
            {
                "time": time,
                "name": name,
                "plan": plan,
                "type": "Upcoming expiration",
            }
        )
        # ceate Expired
        time = begin_date + duration
        email_events.append(
            {
                "time": time,
                "name": name,
                "plan": plan,
                "type": "Expired",
            }
        )
    for change in changes:
        name, change_date = (
            change["name"],
            change["change_date"],
        )
        if "new_plan" in change:
            new_plan = change["new_plan"]
            email_events.append(
                {
                    "time": change_date,
                    "name": name,
                    "plan": new_plan,
                    "type": "Changed",
                }
            )
            for event in email_events:
                if event["time"] < change_date:
                    continue

                if event["name"] == name:
                    event["plan"] = new_plan
        elif "extension" in change:
            extension = change["extension"]
            email_events.append(
                {
                    "time": change_date,
                    "name": name,
                    "plan": plan,
                    "type": "Renewed",
                }
            )
            temp = email_events
            for event in temp:
                if event["time"] < change_date:
                    continue

                if event["name"] == name and event["type"] == "Expired":
                    event["time"] += extension
                    # add new "Upcoming expiration" event
                    email_events.append(
                        {
                            "time": event["time"] - expiry,
                            "name": name,
                            "plan": plan,
                            "type": "Upcoming expiration",
                        }
                    )

    email_events.sort(key=lambda x: x["time"])
    return email_events


def send_emails_with_changes_ext_expiry(user_requests, change_requests):
    users_data = parse_users_expiry(user_requests)
    email_events = create_email_events_with_changes_ext_expiry(
        users_data, change_requests
    )

    for event in email_events:
        print(
            f"{event['time']}: [{event['type']}] {event['name']}, subscribe in plan {event['plan']}"
        )


if __name__ == "__main__":
    # 1
    print("***************Part 1***************")
    users = [
        {"name": "A", "plan": "X", "begin_date": 0, "duration": 30},
        {"name": "B", "plan": "Y", "begin_date": 1, "duration": 15},
    ]
    send_emails(users)
    print("***************Part 2***************")
    changes = [
        {"name": "A", "new_plan": "Y", "change_date": 5},
    ]
    send_emails_with_changes(users, changes)
    print("***************Part 3***************")
    changes = [
        {"name": "A", "new_plan": "Y", "change_date": 5},
        {"name": "B", "extension": 15, "change_date": 3},
    ]
    send_emails_with_changes_ext(users, changes)
    print("***************Part 4***************")
    users = [
        {
            "name": "A",
            "plan": "X",
            "begin_date": 0,
            "duration": 30,
            "expiry": 7,  # 提前 7 天通知
        },
        {
            "name": "B",
            "plan": "Y",
            "begin_date": 1,
            "duration": 10,
            "expiry": 3,  # 提前 3 天通知
        },
        {
            "name": "C",
            "plan": "Z",
            "begin_date": 2,
            "duration": 5,
            "expiry": 10,  # 时间不足，无法触发提醒
        },
    ]
    changes = [
        {"name": "A", "new_plan": "Y", "change_date": 5},
        {"name": "B", "extension": 15, "change_date": 3},
    ]
    send_emails_with_changes_ext_expiry(users, changes)
