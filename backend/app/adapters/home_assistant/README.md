# Home Assistant Adapter

Responsibilities:

- Discover selected Home Assistant entities
- Read current state
- Subscribe to state changes
- Send service/control commands
- Translate Home Assistant entities into canonical TAO entities

Home Assistant credentials stay on the TAO backend and must never be shipped to browser or Unreal clients.
