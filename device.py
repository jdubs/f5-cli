
import base64
from distutils.version import LooseVersion


class Device:
    def __init__(self, connection):
        self.connection = connection
        self.product_info = None

    def is_current_node_active(self, partition):
      """
          Determines if the version of F5 is succifient to determine fail over state

          @param self - the object type
          @param partition - target partition

      """
      if self.is_version_sufficient(min_version='11.3.0') is False:
          print "!!!!!!!!!!! WARNING !!!!!!!!!!!!!!!"
          print "! UNABLE TO VERIFY FAILOVER STATE !"
          print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
          stop = raw_input('Do you want to continue? [y|N]')
          if stop.strip() == "y" or stop.strip() == "Y":
              return True
          else:
              return False
      """ Determines if the connect device is the master, if not Bail with an error."""
      try:
        self.connection.System.Session.set_active_folder("/Common")
        local_device = self.connection.Management.Device.get_local_device()
        status = self.connection.Management.Device.get_failover_state([local_device])
        if status == ['HA_STATE_ACTIVE']:
          self.connection.System.Session.set_active_folder("/"+partition)
          return True
        else:
          return False
      except:
        raise Exception("Failed to determine if {} is a master".format(device))
    
    def get_active_node(self):
      """
          Determines if the target node is the active master

          @param self - the object type

      """
      try: 
        for device in self.connection.Management.Device.get_list():
          device_status = self.connection.Management.Device.get_failover_state([device])
          if device_status == ['HA_STATE_ACTIVE']:
            return device.replace('/Common/','')
      except:
        raise Exception("Failed to determine if host is the active node")
    
    def get_config(self, config_file='bigip.conf', partition='Common'):
        """
            Get the bigip configuration as a string for the given partition 

            @param self - the object type
            @param config_file - the f5 configuration file
            @param partition - the partition in question.

        """
        if partition == 'Common':
            path = "/config/{}".format(config_file)
        else:
            path = "/config/partitions/{}/{}".format(partition, config_file)

        offset = 0
        chunk_size = 32768
        config = ''
        while True:
            try:
                data = self.connection.System.ConfigSync.\
                    download_file(file_name=path, chunk_size=chunk_size,
                                  file_offset=offset)
                config += base64.b64decode(data['return']['file_data'])
                if data['return']['chain_type'] == "FILE_LAST" or \
                        data['return']['chain_type'] == "FILE_FIRST_AND_LAST":
                    break
            except Exception, e:
                print "WARNING: {} download failed".format(path)
                break
        return config


    def get_config_sync_status(self):
      """
          Determine if the cluster configuration has any pending writes.

          @param self - the object type
      """
      
      try:
        device_group = self.connection.Management.DeviceGroup.get_list()
        print self.connection.Management.DeviceGroup.get_sync_status([device_group])
        
      except:
        raise Exception("Target system has pending configuration, please sync beforehand.")
      
    def get_software_version(self):
      """
          Returns the version of the f5 system

          @param self - the object type
      """
      
      try:
          if self.product_info is None:
              self.product_info = self.connection.System.SystemInfo.\
                  get_product_information()
          return self.product_info['product_version']
      except:
          raise

    def get_partitions(self):
      """
          get an array of partitions for the device

          @param self - the object type
      """
        
      parts = client.Management.Partition.get_partition_list()
      partitions = []
      for part in parts:
          partitions.append(part['partition_name'])
      return partitions

    def is_version_sufficient(self, min_version):
      """
          Check to see if the device has at least the min_version

          @param self - the object type
      """
        
      try:
          current_version = self.get_software_version()
          return LooseVersion(current_version) >= LooseVersion(min_version)
      except:
          raise

    
    def sync_to_group(self):
      """
          After a change sync the conig to the device group

          @param self - the object type
      """
      
      try:
        self.connection.System.Session.set_active_folder("/Common")
        for failover_group in self.connection.Management.DeviceGroup.get_list():
          if 'device-group-failover' in failover_group:
            device_group = failover_group.replace("/Common/", '')
            self.connection.System.ConfigSync.synchronize_to_group_v2(
              group=device_group,device='',force=False
            )
            return "Cluster Sync Complete"
      except Exception as e:
        
        raise Exception("###############\n Cluster Sync Failure\n {} \n ###############\n".format(e))
        

