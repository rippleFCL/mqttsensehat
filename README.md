# MQTT SenseHat

A Python application that exposes Raspberry Pi SenseHat LED matrix control via MQTT, with support for animations, effects, and Home Assistant auto-discovery.

## Features

- **LED Matrix Control**: Control the 8x8 LED matrix on Raspberry Pi SenseHat
- **Animations**: Built-in rainbow, rolling, flash, and colour fill animations
- **MQTT Integration**: Full MQTT support for remote control
- **Home Assistant**: Auto-discovery support for seamless integration
- **Docker Support**: Easy deployment with Docker and Docker Compose
- **Configurable**: YAML-based configuration for easy setup

## Supported Animations

- **Fill Colour**: Solid colour fill
- **Fill Rainbow**: Smooth rainbow colour cycling
- **Fill Rainbow Fast**: Fast rainbow colour cycling
- **Rolling Rainbow**: Rainbow pattern that rolls across the matrix
- **Rolling Rainbow Fast**: Fast rolling rainbow pattern
- **Flash Animation**: Flashing colour effects
- **Flash Animation Fast**: Fast flashing effects

## Requirements

### Hardware
- Raspberry Pi (any model with GPIO support)
- Raspberry Pi SenseHat

### Software
- Python 3.10 or higher
- MQTT Broker (e.g., Mosquitto)

## Installation

### Option 1: Docker (Recommended)

1. Clone the repository:
```bash
git clone https://github.com/rippleFCL/mqttsensehat.git
cd mqttsensehat
```

2. Copy the example configuration:
```bash
cp config.yml.example config.yml
```

3. Edit the configuration file:
```bash
nano config.yml
```

4. Run with Docker Compose:
```bash
docker compose up -d
```

### Option 2: Local Installation

1. Clone the repository:
```bash
git clone https://github.com/rippleFCL/mqttsensehat.git
cd mqttsensehat
```

2. Install Poetry (if not already installed):
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

3. Install dependencies:
```bash
poetry install
```

4. Copy and configure the config file:
```bash
cp config.yml.example config.yml
nano config.yml
```

5. Run the application:
```bash
poetry run python main.py
```

## Configuration

Create a `config.yml` file based on the provided example:

```yaml
username: "your_mqtt_username"
password: "your_mqtt_password"
host: "mqtt.broker.address"
base_topic: "home/sensehat"
device_name: "sensehat"
log_level: "INFO"  # Optional: DEBUG, INFO, WARNING, ERROR
```

### Configuration Parameters

- `username`: MQTT broker username
- `password`: MQTT broker password
- `host`: MQTT broker hostname or IP address
- `base_topic`: Base MQTT topic for all device communications
- `device_name`: Device identifier for Home Assistant discovery
- `log_level`: Logging level (optional, defaults to INFO)
- `ha_discovery`: Enables device autodiscovery in homeassistant

## Home Assistant Integration

The application automatically publishes Home Assistant discovery messages. Once running, the SenseHat will appear as a light entity in Home Assistant with support for:

- On/Off control
- Brightness adjustment
- RGB colour selection
- Effect selection


## MQTT Topics

The application subscribes to and publishes on the following topic structure:
```
{base_topic}/
├── state              # Current state (published by device)
├── effect             # Command topic for all controls (state, brightness, colour, effects)
├── animation/cmd      # Direct animation commands
└── availability       # Device availability status (online/offline)
```

### Command Examples

Basic device control (state, brightness, colour, effects) goes through the `{base_topic}/effect` topic using JSON payloads.

#### Turn On/Off
```bash
mosquitto_pub -h your_broker -t "home/sensehat/effect" -m '{"state": "ON"}'
mosquitto_pub -h your_broker -t "home/sensehat/effect" -m '{"state": "OFF"}'
```

#### Set Colour (RGB)
```bash
mosquitto_pub -h your_broker -t "home/sensehat/effect" -m '{"colour": {"r": 255, "g": 0, "b": 0}}'
```

#### Set Brightness
```bash
mosquitto_pub -h your_broker -t "home/sensehat/effect" -m '{"brightness": 128}'
```

#### Start Animation/Effect
```bash
mosquitto_pub -h your_broker -t "home/sensehat/effect" -m '{"effect": "Fill rainbow"}'
mosquitto_pub -h your_broker -t "home/sensehat/effect" -m '{"effect": "Rolling rainbow fast"}'
```

#### Combined Commands
```bash
# Turn on with red colour and half brightness
mosquitto_pub -h your_broker -t "home/sensehat/effect" -m '{"state": "ON", "colour": {"r": 255, "g": 0, "b": 0}, "brightness": 128}'
```

#### Available Effects
- `Rolling rainbow` - Rolling rainbow pattern
- `Rolling rainbow fast` - Fast rolling rainbow
- `Fill rainbow` - Smooth rainbow cycling
- `Fill rainbow fast` - Fast rainbow cycling
- `Flash colour` - Flashing colour effects (uses current colour)
- `Flash colour fast` - Fast flashing effects (uses current colour)

## Advanced Commands

### Direct Animation Handler

The application also provides a direct animation handler for more granular control over animations. This handler subscribes to the `animation/cmd` topic and allows you to trigger specific animations with custom parameters.

#### Animation Handler Topic
```
{base_topic}/animation/cmd
```

#### Available Direct Animations

The animation handler supports the following animations with parameters:

- **`fill_rainbow`** - Smooth rainbow cycling animation
- **`fill_colour`** - Solid colour fill (requires RGB colour tuple)
- **`rolling_rainbow`** - Rolling rainbow pattern across the matrix
- **`flash_colour`** - Flashing colour animation (requires RGB colour tuple)

#### Direct Animation Examples

##### Fill with Specific Colour
```bash
# Fill the matrix with blue colour
mosquitto_pub -h your_broker -t "home/sensehat/animation/cmd" -m '{"fill_colour": [[0, 0, 255]]}'
```

##### Start Rainbow Animation
```bash
# Start a smooth rainbow cycling animation
mosquitto_pub -h your_broker -t "home/sensehat/animation/cmd" -m '{"fill_rainbow": []}'
```

##### Rolling Rainbow Pattern
```bash
# Start a rolling rainbow pattern
mosquitto_pub -h your_broker -t "home/sensehat/animation/cmd" -m '{"rolling_rainbow": []}'
```

##### Flash Colour Animation
```bash
# Flash with red colour
mosquitto_pub -h your_broker -t "home/sensehat/animation/cmd" -m '{"flash_colour": [[255, 0, 0]]}'
```

**Note**: The animation handler expects parameters as arrays. For colour-based animations, pass the RGB values as `[[r, g, b]]`. For animations without parameters, use an empty array `[]`.

## Animation Reference

### Animation Classes and Parameters

This section provides detailed information about each animation class, their parameters, and how to use them programmatically or via MQTT.

#### FillColour
**Purpose**: Fills the entire LED matrix with a solid colour.

**Parameters**:
- `colour` (tuple[int, int, int]): RGB colour values (0-255 for each component)

**Example Usage**:
```bash
mosquitto_pub -t "home/sensehat/animation/cmd" -m '{"fill_colour": [[255, 0, 0]]}'
```

#### FillRainbow
**Purpose**: Creates a smooth rainbow colour cycling effect across the entire matrix.

**Parameters**:
- `delay` (float, optional): Time delay between colour transitions (default: 0.05 seconds)

**Example Usage**:
```bash
mosquitto_pub -t "home/sensehat/animation/cmd" -m '{"fill_rainbow": [0.1]}'
```

#### RollingRainbow
**Purpose**: Creates a rainbow pattern that rolls across the LED matrix with configurable wave width.

**Parameters**:
- `delay` (float, optional): Time delay between animation frames (default: 0.05 seconds)
- `width` (int, optional): Width of the rainbow wave pattern (default: 5)

**Example Usage**:
```bash
mosquitto_pub -t "home/sensehat/animation/cmd" -m '{"rolling_rainbow": [0.1, 5]}'
```


#### FlashAnimation
**Purpose**: Creates a flashing effect with a specified colour, pulsing between minimum and maximum brightness.

**Parameters**:
- `colour` (tuple[int, int, int], optional): RGB colour values (default: white (255, 255, 255))
- `min_brightness` (float, optional): Minimum brightness level (0.0-1.0, default: 0.3)
- `delay` (float, optional): Time delay between brightness steps (default: 0.001 seconds)

**Example Usage**:
```bash
mosquitto_pub -t "home/sensehat/animation/cmd" -m '{"flash_colour": [[0, 255, 0], 0.1, 0.002]}'
```


### Animation Control Notes

- **Colour Format**: All colours use RGB format with values from 0-255
- **Timing**: Delay values are in seconds; smaller values create faster animations
- **Persistence**: Animations continue until a new animation is set or the device is turned off

## Development

### Setup Development Environment

1. Clone and enter the repository:
```bash
git clone https://github.com/rippleFCL/mqttsensehat.git
cd mqttsensehat
```

2. Install development dependencies:
```bash
poetry install --with dev
```

3. Install pre-commit hooks:
```bash
poetry run pre-commit install
```

### Code Quality

The project uses:
- **Ruff**: For linting and code formatting
- **Pre-commit**: For automated code quality checks

Run linting manually:
```bash
poetry run ruff check
poetry run ruff format
```

---

**Note**: This application is designed specifically for Raspberry Pi with SenseHat hardware. It will not function properly on other platforms without the appropriate hardware.

