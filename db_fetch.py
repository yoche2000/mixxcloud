## a python lib to fetch info from db


## Tenant
'''
createTenant(tenantID)  ->  add tenant to database
readTenant(tenantID)    ->  return tenant info
deleteTenant(tenantID)  ->  delete tenant from database,
                            delete all instances associated to tenant
verifyTenant(tenantID)  ->  if tenant in database , return True/False
'''

## VPC
'''
vpc.create(tenantID, vpcID) ->  add nes VPC under a tenant in db
vpc.read(tenantID, vpcID)   ->  read VPC info 
vpc.list((tenantID)         ->  return a list of vpc owned by a tenant
vpc.delete(tenantID, cpvID) ->  delete vpc from database
vpc.setRouter(RouterID)
vpc.setIP(poolIP)
'''

## subnet

## VM


