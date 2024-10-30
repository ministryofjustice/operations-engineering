import requests
import datetime


class GandiService:
    def __init__(self, token, url_extension) -> None:
        self.headers = {'Authorization': f'Bearer {token}'}
        self.params = {'per_page': 1000}
        self.url = "https://api.gandi.net/" + url_extension

    def get_current_account_balance_from_org(self, org_id):
        try:
            response = requests.get(
                url=self.url + org_id, headers=self.headers, timeout=60)
            response.raise_for_status()
            return float(response.json()['prepaid']['amount'])
        except requests.exceptions.HTTPError as authentication_error:
            raise requests.exceptions.HTTPError(
                f"You may need to export your Gandi API key:\n {authentication_error}") from authentication_error
        except TypeError as api_key_error:
            raise TypeError(
                f"Gandi API key does not exist or is in the wrong format:\n {api_key_error}") from api_key_error

    def _get_email_address_of_domain_owners(self, domain_name, email_list):
        domain_name_to_check = self._remove_suffix_if_present(domain_name)
        if email_list[domain_name_to_check]['external_cname']:
            return email_list[domain_name_to_check]['external_cname']
        email_addresses_of_domain_owners = [
            email_list[domain_name_to_check]['recipient']]
        if email_list[domain_name_to_check]['recipientcc']:
            email_addresses_of_domain_owners.extend(
                iter(email_list[domain_name_to_check]['recipientcc'])
            )
        return email_addresses_of_domain_owners

    def _remove_suffix_if_present(self, domain_name):
        base, sep, suffix = domain_name.rpartition('.')
        return base if sep == '.' and suffix.isdigit() else domain_name

    def _check_certificate_state(self, domain_item, email_list, certificate_state) -> bool:
        return domain_item['cn'] in email_list and domain_item['status'] == certificate_state

    def _is_certificate_owned_by_operations_engineering(self, domain_item, email_list):
        return email_list[domain_item['cn']]['owner'] == 'OE'

    def _get_days_between_now_and_expiry_date(self, expiry_date):
        return (expiry_date - (datetime.datetime.now().date())).days

    def _format_expiry_date(self, date_string: str) -> datetime.date:
        return datetime.datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%SZ').date()

    def get_certificate_list(self):
        try:
            response = requests.get(
                url=self.url, params=self.params, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as authentication_error:
            raise requests.exceptions.HTTPError(
                f"You may need to export your Gandi API key:\n {authentication_error}") from authentication_error
        except TypeError as api_key_error:
            raise TypeError(
                f"Gandi API key does not exist or is in the wrong format:\n {api_key_error}") from api_key_error

    def get_certificates_in_valid_state(self, certificate_list, email_list):
        valid_state_certificates = {}
        for domain_item in certificate_list:
            if self._check_certificate_state(domain_item, email_list, 'valid') and \
                    self._is_certificate_owned_by_operations_engineering(domain_item, email_list):
                expiry_date = self._format_expiry_date(
                    domain_item['dates']['ends_at'])
                base_cn = domain_item['cn']
                suffix = 0
                while base_cn in valid_state_certificates:
                    suffix += 1
                    base_cn = f"{domain_item['cn']}.{suffix}"
                valid_state_certificates[base_cn] = {
                    "expiry_date": expiry_date
                }
        return valid_state_certificates

    def get_expired_certificates_from_valid_certificate_list(self, valid_state_certificate_list: dict, email_list):
        expired_certificates = {}
        for domain_item in valid_state_certificate_list:
            days_between_now_and_expiry_date = self._get_days_between_now_and_expiry_date(
                valid_state_certificate_list[domain_item]['expiry_date'])
            if days_between_now_and_expiry_date in self.config['cert_expiry_thresholds']:
                email_addresses_of_domain_owners = \
                    self._get_email_address_of_domain_owners(
                        domain_item, email_list)
                expired_certificates[domain_item] = {
                    "expiry_date": valid_state_certificate_list[domain_item]['expiry_date'],
                    "emails": email_addresses_of_domain_owners
                }
        return expired_certificates
