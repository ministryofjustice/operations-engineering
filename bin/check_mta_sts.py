from services.s3_service import S3Service

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


def main():
    s3_client = S3Service("880656497252", "ministryofjustice")
    failed_domains = []
    for domain in domains:
        if not s3_client.is_well_known_mta_sts_enforced(domain):
            print(f"{domain} (No 'mode: enforce')")
            failed_domains.append(domain)

    # Send message to slack?


if __name__ == "__main__":
    main()
