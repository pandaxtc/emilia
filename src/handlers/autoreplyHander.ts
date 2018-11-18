import * as Discord from 'discord.js'
import { autoreplyRepository, guildRepository } from '../db/db'

export async function handleAutoreply (message: Discord.Message) {
  if (message.guild === undefined) return
  let guild = await guildRepository.getByID(message.guild.id)
  if (guild === undefined) {
    return
  }
  let autoreplies = await autoreplyRepository.getByGuild(guild.id)
  for (let autoreply of autoreplies) {
    if (message.content.split(' ').includes(autoreply.pattern)) {
      message.channel.send(autoreply.reply)
    }
  }
}
