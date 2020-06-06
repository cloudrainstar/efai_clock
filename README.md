# efai_clock
Connecting EFAI with Apollo XE through telegram bot.

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