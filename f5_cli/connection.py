import bigsuds


class Connection(object):

    def __init__(self, host, user, password, partition, debug=False):
        self.host = host
        self.user = user
        self.password = password
        self.partition = partition
        self.debug = debug

    def connect(self):
        """Create a connection to the device."""
        try:
            bigip = bigsuds.BIGIP(
                hostname=self.host,
                username=self.user,
                password=self.password,
                debug=self.debug)
            try:
                bclient = bigip.with_session_id()
                bclient.System.Session.set_transaction_timeout(60)
                bclient.System.Session.set_active_folder("/" + self.partition)
                return bclient
            except bigsuds.OperationFailed as e:
                print(e)
        except bigsuds.ConnectionError as e:
            raise Exception("Authentication failed")
