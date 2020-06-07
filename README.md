# efai_clock
Connecting EFAI with Apollo XE through telegram bot. Feel free to send me PRs.

# deployed bot
http://t.me/efai_clock_bot

# sample run
```bash
docker run -dt \
    -e PG_USER=<db_username> \
    -e PG_PASSWORD=<db_password> \
    -e PG_HOST=<db_hostname> \
    -e PG_PORT=<db_port> \
    -e PG_DB=<db_database> \
    -e BOT_TOKEN=<bot token> \
    --name efai_clock \
    --restart unless-stopped \
    cloudrainstar/efai_clock:latest
```

# caveats / known issues
- detects "onleave" icon, but cannot identify the hours of leave
- does not detect any other types of special attendance arrangements (e.g. business trips)
- hard coded 8am to 5pm schedule with 07:15 reminder clockin and 17:00 reminder clockout
