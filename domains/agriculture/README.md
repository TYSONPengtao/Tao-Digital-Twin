# Agriculture Domain

Digital-twin domain for farms, gardens and greenhouses.

Example entities:

- Soil-moisture sensor
- Air temperature/humidity sensor
- Water tank
- Flow meter
- Pump
- Solenoid valve
- Irrigation zone

Target closed loop:

```text
sensor -> edge device -> TAO Core -> UE5/Web
UE5/Web command -> TAO Core -> edge device -> physical valve/pump
physical feedback -> TAO Core -> all clients
```
