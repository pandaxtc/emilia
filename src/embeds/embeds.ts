import * as Discord from 'discord.js'
import { Autoreply } from '../db/entities'

export function footerEmbed (iconUrl: string, text: string) {
  return new Discord.RichEmbed({
    footer: {
      text: text,
      icon_url: iconUrl
    }
  })
}
