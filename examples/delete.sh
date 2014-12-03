#!/bin/bash

python f5-plow.py --user john6150 --host f5-1b.dev.ord1.us.ci.rackspace.net --partition CI_Engineers node delete --nodes "mbweb-n01.staging.ord1.us.ci.rackspace.net, mbweb-n02.staging.ord1.us.ci.rackspace.net"

python f5-plow.py --user john6150 --host f5-1b.dev.ord1.us.ci.rackspace.net --partition CI_Engineers pool delete --pool_name "mbweb.staging.ord1.us.ci.rackspace.net"

python f5-plow.py --user john6150 --host f5-1b.dev.ord1.us.ci.rackspace.net --partition CI_Engineers ssl_file delete --name mbweb.staging.ord1.us.ci.rackspace.net 

python f5-plow.py --user john6150 --host f5-1b.dev.ord1.us.ci.rackspace.net --partition CI_Engineers ssl_profile delete --name mbweb.staging.ord1.us.ci.rackspace.net 

python f5-plow.py --user john6150 --host f5-1b.dev.ord1.us.ci.rackspace.net --partition CI_Engineers virtual_server delete --vip_name "mbweb.staging.ord1.us.ci.rackspace.net"

