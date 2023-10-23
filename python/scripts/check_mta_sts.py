import boto3
from botocore.exceptions import NoCredentialsError

# Usage:
#   Fill in AWS creds
#   Run the script
#   Action output

# Improvements:
#   Look up domains dynamically
#   Add this to actions somewhere

# Auth
AWS_ACCESS_KEY_ID = ""
AWS_SECRET_ACCESS_KEY = ""
AWS_SESSION_TOKEN = ""

s3 = boto3.client('s3',
                  aws_access_key_id=AWS_ACCESS_KEY_ID,
                  aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                  aws_session_token=AWS_SESSION_TOKEN)

base_url = "https://s3.amazonaws.com/880656497252."
suffix = ".well-known/mta-sts.txt"

# Keep this updated with all MTA-STS domains
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

failed_domains = []

# Check MTA STS is configured
for domain in domains:
    bucket_name = f"880656497252.{domain}"
    object_key = suffix

    try:
        response = s3.get_object(Bucket=bucket_name, Key=object_key)
        sts_content = response['Body'].read().decode('utf-8')
        has_enforce = any(line.startswith("mode: enforce")
                          for line in sts_content.split('\n'))

        if not has_enforce:
            failed_domains.append(f"{domain} (No 'mode: enforce')")
    except NoCredentialsError:
        failed_domains.append(f"{domain} (AWS credentials not found)")
    except Exception as e:
        failed_domains.append(f"{domain} (Exception: {e}")

# Failed domains
for domain in failed_domains:
    print(domain)
