from services.s3_service import S3Service

# List of MTA-STS domains
domains = [
    "ccrc.gov.uk", "cjit.gov.uk", "cshrcasework.justice.gov.uk", "devl.justice.gov.uk",
    "g.justice.gov.uk", "govfsl.com", "hmiprisons.gov.uk", "hmiprobation.gov.uk",
    "ima-citizensrights.org.uk", "imb.org.uk", "judicialappointments.gov.uk",
    "judicialconduct.gov.uk", "judicialombudsman.gov.uk", "judiciary.uk", "justice.gov.uk",
    "lawcommission.gov.uk", "newsletter.ima-citizensrights.org.uk", "obr.uk", "ospt.gov.uk",
    "ppo.gov.uk", "publicguardian.gov.uk", "sentencingcouncil.gov.uk", "sentencingcouncil.org.uk",
    "ukgovwales.gov.uk", "victimscommissioner.org.uk", "yjb.gov.uk", "yjbservicespp.yjb.gov.uk",
    "youthjusticepp.yjb.gov.uk"
]

# Suffix for MTA-STS files
SUFFIX = ".well-known/mta-sts.txt"

def main():
    s3_client = S3Service("880656497252", "ministryofjustice")
    return check_mta_sts_domains(s3_client)

def check_mta_sts_domains(s3_client):
    failed_domains = []

    for domain in domains:
        if not is_well_known_mta_sts_enforce(s3_client, domain):
            print(f"{domain} (No 'mode: enforce')")
            failed_domains.append(domain)

    return failed_domains

def is_well_known_mta_sts_enforce(s3_client, domain):
    try:
        response = s3_client.get_object(Bucket=f"880656497252.{domain}", Key=SUFFIX)
        sts_content = response['Body'].read().decode('utf-8')
        return any(line.startswith("mode: enforce") for line in sts_content.split('\n'))
    except s3_client.client.exceptions.NoSuchKey:
        return False

if __name__ == "__main__":
    failed_domains = main()
    if failed_domains:
        print(f"Domains failing MTA-STS enforcement:\n{', '.join(failed_domains)}")
    else:
        print("All domains enforce MTA-STS.")
        