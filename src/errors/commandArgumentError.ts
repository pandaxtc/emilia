import {Parameter} from '../handlers/commandHandler'
import CommandError from './commandError'

export default class CommandArgumentError extends CommandError {

  constructor(public parameter: Parameter, ...args: any[]) {
    super(...args)
  }

}
