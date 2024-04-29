[fwBasic]
status = enabled
incoming = deny
outgoing = allow
routed = disabled

[Rule0]
ufw_rule = 20595/udp DENY IN Anywhere
description = /run/media/mojtaba/My Passport/Games/ManorLords/ManorLords.exe
command = /usr/sbin/ufw deny in proto udp from any to any port 20595
policy = deny
direction = in
protocol = 
from_ip = 
from_port = 
to_ip = 
to_port = 20595/udp
iface = 
routed = 
logging = 

[Rule1]
ufw_rule = 20595/udp DENY OUT Anywhere (out)
description = /run/media/mojtaba/My Passport/Games/ManorLords/ManorLords.exe
command = /usr/sbin/ufw deny out proto udp from any to any port 20595
policy = deny
direction = out
protocol = 
from_ip = 
from_port = 
to_ip = 
to_port = 20595/udp
iface = 
routed = 
logging = 

[Rule2]
ufw_rule = 20595/udp (v6) DENY IN Anywhere (v6)
description = /run/media/mojtaba/My Passport/Games/ManorLords/ManorLords.exe
command = /usr/sbin/ufw deny in proto udp from any to any port 20595
policy = deny
direction = in
protocol = 
from_ip = 
from_port = 
to_ip = 
to_port = 20595/udp
iface = 
routed = 
logging = 

[Rule3]
ufw_rule = 20595/udp (v6) DENY OUT Anywhere (v6) (out)
description = /run/media/mojtaba/My Passport/Games/ManorLords/ManorLords.exe
command = /usr/sbin/ufw deny out proto udp from any to any port 20595
policy = deny
direction = out
protocol = 
from_ip = 
from_port = 
to_ip = 
to_port = 20595/udp
iface = 
routed = 
logging = 

