# Docker Compose Build, Run, and Test Command

Execute Docker Compose build, run, and test operations on the specified host IP address.

## Usage
`/dc_test <host_ip>`

## Parameters
- `host_ip`: The IP address where Docker services should be accessible (e.g., 192.168.20.108)

## Actions Performed
1. **Build**: Execute `docker-compose build` to build all services
2. **Run**: Execute `docker-compose up -d` to start services in detached mode
3. **Test**: Verify services are running and accessible on the specified host IP
4. **Status Check**: Display running containers and their status

## Example
```bash
/dc_test 192.168.20.108
```

This will:
- Build the Docker Compose services
- Start them in detached mode
- Test connectivity to port 8000 on 192.168.20.108
- Show service status

## Implementation Steps
1. Run `docker-compose build` to build all services
2. Run `docker-compose up -d` to start services in background
3. Wait for services to be ready (sleep 10 seconds)
4. Test HTTP connectivity to http://{host_ip}:8000/health or similar endpoint
5. Run `docker-compose ps` to show service status
6. Display success message with access URLs

## Error Handling
- Check if docker-compose.yml exists
- Verify Docker and Docker Compose are installed
- Handle build failures
- Handle startup failures
- Provide clear error messages and troubleshooting steps