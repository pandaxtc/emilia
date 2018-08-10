# ayano

The latest and greatest half-elf Discord bot. Designed for use with Heroku. Currently an extreme WIP.

## Installing

Depends on [discord.py v1.0.0](https://github.com/Rapptz/discord.py) and [gino](https://github.com/fantix/gino). Install `requirements.txt` before using.

Uses environment variables for configuration.

### Environment variables

- `DATABASE_URL` -  URL for PostgresQL database. Schema can be determined from `db/models`.
- `BOT_NAME` - Name of bot. Currently unused.
- `DESCRIPTION` - discord.py description string.
- `PLAYING` - Playing string.
- `MAX_AUTOREPLIES` - Maximum number of autoreplies each guild can configure.
- `DISCORD_TOKEN` - Self-explanatory.
- `SAFE_TOKEN` - Token for safe.moe API, used for file uploads for the `get` extension.
- `EXTENSIONS` - Comma-separated no-whitespace list of cogs to load.
