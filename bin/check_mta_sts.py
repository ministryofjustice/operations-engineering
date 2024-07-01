import boto3
from botocore.exceptions import NoCredentialsError

# Usage:
#   Fill in AWS creds
#   Run the script
#   Action output

# Improvements:
#   Look up domains dynamically
#   Add this to actions somewhere

# AWS credentials
AWS_ACCESS_KEY_ID = ""
AWS_SECRET_ACCESS_KEY = ""
AWS_SESSION_TOKEN = ""

# Create a boto3 client for s3
s3 = boto3.client('s3',
                  aws_access_key_id=AWS_ACCESS_KEY_ID,
                  aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                  aws_session_token=AWS_SESSION_TOKEN)

# The base URL for the S3 buckets and other objects key
BASE_URL = "https://s3.amazonaws.com/880656497252."
SUFFIX = ".well-known/mta-sts.txt"

# The List of Domains to check
domains = ["ccrc.gov.uk",
           "cjit.gov.uk",
           "cshrcasework.justice.gov.uk",
           "devl.justice.gov.uk",
           "g.justice.gov.uk",
           "govfsl.com",
           "hmiprisons.gov.uk",
           "hmiprobation.gov.uk",
           "ima-citizensrights.org.uk",
           "imb.org.uk",
           "judicialappointments.gov.uk",
           "judicialconduct.gov.uk",
           "judicialombudsman.gov.uk",
           "judiciary.uk",
           "justice.gov.uk",
           "lawcommission.gov.uk",
           "newsletter.ima-citizensrights.org.uk",
           "obr.uk",
           "ospt.gov.uk",
           "ppo.gov.uk",
           "publicguardian.gov.uk",
           "sentencingcouncil.gov.uk",
           "sentencingcouncil.org.uk",
           "ukgovwales.gov.uk",
           "victimscommissioner.org.uk",
           "yjb.gov.uk",
           "yjbservicespp.yjb.gov.uk",
           "youthjusticepp.yjb.gov.uk"]

# A list to store the domains that failed to check
failed_domains = []

# Check both domains MTA STS 
for domain in domains:
    # Bucket Name
    bucket_name = f"880656497252.{domain}"

    try:
        # Try to get object from the bucket
        response = s3.get_object(Bucket=bucket_name, Key=SUFFIX)
        # Read the object content and check if it contains "mode enforce"
        sts_content = response['Body'].read().decode('utf-8')
        has_enforce = any(line.startswith("mode: enforce")
                          for line in sts_content.split('\n'))
        # If "mode: enforce is not found, and the domain to the failed_domains list"
        if not has_enforce:
            failed_domains.append(f"{domain} (No 'mode: enforce')")
    except NoCredentialsError:
        # If AWS credentials are not found, add the domain to the failed_domain list
        failed_domains.append(f"{domain} (AWS credentials not found)")
    except Exception as e:
        # if any other error occurs, add the domain to the failed_domain list
        failed_domains.append(f"{domain} (Exception: {e}")

# Display Failed domains
for domain in failed_domains:
    print(domain)
