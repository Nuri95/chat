"""
create_client
"""

from yoyo import step

__depends__ = {}

steps = [
    step("create table client(secret varchar(80), username varchar(80));",
         "drop table client;")
]
