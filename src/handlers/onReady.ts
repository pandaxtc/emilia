import { guildRepository } from '../db/db'
import { client } from '../index'
import * as CommandHandler from './commandHandler'

export async function onReady () {
  for (let [guild_id, ..._] of client.guilds) {
    let db_guild = await guildRepository.getByID(guild_id)
    if (db_guild === undefined) {
      db_guild = guildRepository.create({ id: guild_id })
      await guildRepository.save(db_guild)
    }
  }
  await CommandHandler.reloadCommands()
  // TODO: register handlers too
  console.log('')
}
