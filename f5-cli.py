#!/usr/bin/env python

import os
import sys
import datetime
import getpass
import bigsuds
import argparse
import pprint
from argparse import ArgumentParser
from connection import Connection
from pool import Pool
from node import Node
from device import Device
from virtual_server import Virtual_server
from ssl_file import Ssl_file
from ssl_profile import Ssl_profile
from profile import Profile


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
    except Exception, e:
        print "ERROR: {}".format(e)
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


def main():
    parser = ArgumentParser(description="F5 Deployer")
    parser.add_argument('obj', action='store', help="The object you want to "
                        "work with. pool|virutal_server|node")
    parser.add_argument('action', action='store', help='list, create')
    parser.add_argument('--user', action="store", dest="username",
                        default=getpass.getuser(), required=False,
                        help="F5 User credentials. Defaults to current "
                        "user.")
    parser.add_argument('--password', action="store", dest="password", 
                        required=False, help="Username. Defaults "
                        "to current user.")
    parser.add_argument('--host', action="store", dest="host", required=True,
                        help='FQDN of the LB you are targeting')
    parser.add_argument('--partition', action="store", dest="partition",
                        default="Common", required=False,
                        help='The target partition. Defaults to Common')
    args, unknown = parser.parse_known_args()
    
    if args.password is None:
      print ("Enter Password")
      password = getpass.getpass()
    else:
      password = args.password
      
    if args.obj not in ["pool", "virtual_server", "node", "ssl_file", "ssl_profile", "profile"]:
        print "Please specify a valid object. pool|virtual_server|node"
        raise Exception("Invalid object specified: {}".format(args.obj))

    if args.action not in ["list", "create", "delete"]:
        print "Please specify a valid action. list|create, delete"
        raise Exception("Invalid action specified: {}".format(args.action))

    connection = get_f5_connection(args.host, args.username, password, args.partition)
    if connection is False:
        raise Exception("Unable to get F5 connection")

    device = Device(connection)
    if device.is_current_node_active(args.partition) == True:
        ##### This call only works in F5 1.4<
        #if client:
        #  print device.get_config_sync_status()
        object_connection = get_object_connection(args.obj, connection,
                                                  args.partition, parser)
        if args.action == "list":
            print object_connection.list()
        elif args.action == "create":
          result = object_connection.create(parser)
          if result == True:
            print "Added {} Succesfully".format(args.obj)
            print device.sync_to_group()
          else:
            print "Error, operation did not succeed"
        elif args.action == "delete":
          result = object_connection.delete(parser)
          if result == True:
            print "Deleted {} Succesfully".format(args.obj)
            print device.sync_to_group()
          else:
            print "Error, operation did not succeed"
    else:
        print "The device you connected to is NOT THE MASTER"
        print ("The master is currenlty %s") % (device.get_active_node())
        raise Exception("Specified host is not the master")

if __name__ == "__main__":
    try:
      main()
    except Exception, e:
      print "ERROR: {}".format(e)
