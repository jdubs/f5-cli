#!/usr/bin/env python

from argparse import ArgumentParser
from ConfigParser import ConfigParser
import getpass
import os

from connection import Connection
from pool import Pool
from node import Node
from device import Device
from virtual_server import Virtual_server
from ssl_file import Ssl_file
from ssl_profile import Ssl_profile
from profile import Profile


config_file = '~/.f5-cli.ini'
objects = [
    "pool",
    "virtual_server",
    "node",
    "ssl_file",
    "ssl_profile",
    "profile",
]
actions = ["list", "create", "delete"]


def get_f5_connection(host, username, password, partition):
    """
    create a connection object to an f5 and return it

    @param host - f5 hostname
    @param username - user name to connection with
    @param password - the password to connect with
    @param partition - partition to work with
    """
    try:
        connection = Connection(host, username, password, partition).connect()
    except Exception as e:
        print("ERROR: {}".format(e))
        return False

    return connection


def get_object_connection(obj, connection, partition, parser):
    """
    get an object specific connection

    @param obj - the object type
    @param connection - the f5 connection to use
    @param partition - the partition to work with
    @param parser - our args parser for object specifc items
    """
    if obj == "pool":
        object_connection = Pool(connection, partition, parser)
    elif obj == "node":
        object_connection = Node(connection, partition, parser)
    elif obj == "virtual_server":
        object_connection = Virtual_server(connection, partition, parser)
    elif obj == "ssl_file":
        object_connection = Ssl_file(connection, partition, parser)
    elif obj == "ssl_profile":
        object_connection = Ssl_profile(connection, partition, parser)
    elif obj == "profile":
        object_connection = Profile(connection, partition, parser)
    else:
        raise Exception("Unknown object {}".format(obj))

    return object_connection


def get_config():
    config = ConfigParser(defaults={'password': None})
    config.read(os.path.expanduser(config_file))
    return config


def main():
    parser = ArgumentParser(description="F5 Deployer")
    parser.add_argument('obj', action='store', metavar='object_type',
                        choices=objects,
                        help='Object type. One of %(choices)s.')
    parser.add_argument('action', action='store', metavar='action',
                        choices=actions,
                        help='Action. One of %(choices)s.')
    parser.add_argument('--user', action="store", dest="user",
                        required=False,
                        help="User name. Defaults to current user.")
    parser.add_argument('--password', action="store", dest="password",
                        help="Password")
    parser.add_argument('--host', action="store", dest="host",
                        help='FQDN of the LB you are targeting')
    parser.add_argument('--partition', action="store", dest="partition",
                        default="Common", required=False,
                        help='The target partition. Defaults to Common')
    args, unknown = parser.parse_known_args()

    config = get_config()
    host = args.host or config.get('defaults', 'host')
    user = args.user or config.get(host, 'user')
    password = args.password or config.get(host, 'password')

    if password is None:
        prompt = 'Password for {user}@{host}: '.format(user=user, host=host)
        password = getpass.getpass(prompt)

    connection = get_f5_connection(host, user, password, args.partition)
    if not connection:
        raise Exception("Unable to get F5 connection")

    device = Device(connection)
    if device.is_current_node_active(args.partition):
        # This call only works in F5 1.4<
        # if client:
        #     print device.get_config_sync_status()
        object_connection = get_object_connection(args.obj, connection,
                                                  args.partition, parser)
        if args.action == "list":
            print(object_connection.list())
        elif args.action == "create":
            result = object_connection.create(parser)
            if result:
                print("Added {} Succesfully".format(args.obj))
                print(device.sync_to_group())
            else:
                print("Error, operation did not succeed")
        elif args.action == "delete":
            result = object_connection.delete(parser)
            if result:
                print("Deleted {} Succesfully".format(args.obj))
                print(device.sync_to_group())
            else:
                print("Error, operation did not succeed")
    else:
        print("The device you connected to is NOT THE MASTER")
        print("The master is currenlty %s") % (device.get_active_node())
        raise Exception("Specified host is not the master")


if __name__ == "__main__":
    main()
