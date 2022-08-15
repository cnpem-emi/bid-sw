# bid_test


    argument('-ps', '--power-supply', dest='ps_type', choices=['fbp', 'fbp-dclink', 'fap'])
    argument('-bid', '--bid-id', dest='bid_id', type=int)
    argument('-memory', '--type-memory', dest='type_mem', type=int, choices=[1, 2], default=1)



Examples:

`python3 bid_flashing.py -bid 139 -memory 1` 
_Flashing DBs corresponding to BID #139 into BID memory_


`python3 bid_flashing.py -ps fbp -memory 2`
_Flashing DBs corresponding to FBPs into on-board memory._
