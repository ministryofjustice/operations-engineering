import datetime


class TestData:
    test_undeliverable_message = "permanent_failure"
    test_domain_name_root = "test.domain.gov.uk"
    test_recipient_email_root = "test.user@mail.com"
    test_recipientcc_email_root = "test.user.cc@mail.com"
    test_cname_email_root = "test.cname.user@mail.com"

    @classmethod
    def generate_single_email_list(cls, owner: str = 'OE', recipcc: int = 0, cname: int = 0):
        recipientcc = [
            f"{cls.test_recipientcc_email_root}{i}" for i in range(recipcc)]
        external_cname = [
            f"{cls.test_cname_email_root}{i}" for i in range(cname)]
        return {
            cls.test_domain_name_root: {
                "recipient": cls.test_recipient_email_root,
                "recipientcc": recipientcc,
                "owner": owner,
                "external_cname": external_cname,
            }
        }

    @classmethod
    def generate_multiple_email_list(cls, count: int = 1, owner: str = 'OE', recipcc: int = 0, cname: int = 0):
        recipientcc = [
            f"{cls.test_recipientcc_email_root}{i}" for i in range(recipcc)]
        external_cname = [
            f"{cls.test_cname_email_root}{i}" for i in range(cname)]
        return {
            f"{cls.test_domain_name_root}{i}": {
                "recipient": cls.test_recipient_email_root,
                "recipientcc": recipientcc,
                "owner": owner,
                "external_cname": external_cname,
            }
            for i in range(count)
        }

    @classmethod
    def generate_multiple_email_list_same_domain_name(cls, count: int = 1, owner: str = 'OE', recipcc: int = 0,
                                                      cname: int = 0):
        recipientcc = [
            f"{cls.test_recipientcc_email_root}{i}" for i in range(recipcc)]
        external_cname = [
            f"{cls.test_cname_email_root}{i}" for i in range(cname)]
        return {
            f"{cls.test_domain_name_root}": {
                "recipient": cls.test_recipient_email_root,
                "recipientcc": recipientcc,
                "owner": owner,
                "external_cname": external_cname,
            }
            for i in range(count)
        }

    @classmethod
    def generate_single_filtered_certificate_list_with_expiry_date(cls, days: int):
        expiry_date = (datetime.datetime.now() +
                       datetime.timedelta(days=days)).date()
        return {cls.test_domain_name_root: {"expiry_date": expiry_date}}

    @classmethod
    def generate_multiple_filtered_certificate_list_with_expiry_date(cls, days: int, count: int = 1):
        expiry_date = (datetime.datetime.now() +
                       datetime.timedelta(days=days)).date()
        return {
            f"{cls.test_domain_name_root}{i}": {"expiry_date": expiry_date}
            for i in range(count)
        }

    @classmethod
    def generate_single_gandi_certificate_state(cls, state: str):
        return [{"cn": cls.test_domain_name_root, "status": state,
                 "dates": {"ends_at": "2023-01-01T06:00:00Z"}, }]

    @classmethod
    def generate_multiple_gandi_certificate_states(cls, state: str, count: int = 1):
        return [
            {"cn": f"{cls.test_domain_name_root}{i}", "status": state,
             "dates": {"ends_at": "2023-01-01T06:00:00Z"}, }
            for i in range(count)]

    @classmethod
    def generate_multiple_gandi_certificate_states_same_domain_name(cls, state: str, count: int = 1):
        return [
            {
                "cn": f"{cls.test_domain_name_root}",
                "status": state,
                "dates": {"ends_at": "2023-01-01T06:00:00Z"},
            }
            for _ in range(count)
        ]

    @classmethod
    def generate_multiple_valid_certificate_list(cls, count: int = 1):
        return {
            f"{cls.test_domain_name_root}{i}":
                {"expiry_date": "2023-01-01", "emails":
                    [f"{cls.test_recipient_email_root}{i}"]}
            for i in range(count)
        }

    @classmethod
    def generate_single_valid_certificate_multiple_emails(cls, count: int = 1):
        emails = [f"{cls.test_recipient_email_root}{i}" for i in range(count)]
        return {
            cls.test_domain_name_root:
                {"expiry_date": "2023-01-01", "emails": emails}
        }

    @classmethod
    def generate_multiple_email_parameter_list(cls, count: int = 1):
        return [
            {
                'email_addresses': [f"{cls.test_recipient_email_root}{i}"],
                'domain_name': f"{cls.test_domain_name_root}{i}",
                'csr_email': 'test@example.com',
                'end_date': '2023-01-01',
            }
            for i in range(count)
        ]

    @classmethod
    def generate_main_report_single_domain_single_email(cls):
        new_line = '\n'
        return (
            f"Domain Name: {cls.test_domain_name_root}\n"
            f"Sent to:\n{''.join([f'{cls.test_recipient_email_root}{new_line}'])}"
            f"\nExpiry Date: 2023-01-01 \n\n")

    @classmethod
    def generate_main_report_multiple_domain_multiple_email(cls, domain_count: int = 1, email_count: int = 1):
        new_line = '\n'
        return "".join(
            f"Domain Name: {cls.test_domain_name_root}{i}\n"
            f"Sent to:\n{''.join([f'{cls.test_recipient_email_root}{i}{new_line}' for i in range(email_count)])}"
            "\nExpiry Date: 2023-01-01 \n\n"
            for i in range(domain_count)
        )

    @classmethod
    def generate_undeliverable_report_single_email(cls):
        return "".join(
            f"Email Address: {cls.test_recipient_email_root}\n"
            "Sent at: 2023=01=01\n"
            f"Status: {cls.test_undeliverable_message} \n\n"
        )

    @classmethod
    def generate_undeliverable_report_multiple_email(cls, email_count):
        return "".join(
            f"Email Address: {cls.test_recipient_email_root}{i}\n"
            "Sent at: 2023-01-01\n"
            f"Status: {cls.test_undeliverable_message} \n\n"
            for i in range(email_count)
        )
