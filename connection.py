import bigsuds
class Connection:
  def __init__(self, host, user, password, partition):
    self.host = host
    self.user = user
    self.password = password
    self.partition = partition
  
  def connect(self):
    """
        Create a connection to the device.

        @param self - the object type

    """
    try:
      b = bigsuds.BIGIP(
        hostname = self.host, 
        username = self.user, 
        password = self.password
        )
      try:
        bclient = b.with_session_id()
        bclient.System.Session.set_transaction_timeout(60)
        bclient.System.Session.set_active_folder("/"+self.partition)
        
        return bclient
      except bigsuds.OperationFailed, e: 
        print e 
    except bigsuds.ConnectionError as e:
      raise Exception("Authentication failed")
