import { Column, Entity, PrimaryColumn } from 'typeorm'

@Entity()
export class User {
  @PrimaryColumn({ type: 'bigint' })
  id!: string

  @Column({ default: 0 })
  commands_executed: number = 0
}
