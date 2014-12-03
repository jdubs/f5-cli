#!/usr/bin/env python
'''
    ssl_profile.py


    Configure a basic profile with the defaults
    # python ssl_profile.py --host f5-1b.chicken.net \
            --partition CI_Engineers --name atom.chicken.net

    Configure a profile with the defaults but use a different parent profile
    # python ssl_profile.py --host f5-1b.chicken.net \
            --partition CI_Engineers --name atom.chicken.net \
            --default_profile /Common/clientssl-insecure-compatible

    # Configure SSL profile with a CA chain
    # python ssl_profile.py --host f5-1b.chicken.net \
            --partition /CI_Engineers --name atom.chicken.net \
            --chain /Common/SSL123_CA_Bundle.crt
'''

import sys
import base64
import pprint
import os
import sys
import datetime


class Ssl_file:

    def __init__(self, connection, partition, parser):
        self.connection = connection
        self.partition = partition
        connection.System.Session.set_active_folder("/" + self.partition)
        self.parser = parser

    def list(self):
        """
            List all SSL Profiles in a partition
        """
        return self.connection.Management.KeyCertificate.get_certificate_list(
            mode='MANAGEMENT_MODE_DEFAULT')

    def create(self, parser):
        """
            Uploads SSL certificates

            @param self - the object type
            @param parser - the f5 connection to use

        """
        parser.add_argument('--name', action='store', dest='name',
                            required=True, help='name for certificate/key/bundle')
        parser.add_argument('--certificate', action='store', dest='certificate',
                            default=None, required=False, help='Certificate file (PEM)')
        parser.add_argument('--key', action='store', dest='key',
                            default=None, required=False, help='Key file (PEM)')
        args = self.parser.parse_args()
        try:
            if args.certificate is not None:
                print "Reading file {}".format(args.certificate)
                with open(args.certificate, 'r') as fh:
                    certificate_data = fh.read()

                """ Uploading certificate data """
                print "Uploading certificate data"
                self.connection.Management.KeyCertificate.certificate_import_from_pem(
                    mode='MANAGEMENT_MODE_DEFAULT', cert_ids=[args.name],
                    pem_data=[certificate_data], overwrite=True)

            if args.key is not None:
                print "Reading file {}".format(args.key)
                with open(args.key, 'r') as fh:
                    key_data = fh.read()

                """ Uploading key data """
                print "Uploading key data"
                self.connection.Management.KeyCertificate.key_import_from_pem(
                    mode='MANAGEMENT_MODE_DEFAULT', key_ids=[args.name],
                    pem_data=[key_data], overwrite=True)

            print "Done!"
            return True
        except Exception, e:
            print e

    def delete(self, parser):
        """
            Deletes a ssl file in a given parition

            @param self - the object type
            @param parser - the f5 connection to use

        """
        self.parser.add_argument('--name', action='store', dest='name',
                                 required=True, help='Name of the SSL certificate key/pair to delete')
        args = self.parser.parse_args()
        ssl_name = "/{}/{}".format(args.partition, args.name)
        if ssl_name in str(self.list()):
            self.connection.Management.KeyCertificate.certificate_delete(
                mode='MANAGEMENT_MODE_DEFAULT', cert_ids=[ssl_name])

            self.connection.Management.KeyCertificate.key_delete(
                mode='MANAGEMENT_MODE_DEFAULT', key_ids=[ssl_name])
            return True
        else:
            print "SSL Key pair {} does not exist".format(ssl_name)
            return False
