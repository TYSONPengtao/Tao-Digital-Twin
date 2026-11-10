# Safety and Security

These requirements apply when TAO Home Digital Twin connects to physical devices. The current prototype uses simulated state and local software-light tests.

## Principles

- Keep credentials and access tokens on the backend.
- Never embed Home Assistant tokens, MQTT passwords or PLC credentials in UE5 or browser bundles.
- Authenticate clients before accepting control commands.
- Authorize commands by user, client and device capability.
- Validate command parameters and target state.
- Record important control actions in an audit log.
- Prefer encrypted transport where practical.
- Keep critical local control available if internet access fails.

## Physical safety

Household lights, heaters, door and window motors, and similar equipment require safeguards such as:

- Maximum run time
- Automatic timeout
- Local emergency stop
- Safe default after communication loss
- Sensor interlocks
- Rate limits
- Manual override

## State confidence

Requested state and confirmed physical state are different.

```text
Requested: window OPEN
Confirmed: window OPEN
```

If feedback is missing, the twin must not pretend that the action succeeded.

## Cameras

Use dedicated secure streaming paths. TAO Core should manage metadata, permissions and control rather than proxying every video frame unless required.
