import { Command, Context, ParameterType } from '../../handlers/commandHandler'

async function ping (context: Context, a: string) {
  await context.channel.send(a)
}

export const command: Command = {
  names: ['ping'],
  category: 'misc',
  target: ping,
  params: [
    { name: 'a', types: [ParameterType.String] },
  ]
}
