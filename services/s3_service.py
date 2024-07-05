import csv
import json
import os
from datetime import datetime
from dateutil.relativedelta import relativedelta
import boto3


from config.constants import NO_ACTIVITY


class S3Service:
    def __init__(self, bucket_name: str, organisation_name: str) -> None:
        self.client = boto3.client("s3")
        self.bucket_name = bucket_name
        self.emailed_users_file_name = f"{organisation_name.lower()}_first_email_list.json"
        self.emailed_users_file_path = self.emailed_users_file_name
        self.dormant_users_file_name = "dormant.csv"
        self.dormant_users_file_path = "dormant.csv"
        self.org_people_file_name = f"export-{organisation_name.lower()}.json"
        self.org_people_file_path = self.org_people_file_name

    def delete_emailed_users_file(self):
        self._delete_file(self.emailed_users_file_name)

    def save_emailed_users_file(self, users: list):
        with open(self.emailed_users_file_path, "w", encoding="utf8") as the_file:
            the_file.write(json.dumps(users))
        self._upload_file(
            self.emailed_users_file_name, self.emailed_users_file_path)

    def save_r53_backup_file(self):
        session = boto3.Session(profile_name='cp_r53_backup_profile')
        client = session.client('s3')
        client.upload_file("hosted_zones.json", self.bucket_name, f"{datetime.now().strftime('%Y-%m-%d')}-hosted_zones.json")

    def get_users_have_emailed(self):
        self._download_file(
            self.emailed_users_file_name, self.emailed_users_file_path)
        with open(self.emailed_users_file_path, "r", encoding="utf8") as the_file:
            return json.load(the_file)

    def get_users_from_dormant_user_file(self) -> list:
        username = 2
        is_outside_collaborator = 6
        users = []
        self._download_file(
            self.dormant_users_file_name, self.dormant_users_file_path)
        with open(self.dormant_users_file_path, "r", encoding="utf8") as the_file:
            dormant_user_file = csv.reader(the_file)
            # Do not remove next() it skips the top row of the .csv file
            next(the_file)
            for user in dormant_user_file:
                users.append(
                    {
                        "username": user[username].lower(),
                        "is_outside_collaborator": user[is_outside_collaborator],
                    }
                )
        return users

    def get_active_users_from_org_people_file(self) -> list:
        three_months_ago_date = datetime.now() - relativedelta(months=3)

        active_users = []
        for user in self._get_users_from_org_people_file():
            # Some users have "No activity" skip over these users
            if user["last_active"].lower() == NO_ACTIVITY:
                continue
            last_active_date = datetime.strptime(
                user['last_active'][0:10], '%Y-%m-%d')
            if last_active_date > three_months_ago_date:
                active_users.append(user["username"])

        return active_users

    def _get_users_from_org_people_file(self) -> list:
        users = []
        self._download_file(
            self.org_people_file_name, self.org_people_file_path)
        with open(self.org_people_file_path, "r", encoding="utf8") as the_file:
            org_user_file = json.load(the_file)
            for user in org_user_file:
                users.append(
                    {
                        "username": user["login"].lower(),
                        "last_active": user["last_active"]
                    }
                )
        return users

    def _download_file(self, object_name: str, file_path: str):
        self.client.download_file(
            self.bucket_name, object_name, file_path)
        if not os.path.isfile(file_path):
            raise ValueError(
                f"The {file_path} file did not download or is not in the expected location")

    def _upload_file(self, object_name: str, file_path: str):
        self.client.upload_file(file_path, self.bucket_name, object_name)

    def _delete_file(self, object_name: str):
        self.client.delete_object(Bucket=self.bucket_name, Key=object_name)
        
    def is_well_known_mta_sts_enforce(self, domain: str) -> bool:
        suffix = ".well-known/mta-sts.txt"
        bucket_name = f"880656497252.{domain}"
        response = self.client.get_object(Bucket=bucket_name, Key=suffix)
        sts_content = response['Body'].read().decode('uft-8')
        return any(line.startswitch("mode: enforce") for line in sts_content.split('\n'))
