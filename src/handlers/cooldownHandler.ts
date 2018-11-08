enum CooldownContext {
  guild,
  channel,
  user
}

type Cooldown = {
  time: number,
  context: CooldownContext
}