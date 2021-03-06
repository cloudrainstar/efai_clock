# efai_clock
Connecting EFAI with Apollo XE through telegram bot. Feel free to send me PRs.

# deployed bot
http://t.me/efai_clock_bot

Commands:
- /start - show help message
- /login <username> <password> - save your info to a database
- /info - retrieve your current information
- /clock <in/out> - clock in or out
- /reminder <on/off> - turn on/off reminder
- /autolog <on/off> - turn on/off auto clock in
- /delete - delete everything about you from my database.

# sample run
```bash
docker run -dt \
    -e DB_URI="sqlite://" \
    -e BOT_TOKEN=<bot token> \
    --name efai_clock \
    --restart unless-stopped \
    cloudrainstar/efai_clock:latest
```

# alembic
Alembic has been added to this latest revision. For versions prior to tags, stamp head using 1.0.0.
```bash
docker run -it --rm \
    -e DB_URI="sqlite://" \
    cloudrainstar/efai_clock:1.0.0 \
    alembic stamp head
```

# caveats / known issues
- detects "onleave" icon, but cannot identify the hours of leave
- does not detect any other types of special attendance arrangements (e.g. business trips)
- hard coded 8am to 5pm schedule with 07:29 reminder clockin and 17:01 reminder clockout
- note: a random delay of 29 minutes is added, so your auto clockin will be from 07:29 to 07:58, while your clockout will be from 17:01 to 17:30
