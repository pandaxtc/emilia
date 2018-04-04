# ayano
A basic discord utility bot. Default prefix: **$**

All downloads are stored in `cache/`.

Depends on discord.py ***AND aiohttp v1.3.0!*** 

## Configuration
### token.json
This bot requires two tokens to function properly. These tokens are stored as keys in a file in the project root called `tokens.json`.
- Discord bot token: `dsc-token`
- safe.moe token: `safe-token`
Also in token.json is birthday role configuration. ServerID-roleID key-value pairs are stored as strings in a dict called "bd_guilds".
