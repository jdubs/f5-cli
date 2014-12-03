import dns.resolver
import os
import sys
import datetime
import pprint


class Node:

    def __init__(self, connection, partition, parser):
        self.connection = connection
        self.partition = partition
        connection.System.Session.set_active_folder("/" + self.partition)
        self.parser = parser

    def list(self):
        """
            List all nodes in a partition
        """
        return self.connection.LocalLB.NodeAddressV2.get_list()

    def create(self, parser):
        """
            Create a virtual server

            @param self - the object type
            @param parser - the f5 connection to use

        """
        self.parser.add_argument(
            '--nodes', action='store', dest='nodes', required=True, help='Comma seperate list of nodes')

        args = self.parser.parse_args()
        username = args.username
        if args.nodes:
            nodes_args = args.nodes.replace(' ', '')
            node_list = []
            for x in nodes_args.split(','):
                node = {}
                y = x.split(':')
                node['name'] = str(y[0])
                try:
                    answers = dns.resolver.query(node['name'], 'A')
                    for rdata in answers:
                        node['address'] = rdata.address
                    self.__create(node, username)
                except dns.resolver.NXDOMAIN:
                    raise Exception(
                        "%s did not have a valid A record, pleaes add one and try again".format(node['name']))
            return True
        else:
            print "Please specify the nodes that you would like to add"

    def __create(self, node, username):
        """
            Creates a node with a default ICMP monitor and upates the description.

            @param self - the object type
            @param parser - the f5 connection to use

        """
        try:
            self.connection.LocalLB.NodeAddressV2.create(
                nodes=[node['name']], addresses=[node['address']], limits=[0])
            description = ("Added by %s via cli on %s") % (
                username, datetime.datetime.now())
            self.connection.LocalLB.NodeAddressV2.set_description(
                [node['name']], [description])
        except:
            raise Exception("Failed to create node")
        try:
            self.connection.LocalLB.NodeAddressV2.set_monitor_rule([node['name']],
                                                                   [{'monitor_templates': [
                                                                       '/Common/icmp'], 'quorum': 0, 'type': 'MONITOR_RULE_TYPE_SINGLE'}]
                                                                   )
            print ("Added node: %s with ICMP monitor") % (node['name'])
            return True
        except:
            raise Exception("Failed to assign ICMP monitor to a node")

    def delete(self, parser):
        """
            Deletes a Node

            @param self - the object type
            @param parser - the f5 connection to use

        """
        self.parser.add_argument(
            '--nodes', action='store', dest='nodes', required=True, help='Name of the nodes to delete')
        args = self.parser.parse_args()

        nodes_args = args.nodes.replace(' ', '')
        node_list = []
        for x in nodes_args.split(','):
            node = []
            y = x.split(':')
            node_list.append(str(y[0]))

        print node_list
        try:
            self.connection.LocalLB.NodeAddressV2.delete_node_address(
                nodes=[node_list])
            return True
        except:
            raise Exception("Failed to delete Node")
            return False
