CLI interface into F5.
======================

Managing an F5 through the web interface is a bummer. Why not wrap the
API in a CLI for easier management!

Pull requests welcome!


Assumptions
~~~~~~~~~~~

Some F5 operations take 10 seconds to complete.

1. The default node monitoring is ICMP, this monitor should be in
   /Common/icmp ⋅⋅\* Nodes should be created with their FQDN, and should
   have a valid A record
2. The default pool monitor is HTTP, this monitor should be in
   /Common/icmp ⋅⋅\* Specified nodes should be referenced with their
   FQDN & should use the same format as they were created above.
3. Virtual servers are assumed to balance HTTP traffic.
4. Virtual servers have the following profiles automatically assigned.
   ⋅⋅\* tcp ⋅⋅\* http ⋅⋅\* oneconnect
5. Creating a VS with a SSL profile, the CA should be available in the
   partition.


Usage examples
~~~~~~~~~~~~~~

Add some Nodes
^^^^^^^^^^^^^^^

list
''''

.. code-block:: bash

    python f5_cli.py --user john --host f5-1b.chicken.net --partition ops node list

Create
''''''

.. code-block:: bash

    python f5_cli.py --user john --host f5-1b.chicken.net --partition ops node create --nodes "web-n01.chicken.net, web-n02.chicken.net"

Delete Node
'''''''''''

.. code-block:: bash

    python f5_cli.py --user john --host f5-1b.chicken.net --partition ops node delete --nodes "web-n01.chicken.net, web-n02.chicken.net"

Pool
^^^^

list
''''

.. code-block:: bash

    python f5_cli.py --user john --host f5-1b.chicken.net --partition ops pool list

Create
''''''

.. code-block:: bash

    python f5_cli.py --user john --host f5-1b.chicken.net --partition ops pool create \
        --nodes "web-n01.chicken.net:80, web-n02.chicken.net:80" --pool\_name "web.chicken.net.net"

Delete Pool
'''''''''''

.. code-block:: bash

    python f5_cli.py --user john --host f5-1b.chicken.net --partition ops pool delete --pool\_name "web.chicken.net.net"

Upload SSL Files
^^^^^^^^^^^^^^^^

list
''''

.. code-block:: bash

    python f5_cli.py --user john --host f5-1b.chicken.net --partition ops ssl\_file list

Create/import SSL key & Cert
''''''''''''''''''''''''''''

.. code-block:: bash

    python f5_cli.py --user john --host f5-1b.chicken.net --partition ops ssl\_file create \
        --name web.chicken.net.net --key sample.key --certificate sample.cert

Delete SSL key & Cert
'''''''''''''''''''''

.. code-block:: bash

    python f5_cli.py --user john --host f5-1b.chicken.net --partition ops ssl\_file delete --name web.chicken.net.net

SSL profiles
^^^^^^^^^^^^

list
''''

.. code-block:: bash

    python f5_cli.py --user john --host f5-1b.chicken.net --partition ops ssl\_profile list

Create
''''''

.. code-block:: bash

    python f5_cli.py --user john --host f5-1b.chicken.net --partition ops ssl\_profile create --name web.chicken.net.net --certificate chicken.net.net --key chicken.net.net

Create SSL profile with CA
''''''''''''''''''''''''''

The chain fiile should be uploaded before hand.

.. code-block:: bash

    python f5_cli.py --user john --host f5-1b.chicken.net --partition ops ssl\_profile create --name web.chicken.net.net --certificate chicken.net.net --key chicken.net.net --chain chicken\_ca

Delete
''''''

.. code-block:: bash

    python f5_cli.py --user john --host f5-1b.chicken.net --partition ops ssl\_profile delete --name web.chicken.net.net

Virtual servers
^^^^^^^^^^^^^^^

list
''''

.. code-block:: bash

    python f5_cli.py --user john --host f5-1b.chicken.net --partition ops virtual\_server list

Create
''''''

.. code-block:: bash

    python f5_cli.py --user john --host f5-1b.chicken.net --partition ops virtual\_server create \
        --vip\_name "web.chicken.net.net" --vip\_address "10.1.1.25" \
        --port 80 --protocol TCP --pool chicken.net.net --type http

Create Virtual server with SSL profile
''''''''''''''''''''''''''''''''''''''

.. code-block:: bash

    python f5_cli.py --user john --host f5-1b.chicken.net --partition ops virtual\_server create \
        --vip\_name "web.chicken.net.net" --vip\_address "10.1.1.25" \
        --port 443 --protocol TCP --pool chicken.net.net --ssl\_profile chicken.net.net --type https --http\_profile ci\_http

Additional profiles to be applied at virtual server creation
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

.. code-block:: bash

--snat - Secure network translation, available options: automap\|none
--protocol\_profile - Specified TCP & UDP profile --http\_profile
-Specified HTTP profile, defaults to the default http profile.

Delete
''''''

.. code-block:: bash

    python f5_cli.py --user john --host f5-1b.chicken.net --partition ops virtual\_server delete --vip\_name "web.chicken.net.net"

python deps
~~~~~~~~~~~~

* `dnspython <http://www.dnspython.org/>`_
