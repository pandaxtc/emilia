import { EntityRepository, getCustomRepository, Repository } from 'typeorm'
import { Autoreply, Guild, User } from './entities'

@EntityRepository(Autoreply)
export class AutoreplyRepository extends Repository<Autoreply> {

  async createAndSave (guild: Guild, pattern: string, reply: string) {
    return this.save(this.create({ guild, pattern, reply }))
  }

  getByPattern (guild_id: string, pattern: string) {
    return this.findOne({ where: { guild_id, pattern } })
  }

  getByGuild (guild_id: string) {
    return this.find({ where: { guild: guild_id }, cache: { id: guild_id, milliseconds: 30000 } })
  }

}

@EntityRepository(Guild)
export class GuildRepository extends Repository<Guild> {

  createAndSave (guild_id: string) {
    return this.save(this.create({ id: guild_id }))
  }

  getByID (guild_id: string) {
    return this.findOne(guild_id)
  }

  toggleAutoreply (guild_id: string) {
    return this.findOne(guild_id).then(guild => {
      if (guild === undefined) return
      guild.autoreply_on = !guild.autoreply_on
      this.save(guild)
    })
  }

}

@EntityRepository(User)
export class UserRepository extends Repository<User> {

  getByID (user_id: string) {
    return this.findOne(user_id)
  }

}

export function initRepositories () {
  autoreplyRepository = getCustomRepository(AutoreplyRepository)
  guildRepository = getCustomRepository(GuildRepository)
  userRepository = getCustomRepository(UserRepository)
}

export let autoreplyRepository: AutoreplyRepository
export let guildRepository: GuildRepository
export let userRepository: UserRepository
