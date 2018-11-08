import * as Discord from 'discord.js'
import { readdirSync } from 'fs'
import { client } from '../index'
import CommandArgumentError from '../errors/commandArgumentError'
import 'minimist'
import minimist from 'minimist'
import CommandError from '../errors/commandError'

export enum ParameterType {
  String = 'string',
  Number = 'number',
  User = 'user',
  Channel = 'channel',
  Role = 'role',
  Emoji = 'emoji'
}

export type Parameter = {
  name: string,
  type: ParameterType
}

export type OptionalParameter = Parameter & {flag: string}

export type Command = {
  names: string[],
  category: string,
  target: Function,
  reqParams: Parameter[],
  optionalParams: OptionalParameter[],
  allowedInDMs?: boolean,
  cooldown?: Cooldown
}

export type Context = {
  author: Discord.User,
  channel: Discord.TextBasedChannelFields,
  guild?: Discord.Guild
}

export default class CommandHandler {
  public static commands = new Discord.Collection<string[], Command>()

  public static async reloadCommands () {
    const commandModules = readdirSync('./bin/commands')
    commandModules.forEach((commandModule: string) => {
      const command = require(`../commands/${commandModule}`).command as Command
      CommandHandler.commands.set(command.names, command)
    })
  }

  public static async parseCommand (message: Discord.Message) {
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
    let {_, ...optArgs} = args
    let reqArgs: string[] = _
    const commandName = reqArgs[0].replace(prefix, "")
    reqArgs = reqArgs.slice(1)


    const command = CommandHandler.commands.find((v, k) => k.includes(commandName))
    try {
      await this.invokeCommand(message, command, reqArgs, optArgs)
    }
    catch (error) {
      throw error

    }
  }

  private static async invokeCommand (context: Context, command: Command, requiredArgs: string[], optionalArgs: {[key: string]: string}) {
    if (context.guild === undefined && !command.allowedInDMs) return

    let args: any = []

    let detectedArgs: (string|undefined)[] = requiredArgs
    let fullParams: Parameter[] = [...command.reqParams, ...command.optionalParams]

    for (let optParam of command.optionalParams) {
      if (optionalArgs[optParam.flag] != undefined) {
        detectedArgs.push(String(optionalArgs[optParam.flag]).trim())
      }
      else {
        detectedArgs.push(undefined)
      }
    }

    const zippedDetectedArgs = [[...detectedArgs],[...fullParams]]

    for (let i = 0; i < zippedDetectedArgs[1].length; i++) { // populate required parameters
      const param = zippedDetectedArgs[1][i] as Parameter
      if (i >= zippedDetectedArgs[0].length) {
        throw new CommandArgumentError(param)
      }
      const arg = zippedDetectedArgs[0][i] as string

      if (arg == undefined) {
        args.push(undefined)
      }
      else {
        let typeArg: string | number | Discord.User | Discord.Role | Discord.Channel | Discord.Emoji | undefined
        switch (param.type) {
          case 'string':
            args.push(arg)
            break
          case 'number':
            typeArg = Number(arg)
            if (isNaN(typeArg)) throw new CommandArgumentError(param)
            else args.push(typeArg)
            break
          case 'user':
            typeArg = this.getUserFromString(arg)
            if (typeArg == undefined) throw new CommandArgumentError(param)
            else args.push(typeArg)
            break
          case 'channel':
            typeArg = this.getChannelFromString(arg)
            if (typeArg == undefined) throw new CommandArgumentError(param)
            else args.push(typeArg)
            break
          case 'role':
            typeArg = this.getRoleFromString(arg, context)
            if (typeArg == undefined) throw new CommandArgumentError(param)
            else args.push(typeArg)
            break
          case 'emoji':
            typeArg = this.getEmojiFromString(arg, context)
            if (typeArg == undefined) throw new CommandArgumentError(param)
            else args.push(typeArg)
            break
        }
      }
    }

    await command.target(context, ...args)
  }

  public static getUserFromString (text: any): undefined
  public static getUserFromString (text: string): Discord.User | undefined {
    if (!text || typeof text !== 'string') return
    if (text.startsWith('<@') && text.endsWith('>')) {
      text = text.slice(2, -1)
      if (text.startsWith('!')) {
        text = text.slice(1)
      }
      return client.users.get(text)
    }
  }

  public static getChannelFromString (text: any): undefined
  public static getChannelFromString (text: string): Discord.Channel | undefined {
    if (!text || typeof text !== 'string') return
    if (text.startsWith('<#') && text.endsWith('>')) {
      text = text.slice(2, -1)
      return client.channels.get(text)
    }
  }

  public static getRoleFromString (text: any, context: Context): undefined
  public static getRoleFromString (text: string, context: Context): Discord.Role | undefined {
    if (!text || typeof text !== 'string' || context.guild === undefined) return
    if (text.startsWith('<@&') && text.endsWith('>')) {
      text = text.slice(3, -1)
      return context.guild.roles.get(text)
    }
  }

  public static getEmojiFromString (text: any, context: Context): undefined
  public static getEmojiFromString (text: string, context: Context): Discord.Emoji | undefined {
    if (!text || typeof text !== 'string' || context.guild === undefined) return
    const regex = /<:[a-zA-Z0-9]+:([0-9]+)>/g
    const match = regex.exec(text)
    if (match != null) {
      text = match[1]
    }
    return context.guild.emojis.get(text)
  }

}
