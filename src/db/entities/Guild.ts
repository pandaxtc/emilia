import { Column, Entity, OneToMany, PrimaryColumn } from 'typeorm'
import { Autoreply } from './Autoreply'

@Entity()
export class Guild {
  @PrimaryColumn({ type: 'bigint' })
  id!: string

  @Column({ default: '$' })
  prefix!: string

  @Column({ default: false })
  autoreply_on!: boolean

  @OneToMany(type => Autoreply, (autoreply: Autoreply) => autoreply.guild)
  autoreplies!: Promise<Autoreply[]>
}
