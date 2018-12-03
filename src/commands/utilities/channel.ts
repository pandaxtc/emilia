import * as Discord from 'discord.js'
import { CommandDefinedError } from '../../errors/commandError'
import { Command, Context, ParameterType, TextBasedChannel } from '../../handlers/commandHandler'

async function channel (context: Context) {}

async function info (context: Context, channel: TextBasedChannel = context.channel) {
  const replyEmbed = new Discord.RichEmbed({ color: 10181046 })

  const name = ('name' in channel) ? channel.name : channel.recipient.username
  replyEmbed.setAuthor(`#${name}`, process.env.SCROLL_ICON)

  const url = ('guild' in channel) ? channel.guild.iconURL : ('recipient' in channel) ? channel.recipient.avatarURL : ''
  replyEmbed.setThumbnail(url)

  const topic = ('topic' in channel) ? channel.topic : undefined
  if (topic) {
    replyEmbed.setDescription(topic)
  }

  replyEmbed.setTitle(`ID <${channel.id}>`)

  replyEmbed.addField('Created At', channel.createdAt.toUTCString())

  const category = ('parent' in channel && channel.parent) ? channel.parent.name : undefined
  if (category) {
    replyEmbed.addField('Category', category, true)
  }

  replyEmbed.addField('Pins', (await channel.fetchPinnedMessages()).size, true)

  const countWebhooks = ('fetchWebhooks' in channel) ? (await channel.fetchWebhooks()).size : undefined
  if (countWebhooks || countWebhooks === 0) {
    replyEmbed.addField('Webhooks', countWebhooks, true)
  }

  return context.channel.send('', replyEmbed)
}

async function stats (
  context: Context,
  channel: TextBasedChannel = context.channel,
  limit: number = 5000,
  member?: Discord.GuildMember,
  top: number = 5
) {
  if (channel instanceof Discord.DMChannel) return
  if (limit < 20 || limit >= 10000) throw new CommandDefinedError('Message scan limit must be between 20 and 1000!')
  if (member) top = 1
  if (top <= 0 || top > 10) throw new CommandDefinedError('Number of users to list must be between 0 and 10!')
  const messages = await fetchMessagesUnlimited(channel, limit)
  let countMessages = 0
  const map = new Discord.Collection<Discord.User, number>()

  if (member) {
    map.set(member.user, messages.reduce((accumulator, message) => {
      countMessages++
      if (message.author.id === member.id) {
        accumulator++
      }
      return accumulator
    }, 0)
    )
  } else {
    messages.forEach(message => {
      map.set(message.author, (map.get(message.author) || 0) + 1)
      countMessages++
    })
  }

  const sorted = map.sort((a, b) => b - a)
  const topKeys = sorted.firstKey(top)
  const topValues = sorted.first(top)
  const modes = topKeys.map((key, index) => {
    return { user: key, count: topValues[index] }
  })

  const replyEmbed = new Discord.RichEmbed({ color: 10181046 })
  let userString = ''
  if (member) userString = ` for ${member.user.username}`
  replyEmbed.setAuthor(`#${channel.name} Channel Statistics ${userString}`, process.env.BAR_CHART_ICON)
  if (context.guild) replyEmbed.setThumbnail(context.guild.iconURL)
  modes.forEach(({ user, count }) => {
    const percent = (count / countMessages * 100).toFixed(1)
    replyEmbed.addField(user.username, `${count} messages | ${percent}%`, true)
  })
  replyEmbed.setFooter(`Total messages checked: ${countMessages}`)
  return channel.send('', replyEmbed)
}

// bypass discord 100-message fetch limit
// api rate limits here we come
async function fetchMessagesUnlimited (
  channel: TextBasedChannel,
  limit: number,
  before: Discord.Snowflake = channel.lastMessageID,
  fetchedSoFar: number = 0
): Promise<Discord.Collection<Discord.Snowflake, Discord.Message>> {
  if (limit - fetchedSoFar < 100) {
    return channel.fetchMessages({ limit: limit - fetchedSoFar })
  } else {
    const m = await channel.fetchMessages({ limit: 100, before })
    if (m.size === 0) return new Discord.Collection<Discord.Snowflake, Discord.Message>()
    return m.concat(await fetchMessagesUnlimited(channel, limit, m.last().id, fetchedSoFar + m.size))
  }
}

const statsCommand: Command = {
  names: ['stats', 'statistics'],
  category: 'Utilities',
  target: stats,
  params: [
    { name: 'channel', types: [ParameterType.TextChannel], isOptional: true }
  ],
  flagParams: [
    { name: 'member', flag: 'u', types: [ParameterType.Member] },
    { name: 'limit', flag: 'l', types: [ParameterType.Number] },
    { name: 'top', flag: 't', types: [ParameterType.Number] }
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
