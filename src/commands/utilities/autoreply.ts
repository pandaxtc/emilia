import * as Discord from 'discord.js'
import { autoreplyRepository, guildRepository } from '../../db/db'
import { Guild } from '../../db/entities'
import { footerEmbed } from '../../embeds/embeds'
import { CommandDefinedError } from '../../errors/commandError'
import { Command, Context, ParameterType } from '../../handlers/commandHandler'

async function autoreply (context: Context) {
  if (context.guild === undefined) return
  let guild = (await guildRepository.getByID(context.guild.id)) as Guild
  let autoreplies = await guild.autoreplies

  const embed = new Discord.RichEmbed({ color: 10181046 })
  embed.setAuthor(
    'Autoreplies',
    process.env.SCROLL_ICON
  )
  embed.setDescription('Add autoreplies with `autoreply add`, and remove autoreplies with `autoreply rm`!')
  autoreplies.forEach((autoreply, index) => {
    embed.addField(`[${index + 1}]  ${autoreply.pattern}`, autoreply.reply, true)
  })
  embed.setFooter(
    `Autoreplies ${guild.autoreply_on ? 'ON' : 'OFF'} for this server!`,
    guild.autoreply_on ? process.env.CHECK_ICON : process.env.X_ICON
  )

  await context.channel.send('', embed)
}

async function add (context: Context, pattern: string, reply: string) {
  if (context.guild === undefined) return

  const guild = await guildRepository.getByID(context.guild.id)
  if (guild === undefined) throw new Error('Guild not in database!')
  await autoreplyRepository.createAndSave(guild, pattern, reply)

  const embed = footerEmbed((process.env.CHECK_ICON as string), `Added autoreply ${pattern} <${reply}>!`)
  await context.channel.send('', embed)
}

async function remove (context: Context, pattern: string) {
  if (context.guild === undefined) return

  const autoreply = await autoreplyRepository.getByPattern(context.guild.id, pattern.trim())
  if (autoreply === undefined) throw new CommandDefinedError(`Autoreply with pattern "${pattern}" not found!`)
  await autoreplyRepository.remove(autoreply)
}

async function toggle (context: Context) {
  if (context.guild === undefined) return

  await guildRepository.toggleAutoreply(context.guild.id)
}

const addCommand: Command = {
  names: ['add'],
  category: 'Utilities',
  target: add,
  params: [
    { name: 'pattern', types: [ParameterType.String] },
    { name: 'reply', types: [ParameterType.String] }
  ]
}

const removeCommand: Command = {
  names: ['remove', 'rm'],
  category: 'Utilities',
  target: remove,
  params: [
    { name: 'pattern', types: [ParameterType.String] }
  ]
}

const toggleCommand: Command = {
  names: ['toggle'],
  category: 'Utilities',
  target: toggle,
  params: []
}

export const command: Command = {
  names: ['autoreply', 'ar'],
  category: 'Utilities',
  target: autoreply,
  subcommands: [addCommand, removeCommand, toggleCommand],
  params: []
}
