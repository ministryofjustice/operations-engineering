import json


def create_delete_cname_record(cname):
    """Create a delete cname record
    Args:
        cname (string): The cname record from AWS. Defaults to None.
    Returns:
        cname_record: a delete cname record
    """
    cname_record = {
        "Action": "DELETE",
        "ResourceRecordSet": {
            "Name": cname["Name"],
            "Type": "CNAME",
            "TTL": cname["TTL"],
            "ResourceRecords": [{"Value": cname["ResourceRecords"][0]["Value"]}],
        },
    }

    return cname_record


def create_delete_cname_file(cnames, filename):
    """Create a file of cname records that shall be deleted from AWS

    Args:
        cnames (list): The cnames records downloaded from AWS Route 53
        filename (string): The name of the file to create
    """
    changes = []

    for cname in cnames:
        if "comodoca" in cname["ResourceRecords"][0]["Value"]:
            record = create_delete_cname_record(cname)
            changes.append(record)
        elif "sectigo" in cname["ResourceRecords"][0]["Value"]:
            record = create_delete_cname_record(cname)
            changes.append(record)
        else:
            pass

    if len(changes) != 0:
        json_output = {"Changes": changes}
        output_file = open(filename, "w")
        output_file.write(json.dumps(json_output, indent=2))
        output_file.close()


def run():
    """A function for the main functionality of the script"""

    # Get service justice hostzone cname data
    service_justice_cnames_file = open("service_justice_cnames.json")
    service_justice_cnames_data = json.load(service_justice_cnames_file)
    service_justice_cnames_file.close()

    # Get justice hostzone cname data
    justice_cnames_file = open("justice_cnames.json")
    justice_cnames_data = json.load(justice_cnames_file)
    justice_cnames_file.close()

    create_delete_cname_file(
        service_justice_cnames_data, "delete_service_justice_cnames.json"
    )
    create_delete_cname_file(justice_cnames_data, "delete_justice_cnames.json")


print("Start")
run()
print("Finished")
