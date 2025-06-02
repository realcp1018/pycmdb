#### ! All the current models should be recorded in this file! Every time you add a new model, remember to add it here.
```
interface CI {
    id  BigInteger
    name String!    @uniq
    create_time DateTime  @index
    update_time DateTime  @index
    status String(10)!   @default("online") "online, offline, inventory, unknown; default: online"
    notes String
}
```
```
model User@tablename("user") inherit CI {
    uid String @uniq "user unique id"
    email String(64)! @uniq "email address"
    mobile String(20)! @uniq "phone number"
    dept String "department name"
}
```
```
model Item@tablename("item") inherit CI {
    uid String  @uniq  "item unique id"
    owner User! @index "item owner"
    members String  "item member list"
    level   String(10)!  @default("P1")   "item level: P1, P2, P3, P4, P5"
}
```
```
model Machine@tablename("machine") inherit CI {
    uid String @uniq "machine unique id"
    ip String(20)! @uniq "machine ip address"
    is_physical Boolean @default(false)    "physical machine or virtual machine"
    cpu Integer "cpu core number"
    memory Integer  "memory(GB)"
    disk   Integer  "disk size(GB)"
    is_ssd  Boolean @default(false)   "is ssd"
}
```
```
model MySQLCluster@tablename("mysqlcluster") inherit CI {
    port    Integer @default(3306)  "cluster port"
    item Item   "cluster item"
    rw_domain   String  "cluster read-write domain"
    ro_domain   String  "cluster read-only domain"
    rw_domain_ip   String(50)  "cluster read-write domain bound IP"
    ro_domain_ip   String(50)  "cluster read-only domain bound IP""
    version DBVersion  "cluster version"
    env String(10)! @default("prd") "cluster env:prd,stg,uat,dev"
    ha_type String(50)! "cluster ha type: standalone,master-slave,master-master,mha,orchestrator"
}
```
```
model MySQLInstance@tablename("mysqlinstance") inherit CI {
    machine DBMachine! "instance machine"
    port Integer @default(3306) "instance port"
    cluster MySQLCluster!   "cluster"
    role    String(10)   "instance role: Master/Slave/StandAlone/Mixed/Unknown"
    config_path  String(50)    "path of my.cnf"
}
```