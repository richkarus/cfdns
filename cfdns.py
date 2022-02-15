import click
from cmds import cf_cmds


@click.group()
def cfdns():
    pass


# build click commands
cfdns.add_command(cf_cmds.cf)

if __name__ == "__main__":
    cfdns()
