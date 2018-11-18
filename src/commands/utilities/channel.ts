import * as Discord from 'discord.js'
import { Command, Context, ParameterType, TextBasedChannel } from '../../handlers/commandHandler'

async function channel (context: Context) {}

async function info (context: Context, channel: TextBasedChannel = context.channel) {
  const embed = new Discord.RichEmbed({ color: 10181046 })

  const name = ('name' in channel) ? channel.name : channel.recipient.username
  embed.setAuthor(`#${name}`, process.env.SCROLL_ICON)

  const url = ('guild' in channel) ? channel.guild.iconURL : ('recipient' in channel) ? channel.recipient.avatarURL : ''
  embed.setThumbnail(url)

  const topic = ('topic' in channel) ? channel.topic : undefined
  if (topic) {
    embed.setDescription(topic)
  }

  embed.setTitle(`ID <${channel.id}>`)

  embed.addField('Created At', channel.createdAt.toUTCString())

  const category = ('parent' in channel && channel.parent) ? channel.parent.name : undefined
  if (category) {
    embed.addField('Category', category, true)
  }

  embed.addField('Pins', (await channel.fetchPinnedMessages()).size, true)

  const countWebhooks = ('fetchWebhooks' in channel) ? (await channel.fetchWebhooks()).size : undefined
  if (countWebhooks || countWebhooks === 0) {
    embed.addField('Webhooks', countWebhooks, true)
  }

  await context.channel.send('', embed)
}

async function stats (context: Context, channel: TextBasedChannel = context.channel, limit: number = 5000, user?: Discord.User) {}

const statsCommand: Command = {
  names: ['stats', 'statistics'],
  category: 'Utilities',
  target: stats,
  params: [
    { name: 'channel', types: [ParameterType.TextChannel], isOptional: true }
  ],
  flagParams: [
    { name: 'user', flag: 'u', types: [ParameterType.Member] },
    { name: 'user', flag: 'l', types: [ParameterType.Member] }
  ]
}

const infoCommand: Command = {
  names: ['info', 'information'],
  category: 'Utilities',
  target: info,
  allowedInDMs: true,
  params: [
    { name: 'channel', types: [ParameterType.TextChannel], isOptional: true }
  ]
}

export const command: Command = {
  names: ['channel', 'ch', 'chan'],
  category: 'Utilities',
  target: channel,
  subcommands: [statsCommand, infoCommand],
  params: []
}
