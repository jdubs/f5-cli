#!/bin/bash

python f5-plow.py --user john6150 --host f5-1b.dev.ord1.us.ci.rackspace.net --partition CI_Engineers node create --nodes "mbweb-n01.staging.ord1.us.ci.rackspace.net, mbweb-n02.staging.ord1.us.ci.rackspace.net"

python f5-plow.py --user john6150 --host f5-1b.dev.ord1.us.ci.rackspace.net --partition CI_Engineers pool create --nodes "mbweb-n01.staging.ord1.us.ci.rackspace.net:80, mbweb-n02.staging.ord1.us.ci.rackspace.net:80" --pool_name "mbweb.staging.ord1.us.ci.rackspace.net"


python f5-plow.py --user john6150 --host f5-1b.dev.ord1.us.ci.rackspace.net --partition CI_Engineers ssl_file create --name mbweb.staging.ord1.us.ci.rackspace.net --key sample.key --certificate sample.cert


python f5-plow.py --user john6150 --host f5-1b.dev.ord1.us.ci.rackspace.net --partition CI_Engineers ssl_profile create --name mbweb.staging.ord1.us.ci.rackspace.net --certificate mbweb.staging.ord1.us.ci.rackspace.net --key mbweb.staging.ord1.us.ci.rackspace.net

python f5-plow.py --user john6150 --host f5-1b.dev.ord1.us.ci.rackspace.net --partition CI_Engineers virtual_server create --vip_name "mbweb.staging.ord1.us.ci.rackspace.net" --vip_address "10.23.251.55" --port 443 --protocol TCP --pool mbweb.staging.ord1.us.ci.rackspace.net --ssl_profile mbweb.staging.ord1.us.ci.rackspace.net

