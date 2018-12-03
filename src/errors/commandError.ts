import { Command, Parameter } from '../handlers/commandHandler'

export class CommandNotAllowedInDMsError extends Error {}

export class CommandDefinedError extends Error {
  constructor (public message: string, ...args: any[]) {
    super(...args)
  }
}

export class CommandError extends Error {
  constructor (public command?: Command | undefined, ...args: any[]) {
    super(...args)
  }
}

export class CommandArgumentError extends CommandError {
  constructor (public parameter: Parameter, command: Command, ...args: any[]) {
    super(command, ...args)
  }
}

export class CommandArgumentTypeError extends CommandArgumentError {}

export class CommandArgumentMissingError extends CommandArgumentError {}

export class CommandArgumentSetIncompleteError extends CommandArgumentError {}

export class CommandInvokeError extends CommandError {
  constructor (public error: Error, command: Command, ...args: any[]) {
    super(command, ...args)
  }
}

export class CommandNotFoundError extends CommandError {
  constructor (public invokingName: string, ...args: any[]) {
    super(undefined, ...args)
  }
}
