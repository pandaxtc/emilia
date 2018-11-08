import * as Discord from 'discord.js'
import { ParameterType, Command, Context } from '../handlers/commandHandler'

async function ping (context: Context, a: string, b?: number, c?: Discord.Channel) {
  await context.channel.send('hewwo!?')
}

export const command: Command = {
  names: ['ping'],
  category: 'misc',
  target: ping,
  reqParams: [
    { name: 'a', type: ParameterType.String },
  ],
  optionalParams: [
    { name: 'b', flag: 'b', type: ParameterType.Number },
    { name: 'c', flag: 'c', type: ParameterType.Channel }
  ]
}
