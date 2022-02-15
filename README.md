# cfdns

Cfdns is a dynamic DNS client that doesn't depend on the CloudFlare package.

## Installation

Use pip to install all dependencies.

```bash
pip install -r install/requirements.txt
```

## Usage

```
➜ cfdns.py cf
Usage: cfdns.py cf [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  retrieve-records
  retrieve-zones
  test-token
  update-record

➜ cfdns.py cf update-record -z ZONE_IDENTIFIER -r FQDN
```

