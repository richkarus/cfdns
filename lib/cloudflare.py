import os
import yaml
import requests
import textwrap
import json

from prettytable import PrettyTable
from typing import List, Dict, Tuple, Any


class Cloudflare:
    def __init__(self):
        self.base_url = "https://api.cloudflare.com/client/v4"
        self.session = requests.Session()
        self.creds = self.load_credentials()
        self.test_endpoint = "user/tokens/verify"
        self.headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.creds[1]}",
        }
        self.priv_headers = {
            "Accept": "application/json",
            "X-Auth-Email": self.creds[0],
            "X-Auth-Key": self.creds[2],
        }

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

    def close(self):
        return self.session.close()

    def get(self, destination: str):
        try:
            response = self.session.get(
                f"{self.base_url}/{destination}",
                headers=self.headers,
            )
            response.raise_for_status()
            return response.json()

        except requests.HTTPError as http_error:
            raise Exception(
                f"Invalid request from Cloudflare: {http_error}"
            ) from http_error
        except requests.RequestException as err:
            raise Exception(err) from err

    def put(self, destination: str, payload):
        try:
            response = self.session.put(
                f"{self.base_url}/{destination}",
                headers=self.priv_headers,
                data=payload,
            )

            response.raise_for_status()
            return response.json()

        except requests.HTTPError as http_error:
            raise Exception(
                f"Invalid request from Cloudflare: {http_error}"
            ) from http_error
        except requests.RequestException as err:
            raise Exception(err) from err

    def test_token(self) -> Dict:
        """
        A test method to ensure token presented in client works in Cloudflare.
        """
        return self.get(self.test_endpoint)

    @property
    def zones(self) -> List:
        return self.get("zones")["result"]

    @property
    def current_ip(self) -> str:
        return self.session.get("https://api.ipify.org").text

    def load_credentials(self) -> str:
        """
        Load credentials from env or local yaml file
        to construct the Cloudflare client.
        """
        token = os.getenv("CF_API_TOKEN")
        if token:
            return token
        try:
            with open(r"config/cloudflare.yaml") as f:
                creds = yaml.load(f, Loader=yaml.FullLoader)
            return (creds["email"], creds["api_token"], creds["api_key"])
        except FileNotFoundError:
            print("File not found. Does config/cloudflare.yaml exist?")
        except KeyError as e:
            print(f"A key was not found. Key not found was: {e}")
        except Exception:
            print("Something has gone wrong reading the config file!")
        exit()

    def retrieve_zones(self) -> List:
        return [
            (
                entry["name"],
                entry["id"],
            )
            for entry in self.zones
            if not None
        ]

    def retrieve_dns_records(self, zone_id: str) -> List:
        return self.get(f"zones/{zone_id}/dns_records")["result"]

    def record_matches_cip(self, name: str, zone: str) -> bool:
        return self.find_record_in_zone(name, zone)["content"] == self.current_ip

    def update_record(self, record: str, zone: str) -> Tuple:
        """
        A method that checks if a record matches an expected value.
        In this instance, it is only used for checking against self.current_ip
        for Dynamic DNS.
        """
        if self.record_matches_cip(record, zone):
            return print("Values match! Nothing to do!")

        record_identifier = self.find_record_in_zone(record, zone)["id"]

        payload = {
            "type": "A",
            "name": record,
            "content": self.current_ip,
            "ttl": 1,
            "proxied": False,
        }

        return self.put(
            f"zones/{zone}/dns_records/{record_identifier}",
            json.dumps(payload),
        )

    def find_record_in_zone(self, name: str, zone: str) -> Any:
        records = self.retrieve_dns_records(zone)

        resp_record = next(
            (record for record in records if record["name"] == name),
            None,
        )

        return resp_record

    def print_zones(self) -> str:
        zones = self.retrieve_zones()
        zone_table = PrettyTable()
        zone_table.field_names = ["Domain", "Zone ID"]
        zone_table.hrules = 1
        zone_table.align = "l"
        for zone in zones:
            zone_table.add_row([zone[0], zone[1]])

        print(zone_table)

    def print_records(self, zone_id: str) -> str:
        records = self.retrieve_dns_records(zone_id)
        records_table = PrettyTable()
        records_table.field_names = ["Name", "Type", "Value", "ID"]
        records_table.hrules = 1
        records_table.align = "l"
        for record in records:
            records_table.add_row(
                [
                    record["name"],
                    record["type"],
                    textwrap.fill(record["content"], 60),
                    record["id"],
                ]
            )
        print(records_table)
