import click
import munch

from lib.cloudflare import Cloudflare


@click.group()
def cf():
    pass


@cf.command()
@click.option("--record", "-r", help="name of record", metavar="")
@click.option(
    "--zone", "-z", help="zone that contains the record to update", metavar=""
)
def update_record(record, zone):
    Cloudflare().update_record(record, zone)


@cf.command()
def retrieve_zones() -> str:
    Cloudflare().print_zones()


@cf.command()
@click.option(
    "--zone",
    "-z",
    help="zone that contains the records to fetch",
    metavar="",
    required=True,
)
def retrieve_records(zone) -> str:
    Cloudflare().print_records(zone)


@cf.command()
def test_token():
    response = [
        entry.message
        for entry in munch.munchify(
            Cloudflare().test_token(),
        ).messages
    ][0]
    print(f"\n{response}")
