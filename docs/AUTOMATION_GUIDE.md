# AWS Ontology Automation Guide

> **⚠️ Superseded.** The daemon/cron/systemd/Docker options below (`automation/`) are deprecated
> in favor of [`.github/workflows/ontology-monitor.yml`](../.github/workflows/ontology-monitor.yml),
> a GitHub Actions workflow that runs on a schedule, uses an LLM to triage AWS "What's New"
> announcements against the PRD's declared scope, and opens a PR with proposed additions — see
> [`tools/propose_ontology_updates.py`](../tools/propose_ontology_updates.py) and
> [`automation/README.md`](../automation/README.md). Requires an `OPENAI_API_KEY` (or `ANTHROPIC_API_KEY`) repo secret.
> This guide is kept for reference; new setups should use the GitHub Actions workflow instead.

This guide covers all automation options for the AWS Ontology project, including scheduling, monitoring, and deployment strategies.

## Overview

The automation system provides multiple deployment options for keeping your AWS ontology up-to-date:

1. **Python Scheduler** - Cross-platform daemon with email notifications
2. **Cron Jobs** - Traditional Unix/Linux scheduling
3. **Systemd Service** - Linux system service integration
4. **Docker Container** - Containerized deployment
5. **Cloud Deployment** - AWS, GCP, Azure options

## Quick Start

### 1. Basic Setup

```bash
# Install dependencies
make install-deps

# Create automation configuration
make schedule-setup

# Test the automation
make schedule-test
```

### 2. Start Automated Monitoring

```bash
# Start as daemon (runs continuously)
make schedule-daemon

# Or run specific tasks once
make schedule-daily   # Daily AWS change monitoring
make schedule-weekly  # Weekly comprehensive report
```

## Deployment Options

### Option 1: Python Scheduler (Recommended)

**Best for:** Development, testing, cross-platform deployment

```bash
# Setup
make schedule-setup
# Edit automation/config.json for notifications

# Run as daemon
make schedule-daemon

# Or run specific tasks
python automation/schedule_monitoring.py --run-once daily
python automation/schedule_monitoring.py --run-once weekly
```

**Features:**
- ✅ Cross-platform (Windows, macOS, Linux)
- ✅ Email notifications with attachments
- ✅ Configurable schedules and thresholds
- ✅ Detailed logging and error handling
- ✅ Priority-based change classification

**Configuration Example:**
```json
{
  "notifications": {
    "enabled": true,
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "email_from": "your-email@gmail.com",
    "email_to": ["recipient@example.com"],
    "email_password": "your-app-password"
  },
  "schedules": {
    "daily_monitoring": "09:00",
    "weekly_report": "monday 08:00",
    "monthly_quality_check": "1st 07:00"
  }
}
```

### Option 2: Cron Jobs

**Best for:** Simple Linux/Unix deployments

```bash
# View examples
cat automation/crontab_example.txt

# Edit your crontab
crontab -e

# Add entries (adjust paths):
0 9 * * * cd /path/to/aws-ontology && source venv/bin/activate && make monitor-changes
0 8 * * 1 cd /path/to/aws-ontology && source venv/bin/activate && make monitor-weekly
```

**Features:**
- ✅ Native Unix/Linux integration
- ✅ Simple setup and management
- ✅ System-level reliability
- ❌ No built-in email notifications
- ❌ Limited error handling

### Option 3: Systemd Service

**Best for:** Production Linux servers

```bash
# Setup service
sudo cp automation/aws-ontology-monitor.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable aws-ontology-monitor
sudo systemctl start aws-ontology-monitor

# Monitor
sudo systemctl status aws-ontology-monitor
sudo journalctl -u aws-ontology-monitor -f
```

**Features:**
- ✅ Production-ready service management
- ✅ Automatic startup and restart
- ✅ System logging integration
- ✅ Security hardening
- ❌ Linux-only

### Option 4: Docker Container

**Best for:** Containerized environments, Kubernetes

```bash
# Build container
docker build -t aws-ontology-monitor -f automation/Dockerfile .

# Run with persistent data
docker run -d --name aws-ontology-monitor \
  -v $(pwd)/automation/logs:/opt/aws-ontology/automation/logs \
  -v $(pwd)/automation/reports:/opt/aws-ontology/automation/reports \
  aws-ontology-monitor:latest

# View logs
docker logs -f aws-ontology-monitor

# Run specific tasks
docker run --rm aws-ontology-monitor:latest daily
docker run --rm aws-ontology-monitor:latest weekly
```

**Features:**
- ✅ Consistent deployment across environments
- ✅ Easy scaling and orchestration
- ✅ Isolated dependencies
- ✅ Health checks included
- ✅ Multi-architecture support

## Scheduled Tasks

### Daily Monitoring
- **Purpose**: Track new AWS announcements
- **Schedule**: 9:00 AM daily (configurable)
- **Actions**:
  - Monitor AWS What's New feed
  - Classify changes by priority
  - Send alerts for high-priority changes
  - Generate daily reports

### Weekly Reports
- **Purpose**: Comprehensive change analysis
- **Schedule**: Monday 8:00 AM (configurable)
- **Actions**:
  - Monitor all sources (RSS, CloudFormation, etc.)
  - Compare with cached data
  - Generate comprehensive reports
  - Email weekly summaries

### Monthly Quality Checks
- **Purpose**: Ontology health validation
- **Schedule**: 1st of month, 7:00 AM
- **Actions**:
  - Run full test suite
  - Performance benchmarking
  - Quality metrics validation
  - Error reporting

### Quarterly Reviews
- **Purpose**: Strategic maintenance planning
- **Schedule**: First day of quarter, 6:00 AM
- **Actions**:
  - Generate review checklists
  - Assessment reports
  - Maintenance planning
  - Strategic recommendations

## Email Notifications

### Setup
```json
{
  "notifications": {
    "enabled": true,
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "email_from": "your-email@gmail.com",
    "email_to": ["team@example.com"],
    "email_password": "your-app-password"
  }
}
```

### Gmail Setup
1. Enable 2-factor authentication
2. Generate App Password: Google Account → Security → App passwords
3. Use app password in configuration

### Notification Types
- **🚨 High Priority Changes**: Immediate alerts for critical updates
- **📊 Weekly Reports**: Comprehensive change summaries
- **✅ Quality Check Results**: Monthly test results
- **⚠️ Error Alerts**: System failures and issues

## Cloud Deployment

### AWS (Recommended for AWS-focused ontology)

**Option A: EC2 with Systemd**
```bash
# Launch EC2 instance (t3.micro sufficient)
# Install project and dependencies
# Setup systemd service
# Configure CloudWatch logging
```

**Option B: ECS/Fargate**
```bash
# Build and push Docker image to ECR
# Create ECS task definition
# Setup scheduled tasks with EventBridge
# Configure CloudWatch logs and alarms
```

**Option C: Lambda**
```bash
# Package as Lambda deployment
# Use EventBridge for scheduling
# Store reports in S3
# Send notifications via SES
```

### Google Cloud Platform

**Option A: Compute Engine**
```bash
# Create VM instance
# Setup systemd service
# Configure Stackdriver logging
```

**Option B: Cloud Run**
```bash
# Deploy container to Cloud Run
# Use Cloud Scheduler for triggers
# Store data in Cloud Storage
```

### Azure

**Option A: Virtual Machine**
```bash
# Create Linux VM
# Setup systemd service
# Configure Azure Monitor
```

**Option B: Container Instances**
```bash
# Deploy to Azure Container Instances
# Use Logic Apps for scheduling
# Store data in Blob Storage
```

## Monitoring and Troubleshooting

### Log Locations
- **Python Scheduler**: `automation/logs/scheduler_YYYYMMDD.log`
- **Systemd Service**: `journalctl -u aws-ontology-monitor`
- **Docker Container**: `docker logs aws-ontology-monitor`
- **Cron Jobs**: System cron logs + output files

### Common Issues

**1. Permission Errors**
```bash
# Fix file permissions
chmod +x automation/docker-entrypoint.sh
chown -R user:group automation/

# For systemd, check user/group settings
```

**2. Python Import Errors**
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Verify dependencies
pip install -r requirements.txt
```

**3. Network/RSS Feed Issues**
```bash
# Test connectivity
curl https://aws.amazon.com/new/feed/

# Check firewall/proxy settings
# Verify DNS resolution
```

**4. Email Notification Failures**
```bash
# Test SMTP settings
python -c "import smtplib; s=smtplib.SMTP('smtp.gmail.com',587); s.starttls(); print('OK')"

# Check authentication credentials
# Verify app password for Gmail
```

### Health Checks

**Manual Health Check**
```bash
# Test monitoring tool
make monitor-changes

# Test automation
make schedule-test

# Check logs
tail -f automation/logs/scheduler_*.log
```

**Automated Health Checks** (Docker)
```bash
# Container includes health check
docker inspect aws-ontology-monitor | jq '.[0].State.Health'

# Custom health check
python -c "
import json
from pathlib import Path
log_file = Path('automation/logs').glob('scheduler_*.log')
if any('Starting scheduler daemon' in f.read_text() for f in log_file):
    print('Healthy')
else:
    print('Unhealthy')
"
```

## Best Practices

### Security
1. **Use dedicated user accounts** for automation processes
2. **Secure email credentials** (app passwords, not main passwords)
3. **Restrict file permissions** on configuration files
4. **Enable system firewalls** and limit network access
5. **Regular security updates** for system packages

### Reliability
1. **Monitor log files** for errors and patterns
2. **Set up log rotation** to prevent disk space issues
3. **Configure automated restarts** for failed services
4. **Test failover scenarios** regularly
5. **Backup configuration files** and data

### Performance
1. **Monitor resource usage** (CPU, memory, disk)
2. **Optimize scheduling** to avoid peak system times
3. **Configure timeouts** for external requests
4. **Use compression** for log files and reports
5. **Clean up old files** automatically

### Maintenance
1. **Regular dependency updates** (`pip list --outdated`)
2. **Review and tune schedules** based on AWS announcement patterns
3. **Analyze notification effectiveness** and adjust thresholds
4. **Update automation scripts** for new AWS services
5. **Document configuration changes** and rationale

## Scaling and Advanced Configuration

### Multiple Environments
```bash
# Development
automation/config-dev.json

# Staging  
automation/config-staging.json

# Production
automation/config-prod.json

# Use environment-specific configs
python automation/schedule_monitoring.py --config automation/config-prod.json
```

### Load Balancing
```bash
# Multiple monitoring instances
# Shared storage for reports
# Coordination via file locks or database
```

### Integration with CI/CD
```bash
# GitHub Actions example
name: Ontology Monitoring
on:
  schedule:
    - cron: '0 9 * * *'  # Daily at 9 AM
jobs:
  monitor:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - run: make schedule-daily
```

This automation guide provides comprehensive options for keeping your AWS ontology current with minimal manual effort while ensuring reliability and scalability. 