import {
  BeforeInsert,
  BeforeRemove,
  BeforeUpdate,
  Column,
  Entity,
  getConnection,
  JoinColumn,
  ManyToOne,
  PrimaryColumn
} from 'typeorm'
import { Guild } from './Guild'

@Entity()
export class Autoreply {
  @ManyToOne(type => Guild, (guild: Guild) => guild.id, {
    primary: true,
    eager: true,
    onDelete: 'CASCADE'
  })
  @JoinColumn({ name: 'guild_id' })
  guild!: Guild

  @PrimaryColumn()
  pattern!: string

  @Column({ nullable: false })
  reply!: string

  @BeforeUpdate()
  @BeforeRemove()
  @BeforeInsert()
  evictCache () {
    const connection = getConnection()
    if (connection.queryResultCache) {
      connection.queryResultCache.remove([this.guild.id])
    }
  }
}
