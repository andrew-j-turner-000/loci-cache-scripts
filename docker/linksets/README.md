# Automation of Linkset Creation

Code to automate the process of linkset creation. Currently specific for meshblocks and contracted catchments.

## Requirements

Requires environment variables configured in `../../common/common.sh` and in `./.env`

additionally valid `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` must be set prior to run

## Optional

Optionally set LOAD_LIMIT to test the link build process by loading a limited subset of input data

## Running

Run with `start.sh` to execute the default workflow

Modify docker-compose.yml to swap to the `tail -f...` command to enable manual execution then docker-compose exec linksets to execute manual commands in the `/app/` directory.

### Linkset upload

To upload a new version of the asgs 2016 mb data from WFS to S3 execute `cd /app/linksets/mb2cc && python preload_asgs_wfs.py` in the linksets container
