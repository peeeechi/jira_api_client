# /bin/bash -eu

cd $(dirname $0)
env="./.env"

echo 'export JIRA_BASE_URL=""' > $env 
echo 'export JIRA_EMAIL=""' >> $env 
echo 'export JIRA_API_TOKEN=""' >> $env 
echo 'export JIRA_PROJECT_KEY=""' >> $env 
