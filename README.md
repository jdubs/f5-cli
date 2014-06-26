#CLI interface into F5.
Managing an F5 through the web interface is a bummer. Why not wrap the API in a cli for easier management!

Pull requests welcome!

### Assumptions
Some f5 operations take a 10 seconds to complete.

1. The default node monitoring is ICMP, this monitor should be in /Common/icmp
⋅⋅* Nodes should be created with their FQDN, and should have a valid A record
2. The default pool monitor is HTTP, this monitor should be in /Common/icmp
⋅⋅* Specified nodes should be referenced with their FQDN & should use the same format as they were created above.
3. Virtual servers are assumed to balance HTTP traffic.
4. Virtual servers have the following profiles automatically assigned.
⋅⋅* tcp
⋅⋅* http
⋅⋅* oneconnect

5. Creating a VS with a SSL profile, the CA should be available in the partition.


### Usage example
#### Add some Nodes.
##### list
python f5-cli.py --user john6150 --host f5-1b.chicken.net --partition CI_Engineers node list

##### Create
python f5-cli.py --user john6150 --host f5-1b.chicken.net --partition CI_Engineers node create --nodes "web-n01.chicken.net, web-n02.chicken.net"

##### Delete Node
python f5-cli.py --user john6150 --host f5-1b.chicken.net --partition CI_Engineers node delete --nodes "web-n01.chicken.net, web-n02.chicken.net"


#### Pool
##### list
python f5-cli.py --user john6150 --host f5-1b.chicken.net --partition CI_Engineers pool list

##### Create
python f5-cli.py --user john6150 --host f5-1b.chicken.net --partition CI_Engineers pool create --nodes "web-n01.chicken.net:80, web-n02.chicken.net:80" --pool_name "web.chicken.net.net"

##### Delete Pool
python f5-cli.py --user john6150 --host f5-1b.chicken.net --partition CI_Engineers pool delete --pool_name "web.chicken.net.net"

#### Upload SSL Files
##### list
python f5-cli.py --user john6150 --host f5-1b.chicken.net --partition CI_Engineers ssl_file list

##### Create/import SSL key & Cert
python f5-cli.py --user john6150 --host f5-1b.chicken.net --partition CI_Engineers ssl_file create --name web.chicken.net.net --key sample.key --certificate sample.cert

##### Delete SSL key & Cert
python f5-cli.py --user john6150 --host f5-1b.chicken.net --partition CI_Engineers ssl_file delete --name web.chicken.net.net 



####  SSL profiles
##### list

python f5-cli.py --user john6150 --host f5-1b.chicken.net --partition CI_Engineers ssl_profile list

##### Create
python f5-cli.py --user john6150 --host f5-1b.chicken.net --partition CI_Engineers ssl_profile create --name web.chicken.net.net --certificate chicken.net.net --key chicken.net.net


##### Create SSL profile with CA
###### The chain fiile should be uploaded before hand.

python f5-cli.py --user john6150 --host f5-1b.chicken.net --partition CI_Engineers ssl_profile create --name web.chicken.net.net --certificate chicken.net.net --key chicken.net.net --chain chicken_ca

##### Delete
python f5-cli.py --user john6150 --host f5-1b.chicken.net --partition CI_Engineers ssl_profile delete --name web.chicken.net.net 

#### Virtual servers
##### list
python f5-cli.py --user john6150 --host f5-1b.chicken.net --partition CI_Engineers virtual_server list

##### Create
python f5-cli.py --user john6150 --host f5-1b.chicken.net --partition CI_Engineers virtual_server create --vip_name "web.chicken.net.net" --vip_address "10.23.251.55" --port 80 --protocol TCP --pool chicken.net.net --type http

##### Create Virtaul server with SSL profile.
python f5-cli.py --user john6150 --host f5-1b.chicken.net --partition CI_Engineers virtual_server create --vip_name "web.chicken.net.net" --vip_address "10.23.251.55" --port 443 --protocol TCP --pool chicken.net.net --ssl_profile chicken.net.net --type https --http_profile ci_http

##### Additional profiles to be applied at virtaul server creation.
--snat - Secure network translation, available otpions: automap|none
--protocol_profile - Specified TCP & UDP profile
--http_profile -Specified HTTP profile, defaults to the default http profile.

##### Delete
python f5-cli.py --user john6150 --host f5-1b.chicken.net --partition CI_Engineers virtual_server delete --vip_name "web.chicken.net.net"


######python deps:
dnspython
