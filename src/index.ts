import * as Discord from 'discord.js'
import * as dotenv from 'dotenv'
import { createConnection } from 'typeorm'
import { initRepositories } from './db/db'
import { onMessage } from './handlers/onMessage'
import { onReady } from './handlers/onReady'

export const client = new Discord.Client()

dotenv.config()

createConnection().then((connection) => {
  initRepositories()

  client.on('ready', onReady)
  client.on('message', onMessage)
  client.login(process.env.DISCORD_TOKEN)
})
