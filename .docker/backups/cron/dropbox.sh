#!/bin/sh

curl -X POST https://content.dropboxapi.com/2/files/upload \
    --header "Authorization: Bearer bWQZNnmuhRAAAAAAAAAAEEZ-EwkadOVzPFNepA21BI5CYHEoUDmK74jtMRQwh5Pj" \
    --header "Dropbox-API-Arg: {\"path\": \"/$1\"}" \
    --header "Content-Type: application/octet-stream" \
    --data-binary @/backups/$1

