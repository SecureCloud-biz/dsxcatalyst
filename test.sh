#!/usr/bin/env bash
curl -X GET localhost:8080/api/vms
curl -d '{"id":"dave1", "name":"donk", "tag":"janus"}' -X POST localhost:8080/api/vms
curl -d '{"id":"dave2", "parentid":"dave1", "name":"yeti", "tag":"edna"}' -X POST localhost:8080/api/vms
curl -d 'on' -X PATCH localhost:8080/api/vms/power/dave1
curl -d 'on' -X PATCH localhost:8080/api/vms/power/dave1
curl -d 'off' -X PATCH localhost:8080/api/vms/power/dave1
curl -d 'on' -X PATCH localhost:8080/api/vms/power/dave1
curl -d 'shutdown' -X PATCH localhost:8080/api/vms/power/dave1
curl -d 'on' -X PATCH localhost:8080/api/vms/power/dave1
curl -d 'suspend' -X PATCH localhost:8080/api/vms/power/dave1
curl -d 'on' -X PATCH localhost:8080/api/vms/power/dave1
curl -d 'pause' -X PATCH localhost:8080/api/vms/power/dave1
curl -d 'unpause' -X PATCH localhost:8080/api/vms/power/dave1
curl -X GET localhost:8080/api/vms/dave1/ipaddress
curl -d 'shutdown' -X PATCH localhost:8080/api/vms/power/dave1
curl -X DELETE localhost:8080/api/vms/dave1
curl -X DELETE localhost:8080/api/vms/dave2