import * as Discord from 'discord.js'
import onMessage from './handlers/onMessage'
import onReady from './handlers/onReady'

export const client = new Discord.Client()

import * as dotenv from 'dotenv'
dotenv.config()

client.on('ready', onReady)
client.on('message', onMessage)


client.login(process.env.DISCORD_TOKEN)
