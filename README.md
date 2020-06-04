# LiveTrackBot

> LiveTrackBot, the paragliding bot for Telegram that follows us.

This is a program to retrieve the point of a Livetrack, such as a SPOT or a Garmin, and send messages to a Telegram channel.

Sent messages are:

- **Start**: when a pilot takes off.

- **OK**: when a pilot sends the OK signal.

- **HELP**, **MOVE**, **CUSTOM**: other possible messages sent by the pilot.

Examples of messages:

![start message](https://github.com/axelfahy/LiveTrackBot/blob/media/livetrack_start.png)

![ok message](https://github.com/axelfahy/LiveTrackBot/blob/media/livetrack_ok.png)

The telegram key is stored inside a `.env` file and loaded using the `load_dotenv()` function from the `python-dotenv` package.

## Installation

```sh
git clone https://github.com/axelfahy/LiveTrackBot
cd LiveTrackBot
python -m venv venv-dev
source venv-dev/bin/activate
pip install -e .
```

## Usage

The program is available as a CLI. Possible options are the Telegram's channel and the livetrack's URL to use. The livetrack URL must have a `json4Others.php` page that contains the list of the pilots with their points in a JSON format.

```sh
livetrackbot --channel @my_channel --url https://my_livetrack.net/json4Others.php
```

## Deployment

The deployment is done using Docker.

The `Dockerfile.base` file builds an image containing the requirements.

The `Dockerfile.code` file copy the code and sets the entry point.

The logs are mounted as a volume.

## Development setup

```sh
git clone https://github.com/axelfahy/LiveTrackBot
cd LiveTrackBot
python -m venv venv-dev
source venv-dev/bin/activate
pip install -r requirements_dev.txt
pip install -e .
```

## Tests

Testing is currently only checking for style and linting (`pylint`, `flake8` and `mypy`).

```sh
make test
```

## Release History

* 0.1.0
    * Initial release.

## Meta

Axel Fahy – axel@fahy.net

Distributed under the MIT license. See ``LICENSE`` for more information.

[https://github.com/axelfahy](https://github.com/axelfahy)

## Contributing

1. Fork it (<https://github.com/yourname/yourproject/fork>)
2. Create your feature branch (`git checkout -b feature/fooBar`)
3. Commit your changes (`git commit -am 'Add some fooBar'`)
4. Push to the branch (`git push origin feature/fooBar`)
5. Create a new Pull Request

## Version number

To set a new version:

```sh
git tag v0.1.4
git push --tags
```
