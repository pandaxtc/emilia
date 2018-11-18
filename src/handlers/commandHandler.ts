import * as Discord from 'discord.js'
import { readdirSync } from 'fs'
import minimist from 'minimist'
import { userRepository } from '../db/db'
import {
  CommandArgumentMissingError,
  CommandArgumentSetIncompleteError,
  CommandArgumentTypeError,
  CommandDefinedError,
  CommandInvokeError
} from '../errors/commandError'

export type TextBasedChannel = Discord.TextChannel | Discord.DMChannel | Discord.GroupDMChannel

export enum ParameterType {
  String = 'string',
  Number = 'number',
  Boolean = 'boolean',
  Member = 'member',
  TextChannel = 'text channel',
  VoiceChannel = 'voice channel',
  Role = 'role',
  Emoji = 'emoji'
}

export type Parameter = {
  name: string,
  types: ParameterType[],
  isOptional?: boolean // optional arguments MUST come after all required arguments
}

export type FlagParameter = Parameter & { flag: string }

export type Command = {
  names: string[],
  category: string,
  target: Function,
  subcommands?: Command[]
  params: (Parameter)[],
  flagParams?: FlagParameter[], // optional arguments must be marked as optional function parameters
  repeatParams?: Parameter[], // repeated arguments must be placed in args
  allowedInDMs?: boolean,
  cooldown?: Cooldown
}

export class Context {
  public channel: TextBasedChannel
  public guild: Discord.Guild | undefined

  constructor (public message: Discord.Message, public invokingName: string) {
    this.channel = message.channel
    this.guild = message.guild
  }
}

function getBooleanFromString (text: any): undefined
function getBooleanFromString (text: string): boolean | undefined {
  text = text.trim()
  if (text === 'yes' || text === 'true' || text === 'on') return true
  if (text === 'no' || text === 'false' || text === 'off') return false
}

function getMemberFromString (text: any, context: Context): undefined
function getMemberFromString (text: string, context: Context): Discord.GuildMember | undefined {
  if (!text || typeof text !== 'string' || context.guild === undefined) return
  if (text.startsWith('<@') && text.endsWith('>')) {
    text = text.slice(2, -1)
    if (text.startsWith('!')) {
      text = text.slice(1)
    }
    return context.guild.members.get(text)
  } else {
    return context.guild.members.find(member => {
      return member.user.username.startsWith(text) || member.nickname.startsWith(text)
    })
  }
}

function getTextChannelFromString (text: any, context: Context): undefined
function getTextChannelFromString (text: string, context: Context): Discord.TextChannel | undefined {
  if (!text || typeof text !== 'string' || context.guild === undefined) return
  if (text.startsWith('<#') && text.endsWith('>')) {
    text = text.slice(2, -1)
    return context.guild.channels.get(text) as Discord.TextChannel | undefined
  } else {
    return context.guild.channels.find(channel => {
      return channel.name === text && channel instanceof Discord.TextChannel
    }) as Discord.TextChannel | undefined
  }
}

function getRoleFromString (text: any, context: Context): undefined
function getRoleFromString (text: string, context: Context): Discord.Role | undefined {
  if (!text || typeof text !== 'string' || context.guild === undefined) return
  if (text.startsWith('<@&') && text.endsWith('>')) {
    text = text.slice(3, -1)
    return context.guild.roles.get(text)
  } else {
    return context.guild.roles.find(role => {
      return role.name.startsWith(text)
    })
  }
}

function getEmojiFromString (text: any, context: Context): undefined
function getEmojiFromString (text: string, context: Context): Discord.Emoji | undefined {
  if (!text || typeof text !== 'string' || context.guild === undefined) return
  const regex = /<:[a-zA-Z0-9]+:([0-9]+)>/g
  const match = regex.exec(text)
  if (match != null) {
    text = match[1]
  }
  return context.guild.emojis.get(text)
}

let commands = new Discord.Collection<string[], Command>()

async function reloadCommands () {
  const commandModules = readdirSync('./dist/commands')
  commandModules.forEach((commandModule: string) => {
    const imported = require(`../commands/${commandModule}`)
    console.log(imported)
    if (imported.commands) {
      for (let command of imported.commands) {
        commands.set(command.names, command)
      }
    } else if (imported.command) {
      commands.set(imported.command.names, imported.command)
    } else {
      console.error(`Error loading command module ${commandModule}!`)
    }
  })
}

async function parseCommand (message: Discord.Message) {
  const content = message.content
  const prefix = process.env.PREFIX as string

  if (!content.trim().startsWith(prefix)) {
    return
  }

  const regex = /(-\w*\s"+.+?"+|-\w*\s[^"]\S*|[^"]\S*|"+.+?"+)\s*/g // argument matching regex https://regex101.com/r/PbjRv6/1
  let match = regex.exec(message.content)
  let splitted: string[] = []
  while (match != null) {
    let s = match[1].trim()
    if (s.charAt(0) === '"' && s.charAt(s.length - 1) === '"') {
      s = s.slice(1, s.length - 1)
    }
    splitted.push(s)
    match = regex.exec(message.content)
  }
  splitted = splitted.filter(x => x !== '')

  const args = minimist(splitted)
  console.log(args)
  let { _, ...optArgs } = args
  let reqArgs: string[] = _
  const commandName = reqArgs[0].replace(prefix, '')
  reqArgs = reqArgs.slice(1)

  const command = commands.find((v, k) => k.includes(commandName))
  if (!command) return undefined

  const context = new Context(message, commandName)

  return { context, command, reqArgs, optArgs }
}

async function invokeCommand (context: Context, command: Command, args: string[], flagArgs: { [key: string]: string }): Promise<void> {
  if (context.guild === undefined && !command.allowedInDMs) return

  let invokeArgs = [] // arguments to spread into target function call

  let detectedArgs: { parameter: Parameter, arg: string | undefined }[] = []

  if (command.subcommands) {
    const subcommandString = args[0]
    const subcommand = command.subcommands.find((sc) => sc.names.includes(subcommandString))
    if (subcommand) {
      args.shift()
      console.log('subcommand invoking...')
      console.log(args, flagArgs)
      return invokeCommand(context, subcommand, args, flagArgs)
    }
  }

  args.reverse()

  for (let index = 0; index < command.params.length; index++) {
    let param = command.params[index]
    console.log(index + ' ' + param.types)
    console.log(args.length)
    if (args.length === 0 && !param.isOptional) throw new CommandArgumentMissingError(param, command, context)
    detectedArgs.push({ parameter: param, arg: args.pop() })
  }

  // detect which optional parameters were passed
  if (command.flagParams) {
    for (let optParam of command.flagParams) {
      if (flagArgs[optParam.flag] !== undefined) {
        detectedArgs.push({ parameter: optParam, arg: String(flagArgs[optParam.flag]).trim() })
      } else {
        detectedArgs.push({ parameter: optParam, arg: undefined })
      }
    }
  }

  console.log(args)

  // repeat parameters
  if (command.repeatParams) {
    while (args.length > 0) {
      for (let param of command.repeatParams) {
        if (args.length === 0) throw new CommandArgumentSetIncompleteError(param, command, context)
        console.log('putting in repeated argument for ' + param.name)
        detectedArgs.push({ parameter: param, arg: args.pop() })
      }
    }
  }

  console.log(detectedArgs)

  for (let detectedArg of detectedArgs) {
    const param: Parameter = detectedArg.parameter
    const arg: string | undefined = detectedArg.arg

    if (arg === undefined) {
      invokeArgs.push(undefined)
    } else {
      // temporary variable for types conversions
      let convertedArg: string | number | Discord.User | Discord.Role | Discord.Channel | Discord.Emoji | undefined = undefined
      // types conversion into required types
      for (let paramType of param.types) {
        console.log(`converting parameter ${param.name} type ${paramType} given ${arg}`)
        switch (paramType) {
          case ParameterType.Member:
            convertedArg = getMemberFromString(arg, context)
            break
          case ParameterType.TextChannel:
            convertedArg = getTextChannelFromString(arg, context)
            break
          case ParameterType.Role:
            convertedArg = getRoleFromString(arg, context)
            break
          case ParameterType.Emoji:
            convertedArg = getEmojiFromString(arg, context)
            break
          case ParameterType.Number:
            convertedArg = Number(arg)
            break
          case ParameterType.Boolean:
            convertedArg = getBooleanFromString(arg)
            break
          default: // string
            convertedArg = arg
            break
        }
        console.log('converted to ' + (typeof convertedArg))
        if ((typeof convertedArg === typeof true) || convertedArg) {
          console.log(`pushing argument ${convertedArg}`)
          invokeArgs.push(convertedArg)
          break
        }
      }
      if (!(typeof convertedArg === typeof true || !(typeof convertedArg === typeof 0)) && !convertedArg) {
        if (param.isOptional) {
          invokeArgs.push(undefined)
        } else {
          throw new CommandArgumentTypeError(param, command, context)
        }
      }

    }
  }

  let user = await userRepository.getByID(context.message.author.id)
  if (user === undefined) user = userRepository.create({ id: context.message.author.id })
  user.commands_executed++
  await userRepository.save(user)

  console.log(`spreading ${invokeArgs}`)
  return command.target(context, ...invokeArgs).catch((error: Error) => {
    if (error instanceof CommandDefinedError) {
      throw error
    } else {
      throw new CommandInvokeError(error, command)
    }
  })
}

export {
  commands,
  reloadCommands,
  parseCommand,
  invokeCommand
}
