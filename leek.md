## Global addresses
- 0.A[n] - local mesh net
- 0.A[n].x[1] - local mesh net user
- A[1] - root mesh net
- 65534.A[128].x[n] - use public key A(256 bytes) to route to node x[n] in that network
- 65535 - loopback, redirect to 65535.0.0
- 65535.0.0 - loopback to your router
- 65535.0.1 - loopback to your master (first net in your router)
- 65535.1.1 - loopback to your master (second net in your router)
- 65535.1.0 - loopback to your pc (from second net, equal and redirect to 65535.0.0)
- 65535.0.x[n] - loopback to node x[n] in your net (first net in your router)

## Inner mesh addresses
- 0.0 - pointer to your router
- 1.0 - pointer to your router (from second net)
- 0.1 - pointer to your master (first net)
- 1.1 - pointer to your master (second net)
- 0.4 - pointer to your neighbour with id 4 (from first error)
- 255.3 - pointer to your neighbour with id 3 at your 256 net
Not allowed to use not 2 lenght addreses
- 1.3.2 - doesnt point at your id_3 neighbours child with id 2, raise error
- 1 - pointer to your mesh net, not allowed to be as dst, src or hop (just admins debug info), raise error
