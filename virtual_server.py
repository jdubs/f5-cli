import dns.resolver
import os
import sys
import datetime
import re
import pprint
from pool import Pool
from profile import Profile


class Virtual_server:

    def __init__(self, connection, partition, parser):
        self.connection = connection
        self.partition = partition
        connection.System.Session.set_active_folder("/" + self.partition)
        self.parser = parser

    def list(self):
        """
            List all virtual servers in a partition
        """
        return self.connection.LocalLB.VirtualServer.get_list()

    def create(self, parser):
        """
            Create a virtual server

            @param self - the object type
            @param parser - the f5 connection to use

        """
        NETMASK = '255.255.255.255'
        self.parser.add_argument(
            '--vip_name', action='store', dest='vip_name', required=True, help='Name of the vip')
        self.parser.add_argument(
            '--vip_address', action='store', dest='vip_address', required=True, help='IP of VIP')
        self.parser.add_argument(
            '--port', action='store', dest='port', required=True, help='Port of Vip')
        self.parser.add_argument(
            '--protocol', action='store', dest='protocol', required=True, help="Vip's protocol, TCP, UDP")
        self.parser.add_argument(
            '--pool', action='store', dest='pool_name', required=True, help="Vip's backend pool")
        self.parser.add_argument('--type', action='store', dest='vip_type',
                                 required=True, help="The vip's type, HTTP, Postgresql, other")
        # profiles
        self.parser.add_argument('--ssl_profile', action='store', dest='ssl_profile', required=False,
                                 help="Enable & Apply a SSL profile, requires the name of the ssl profile.")
        self.parser.add_argument('--http_redirect', action='store', dest='http_redirect',
                                 required=False, help="Create the HTTP to HTTPS redirect")
        self.parser.add_argument('--snat_profile', action='store', dest='snat_profile',
                                 required=False, help="Set the snat profile. - defaults to auto_map.")
        self.parser.add_argument('--request_logging', action='store', dest='request_logging',
                                 required=False, help="Sets the remote host syslog logging")

        self.parser.add_argument('--http_profile', action='store', dest='http_profile',
                                 required=False, help="Set the http profile. - defaults to default http profile")
        self.parser.add_argument('--protocol_profile', action='store', dest='protocol_profile',
                                 required=False, help="Set the tcp profile. - defaults to defaults TCP profile")
        # Not Implmeneted for licesning reasons.
        self.parser.add_argument('--gzip_profile', action='store', dest='gzip_profile',
                                 required=False, help="Set the http compression profile. - defaults to none.")

        args = self.parser.parse_args()
        partition = args.partition
        connection = self.connection
        vip_name = self.__validate_vip_name(args.partition, args.vip_name)
        vip_address = self.__validate_address(args.vip_address)
        vip_port = self.__validate_port(args.port)
        vip_protocol = self.__validate_protocol(args.protocol.upper())
        vip_type = self.__validate_type(args.vip_type)
        pool_name = self.__validate_pool_name(
            args.pool_name, connection, partition, parser)
        ssl_profile = args.ssl_profile

        profile_list = []
        if args.protocol_profile is not None:
            profile_tcp = {
                "profile_context": "PROFILE_CONTEXT_TYPE_ALL", "profile_name": args.protocol_profile}
        else:
            profile_tcp = {
                "profile_context": "PROFILE_CONTEXT_TYPE_ALL", "profile_name": "tcp"}
        profile_list.append(profile_tcp)

        if vip_type == 'http' or vip_type == 'https':
            if args.http_profile is not None:
                profile_http = {"profile_name": args.http_profile}
            else:
                profile_http = {"profile_name": "http"}
            profile_list.append(profile_http)

        if args.gzip_profile is not None:
            gzip_profile = {"profile_name": args.gzip_profile}
            profile_list.append(gzip_profile)

        if args.ssl_profile is not None:
            ssl_profile = args.ssl_profile
            profile_ssl = {
                "profile_context": "PROFILE_CONTEXT_TYPE_CLIENT", "profile_name": ssl_profile}
            profile_list.append(profile_ssl)

        if args.request_logging is not None:
            logging_profile = args.request_logging
            request_logging = {
                "profile_name": "PROFILE_TYPE_REQUEST_LOGGING", "profile_name": logging_profile}
            profile_list.append(request_logging)

        vip_name_check = "/{}/{}".format(args.partition, args.vip_name)

        # try:
        # Why does the F5 return void on create??
        self.connection.LocalLB.VirtualServer.create(
            definitions=[{"name": vip_name, "address": vip_address,
                          "port": vip_port, "protocol": vip_protocol}],
            wildmasks=[NETMASK],
            resources=[
                {"type": "RESOURCE_TYPE_POOL", "default_pool_name": pool_name}],
            profiles=[profile_list],
        )
        self.connection.LocalLB.VirtualServer.set_source_address_translation_automap(
            [vip_name])
        # if args.snat_profile:
        #  print "Setting snat profile"
        #  self.set_snat_type(args.snat_profile, vip_name)
        if args.http_redirect == "true":
            vip_name = "/{}/{}-HTTP".format(args.partition, args.vip_name)
            if profile_ssl in profile_list:
                profile_list.remove(profile_ssl)
            self.connection.LocalLB.VirtualServer.create(
                definitions=[
                    {"name": vip_name, "address": vip_address, "port": "80", "protocol": vip_protocol}],
                wildmasks=[NETMASK],
                resources=[
                    {"type": "RESOURCE_TYPE_POOL", "default_pool_name": pool_name}],
                profiles=[profile_list],
            )
            self.connection.LocalLB.VirtualServer.add_rule(
                virtual_servers=[vip_name],
                rules=[[{"rule_name": '_sys_https_redirect', "priority": '1'}]]
            )
                # if args.snat_profile:
                #  print "Setting snat profile"
                #  self.set_snat_type(args.snat_profile, vip_name)
            self.connection.LocalLB.VirtualServer.set_source_address_translation_automap(
                [vip_name])
        return True
    # except:
        vip_name = "/{}/{}".format(args.partition, args.vip_name)
        if vip_name in self.list():
            self.connection.LocalLB.VirtualServer.delete_virtual_server(
                virtual_servers=[vip_name])
            raise Exception(
                "Failed to create Virtaul Server - rolling back creation of virtual server")
        else:
            raise Exception("Failed to create Virtaul Server")
        return False

    def delete(self, parser):
        """
            Deletes a virtual server in a partition

            @param self - the object type
            @param parser - the f5 connection to use

        """
        self.parser.add_argument(
            '--vip_name', action='store', dest='vip_name', required=True, help='Name of the vip to delete')
        args = self.parser.parse_args()
        vip_name = "/{}/{}".format(args.partition, args.vip_name)
        if vip_name in self.list():
            try:
                self.connection.LocalLB.VirtualServer.delete_virtual_server(
                    virtual_servers=[args.vip_name])
                return True
            except:
                raise Exception("Failed to delete Virtaul Server")
                return False
        else:
            print "Virtual Server {} does not exist".format(vip_name)
            return False

    def set_snat_type(self, snat_profile, vip_name):
        """
            Sets the Security Network Translation for a given vip

            @param self - the object type
            @param snat_profile - the type of snat to set, automap, none, pool
            @param vip_name - the vip name to apply the setting too.

        """
        if snat_profile in ['automap', 'none', 'pool']:
            if snat_profile == 'automap':
                try:
                    self.connection.LocalLB.VirtualServer.set_source_address_translation_automap(
                        [vip_name])
                    return True
                except:
                    raise Exception("Failed to set snat type to automap")
                    return False
            elif snat_profile == 'none':
                try:
                    self.connection.LocalLB.VirtualServer.set_source_address_translation_none(
                        [vip_name])
                    return True
                except:
                    raise Exception("Failed to set snat type to none")
                    return False
            elif snat_profile == 'pool':
                raise Exception("Snat pool not implemented")
                return False
        else:
            raise Exception(
                "Please specify the snat type, must be, automap or none. Snat pool not implmeneted")
            return False

    def __validate_vip_name(self, partition, vip_name):
        """
            Determines if the vip name is valid.

            @param self - the object type
            @param vip_name - Vip in question.

        """
        vip_name_check = "/{}/{}".format(partition, vip_name)
        if vip_name_check in self.list():
            raise Exception("Vip {} is already configured".format(vip_name))
            return False
        else:
            return str(vip_name)

    def __validate_pool_name(self, pool_name, connection, partition, parser):
        """
            Determines if the pool is valid before adding it to a Vip

            @param self - the object type
            @param pool_name - the pool to check
            @param connection - object connection
            @param partition, the partition that the pool is in.
            @param parser, the parser object

        """
        pool_name = "/{}/{}".format(partition, pool_name)
        if pool_name in Pool(connection, partition, parser).list():
            return pool_name
        else:
            raise Exception(
                "Could not find desired pool, Please create the pool first")
            return False

    def __validate_port(self, port):
        """
            Determines if the port is an integer.

            @param self - the object type
            @param port - the port to create the vip with.

        """
        try:
            return int(port)
        except ValueError:
            raise Exception("The port specified was not an integer.")
            return False

    def __validate_protocol(self, protocol):
        """
            Checks to see if the protocol is valid.

            @param self - the object type
            @param protocol - The protocol that the vip is in charge of.

        """
        if protocol in ['TCP', 'UDP', 'SCTP']:
            if protocol == 'TCP':
                protocol = 'PROTOCOL_TCP'
            if protocol == 'UDP':
                protocol = 'PROTOCOL_UDP'
            if protocol == 'SCTP':
                protocol = 'PROTOCOL_SCTP'
            return protocol
        else:
            raise Exception("Protocol needs to be TCP, UDP or SCTP")
            return False

    def __validate_address(self, vip_address):
        """
            Determines if the ip address is valid.

            @param self - the object type
            @param vip_address - Determines if the ip address is valid based upon regex.

        """
        ip_pattern_str = re.compile(
            '(([1-2]?[\d]{0,2}\.){1,3}([1-2]?[\d]{0,2})|any)')
        is_ip = ip_pattern_str.match(vip_address)
        if is_ip:
            return vip_address
        else:
            raise Exception(
                "{} is not an ip address, please try again".format(vip_address))
            print("%s is not an ip address, please try again") % (vip_address)
            return False

    def __validate_type(self, vip_type):
        """
            Determines if we should manage the vip type.

            @param self - the object type
            @param vip_type - the layer 7 name, http, https, postgresql, other

        """
        if vip_type in ['http', 'https', 'postgresql', 'other']:
            return vip_type
        else:
            raise Exception(
                "Please specify the type of VIP, http, https, postgresql, other")
            return False
