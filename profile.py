class Profile:
  def __init__(self, connection, partition, parser):
    self.connection = connection
    self.partition = partition
    connection.System.Session.set_active_folder("/"+self.partition)
    self.parser = parser
  
  def list_profiles_types(self, obj):
    """
        Determines if the passsed in data is a valid 
        profile that we can manage.
    """
    valid_profiles = ['ProfileHttp']
    return valid_profiles

      
  def list_profile(self, profile):
    """
        List all profiles for a particular object
    """
    if self.__is_valid_profiles(profile):
      return self.connection.LocalLB.profile.get_list()
    else:
      return Exception("{} is not a valid profile".format(profile))
    
    
    
   
  def __is_valid_profiles(self, profile):
    """
        Is a valid profile on the F5

        @param self - the object type
        @param parser - the f5 connection to use

    """
    if profile in ['ProfileHttp']:
      return True
    else:
      return False