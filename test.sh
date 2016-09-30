#!/usr/bin/env bash
curl -d '{"id":"dave1", "name":"donk", "tag":"janus"}' -X POST localhost:8080/api/vms
curl -d '{"id":"dave2", "parentid":"dave1", "name":"yeti", "tag":"edna"}' -X POST localhost:8080/api/vms
curl -d 'on' -X PATCH localhost:8080/api/vms/power/photon1
curl -X GET localhost:8080/api/vms/photon1/ipaddress
curl -d 'shutdown' -X PATCH localhost:8080/api/vms/power/photon1