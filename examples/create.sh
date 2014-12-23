#!/bin/bash

python f5-plow.py --user john --host f5-1b.dev.xomar.net --partition ops node create --nodes "mbweb-n01.staging.xomar.net, mbweb-n02.staging.xomar.net"

python f5-plow.py --user john --host f5-1b.dev.xomar.net --partition ops pool create --nodes "mbweb-n01.staging.xomar.net:80, mbweb-n02.staging.xomar.net:80" --pool_name "mbweb.staging.xomar.net"


python f5-plow.py --user john --host f5-1b.dev.xomar.net --partition ops ssl_file create --name mbweb.staging.xomar.net --key sample.key --certificate sample.cert


python f5-plow.py --user john --host f5-1b.dev.xomar.net --partition ops ssl_profile create --name mbweb.staging.xomar.net --certificate mbweb.staging.xomar.net --key mbweb.staging.xomar.net

python f5-plow.py --user john --host f5-1b.dev.xomar.net --partition ops virtual_server create --vip_name "mbweb.staging.xomar.net" --vip_address "10.23.251.55" --port 443 --protocol TCP --pool mbweb.staging.xomar.net --ssl_profile mbweb.staging.xomar.net

