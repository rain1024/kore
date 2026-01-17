# Gallery

## dog.kore

```kore
object DOG

animate DOG.go

save dog.gif
```

## diagram1.kore

```kore
architecture
    group api(cloud)[API]

    service db(database)[Database] in api
    service disk1(disk)[Storage] in api
    service server(server)[Server] in api

    db:L -- R:server
    disk1:T -- B:server
```
