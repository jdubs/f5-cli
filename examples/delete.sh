#!/bin/bash

python f5-plow.py --user john --host f5-1b.dev.xomar.net --partition ops node delete --nodes "mbweb-n01.staging.xomar.net, mbweb-n02.staging.xomar.net"

python f5-plow.py --user john --host f5-1b.dev.xomar.net --partition ops pool delete --pool_name "mbweb.staging.xomar.net"

python f5-plow.py --user john --host f5-1b.dev.xomar.net --partition ops ssl_file delete --name mbweb.staging.xomar.net 

python f5-plow.py --user john --host f5-1b.dev.xomar.net --partition ops ssl_profile delete --name mbweb.staging.xomar.net 

python f5-plow.py --user john --host f5-1b.dev.xomar.net --partition ops virtual_server delete --vip_name "mbweb.staging.xomar.net"

