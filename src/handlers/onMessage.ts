import * as Discord from 'discord.js'
import CommandHandler from './commandHandler'

export default async function onMessage (message: Discord.Message) {
  if (message.author.bot) {
    return
  }
  console.log(message.content)
  await CommandHandler.parseCommand(message)
}
