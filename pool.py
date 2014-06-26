import dns.resolver
import datetime, re
import dns.resolver

class Pool:    
    def __init__(self, connection, partition, parser):
        self.connection = connection
        self.partition = partition
        connection.System.Session.set_active_folder("/"+self.partition)
        self.parser = parser
        
    
    def list(self):
      """
          List all pools in a partition

          @param self - the object type
      """
      return self.connection.LocalLB.Pool.get_list()
        
    def create(self, parser):
      """
          Create a Pool

          @param self - the object type
          @param parser - the f5 connection to use

      """
      self.parser.add_argument('--pool_name', action='store', dest='pool_name', required=True, help='Name of the pool')
      self.parser.add_argument('--nodes', action='store', dest='nodes', required=True, help='Comma seperated list of nodes')
      args = self.parser.parse_args()
      pool_name = args.pool_name
      username = args.username
      nodes = args.nodes.replace(' ','')
      pool_member_list = []
      for x in nodes.split(','):
      	pool_member = {}
      	y = x.split(':')
        pool_member['name'] = str(y[0])
        pool_member['port'] = int(y[1])
        try:
          answers = dns.resolver.query(pool_member['name'], 'A')
          for rdata in answers:
            pool_member['address'] = rdata.address
        except dns.resolver.NXDOMAIN:
          raise Exception("{} did not have a valid A record, please add one and try again".format(pool_member['name']))
          
      	
        if pool_member['port'] == 80:
            pool_member['monitor'] = 'http'
        elif pool_member['port'] == 8080:
            pool_member['monitor'] = 'http'
        elif pool_member['port'] == 443:
            pool_member['monitor'] = 'https'
        elif pool_member['port'] == 8443:
            pool_member['monitor'] = 'https'
        elif pool_member['port'] == 8193:
            pool_member['monitor'] = 'http'
        elif pool_member['port'] == 5432:
            pool_member['monitor'] = 'Postgres_DB_Monitor'
        else:
            pool_member['monitor'] = 'TCP'
      	pool_member_list.append(pool_member)
        
      if self.__create(pool_name, pool_member_list, username):
        return True

    def __create(self, pool_name, pool_member_list, username):
      """
          Creates a pool with a given pool_name, adds nodes as pool members 
          and updates the entities description to say what user and time 
          that it was created.

          @param self - the object type
          @param parser - the f5 connection to use

      """
      """Actually creates the pool after everything has been parsed"""
      lbmethod = "LB_METHOD_ROUND_ROBIN"
      pool = ('/%s/%s') % (self.partition, pool_name)
      try:
        member_list_address_port = []
        for members in pool_member_list:
          member_list = {}        
          member_list['address'] = members['address']
          member_list['port'] = members['port']
          member_list_address_port.append(member_list)

        
        print member_list_address_port
        self.connection.LocalLB.Pool.create(
                pool_names = [pool_name],
                lb_methods = [lbmethod],
                members = [member_list_address_port]
        )
        
        self.connection.LocalLB.Pool.set_monitor_association( 
          monitor_associations = [{'monitor_rule': {'monitor_templates': ['/Common/http'], 'quorum': 0,
            'type': 'MONITOR_RULE_TYPE_SINGLE'}, 'pool_name': [pool_name]}]
        )
        

        description = ("Added by %s via cli on %s") % (username, datetime.datetime.now())
        self.connection.LocalLB.Pool.set_description ([pool_name], [description] )
        print ("Added Pool: %s" ) % ([pool_name])
        return True
      except:
        raise Exception("Failed to add pool")
    
    
    def delete(self, parser):
      """
          Deletes a pool in a given partition

          @param self - the object type
          @param parser - the f5 connection to use

      """
      self.parser.add_argument('--pool_name', action='store', dest='pool_name', required=True, help='Name of the pool to delete')
      args = self.parser.parse_args()
      pool_name = "/{}/{}".format(args.partition,args.pool_name)
      if pool_name in self.list():
        try:
          self.connection.LocalLB.Pool.delete_pool(
            pool_names = [ args.pool_name ] )
          return True
        except:
          raise Exception("Failed to delete Pool")
          return False
      else:
        print "Pool {} does not exist".format(pool_name)
        return False
