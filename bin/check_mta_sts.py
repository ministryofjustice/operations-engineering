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
    failed_domains = check_mta_sts_domains(s3_client)

    if failed_domains:
        print(f"Domains failing MTA-STS enforcement:\n{', '.join(failed_domains)}")
    else:
        print("All domains enforce MTA-STS.")


def check_mta_sts_domains(s3_client):
    failed_domains = []

    for domain in domains:
        if not s3_client.is_well_known_mta_sts_enforce(domain):
            print(f"{domain} (No 'mode: enforce')")
            failed_domains.append(domain)

    return failed_domains


if __name__ == "__main__":
    main()
