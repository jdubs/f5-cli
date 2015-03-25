import bigsuds


class Connection(object):

    def __init__(self, host, user, password, partition, debug=False, verify=True):
        self.host = host
        self.user = user
        self.password = password
        self.partition = partition
        self.debug = debug
        if not verify:
            self.disable_ssl_cert_validation()

    def disable_ssl_cert_validation(self):
        # From https://www.python.org/dev/peps/pep-0476/#id29
        import ssl
        ssl._create_default_https_context = ssl._create_unverified_context

    def connect(self):
        """Create a connection to the device."""
        bigip = bigsuds.BIGIP(
            hostname=self.host,
            username=self.user,
            password=self.password,
            debug=self.debug)
        bclient = bigip.with_session_id()
        bclient.System.Session.set_transaction_timeout(60)
        bclient.System.Session.set_active_folder("/" + self.partition)
        return bclient
