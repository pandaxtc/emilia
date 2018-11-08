import * as Discord from 'discord.js'
import CommandHandler from './commandHandler'

export default async function onReady () {
  await CommandHandler.reloadCommands()
}
