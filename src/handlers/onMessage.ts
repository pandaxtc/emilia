import * as Discord from 'discord.js'
import * as CommandHandler from './commandHandler'
import * as AutoreplyHandler from './autoreplyHander'
import * as ErrorHandler from './errorHandler'
import { CommandDefinedError, CommandError } from '../errors/commandError'

export async function onMessage (message: Discord.Message) {
  if (message.author.bot) {
    return
  }
  console.log(message.content)
  let parsedCommand = await CommandHandler.parseCommand(message)
  if (!parsedCommand) {
    await AutoreplyHandler.handleAutoreply(message)
  } else {
    let { context, command, reqArgs, optArgs } = parsedCommand
    console.log(`Invoking command ${command.names[0]}!`)
    try {
      await CommandHandler.invokeCommand(context, command, reqArgs, optArgs)
    } catch (error) {
      if (error instanceof CommandError || error instanceof CommandDefinedError) {
        await ErrorHandler.handleError(context, error)
      } else {
        throw error
      }
    }
  }
}
