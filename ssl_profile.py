#!/usr/bin/env python

class Ssl_profile:

  def __init__(self, connection, partition, parser):
    self.connection = connection
    self.partition = partition
    connection.System.Session.set_active_folder("/"+self.partition)
    self.parser = parser
  
  def list(self):
    """
        List all virtual servers in a partition
    """
    return self.connection.LocalLB.ProfileClientSSL.get_list()
    
  def create(self, parser):
    """
        Create a SSL Profile

        @param self - the object type
        @param parser - the f5 connection to use

    """
    parser.add_argument('--name', action='store', dest='name', 
            required=True, help='name for ssl profile')
    parser.add_argument('--certificate', action='store', dest='certificate', 
            default=None, required=False, help='Certificate file on F5')
    parser.add_argument('--key', action='store', dest='key', 
            default=None, required=False, help='Key file on F5')
    parser.add_argument('--chain', action='store', 
            dest='chain', default=None, required=False, 
            help='The chain certificate file')
    parser.add_argument('--default_profile', action='store', 
            dest='default_profile', default=None, required=False, 
            help='The parent profile for this profile (default: clientssl)')
  
    args = parser.parse_args()
    

    certificate_name = "/{}/{}.crt".format(args.partition, args.certificate)
    key_name = "/{}/{}.key".format(args.partition, args.key)
    chain_name = "/{}/{}.crt".format(args.partition, args.chain)
    common_chain_name = "/Common/{}.crt".format(args.chain)
    
    if not self.__certcheck(certificate_name):
      raise Exception("Provided certificate {} not on F5".format(
        certificate_name))

    if not self.__keycheck( key_name):
      raise Exception("Provided key {} not on F5".format(key_name))

    self.connection.LocalLB.ProfileClientSSL.create_v2(profile_names=[args.name],
      certs=[{'value': certificate_name, 'default_flag': False}], 
      keys=[{'value': key_name, 'default_flag': False}])

    if args.chain is not None:
      if not self.__certcheck(chain_name):
        if not self.__certcheck(common_chain_name):
          chain_name = common_chain_name
          print "Using chain certificate from /Common"
        else:
          raise Exception("Provided chain {} not in /Common".format( chain_name))
      else:
        raise Exception("Provided chain {} not in {}".format( chain_name, partition))
      
      self.connection.LocalLB.ProfileClientSSL.set_chain_file_v2(
        profile_names=[args.name],
        chains=[{'value': chain_name, 'default_flag': False}])
      print "Added chain certificate: {} to: {}".format(args.chain, args.name)
    
    if args.default_profile is not None:
      self.connection.LocalLB.ProfileClientSSL.set_default_profile(
        profile_names=[args.name], defaults=[args.default_profile])
    return True

  def delete(self, parser):
    self.parser.add_argument('--name', action='store', dest='name', required=True, help='Name of the ssl profile to delete')
    args = self.parser.parse_args()
    ssl_name = "/{}/{}".format(args.partition,args.name)
    
    if ssl_name in self.list():
      try:
        self.connection.LocalLB.ProfileClientSSL.delete_profile(
          profile_names = [ ssl_name ] )
        return True
      except:
        raise Exception("Failed to delete ssl profile - this ssl profile may be associated with another profile.")
        return False
    else:
      print "SSL profile {} does not exist".format(ssl_name)
      return False


  def __certcheck(self, certificate_name):
    partition = self.connection.System.Session.get_active_folder()
    f5_certificates = self.connection.Management.KeyCertificate.get_certificate_list(
            mode='MANAGEMENT_MODE_DEFAULT')
    if certificate_name in str(f5_certificates):
      return True



  def __keycheck(self, key_name):
    parition = self.connection.System.Session.get_active_folder()
    f5_keys = self.connection.Management.KeyCertificate.get_key_list(
            mode='MANAGEMENT_MODE_DEFAULT')
    if key_name in str(f5_keys):
      return True
