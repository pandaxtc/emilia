import * as Discord from 'discord.js'
import { Autoreply } from '../db/entities'

export function footerEmbed (iconUrl: string, text: string, color: number = 10181046) {
  return new Discord.RichEmbed({
    color: color,
    footer: {
      text: text,
      icon_url: iconUrl
    }
  })
}
