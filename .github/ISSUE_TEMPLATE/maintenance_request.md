---
name: Operations Engineering Maintenance Request
about: Create a ticket for the Maintenance App
title: ''
labels: Maintenance Pages
assignees: ''

---

## Maintenance Pages Request

### **Pretasks**

Collect the following information in order to action this request, please attach this information to this ticket

- [ ] Application name
- [ ] Contact point
- [ ] Date and time maintenance begins
- [ ] Current DNS name/s
- [ ] Current DNS location
- [ ] \(Optional) Contact point for DNS if not inside DSD

### **Prior to switch**

Prior to turning maintenance mode, a number of things must be done

1. [ ] DNS replicated as a zone in Cloud Platform Account - [Example](https://github.com/ministryofjustice/cloud-platform-environments/blob/main/namespaces/live.cloud-platform.service.justice.gov.uk/maintenance-pages/resources/route53.tf#L18-L42)
2. [ ] Name Servers for zone for above task retrieved from Cloud Platform team
3. [ ] Certificate PR created (**not merged**) - [Example](https://github.com/ministryofjustice/cloud-platform-environments/commit/3eee2737e6c50bbf88b9065c6760d8c378bb0ccf#diff-a0b3e873008b346e0ae4c81c56b6c1a218ffd422e421b7b6036a9fbe7d946d3e)
4. [ ] Remove A record PR created (**not merged**) - [Example](https://github.com/ministryofjustice/cloud-platform-environments/pull/6137/files)
5. [ ] Maintenance page created (**merged**) - [Example](https://github.com/ministryofjustice/cloud-platform-maintenance-pages/blob/main/views/civil-eligibility-calculator.justice.gov.uk.erb)
6. [ ] Ingress created (**not merged**) - [Example](https://github.com/ministryofjustice/cloud-platform-maintenance-pages/pull/18)

### **The Switch**

These are the steps that need to be followed at switch time

> Note: step 1 and 2 can be done before hand if the team is comfortable with the Cloud Platform Account handling their DNS for a while

1. [ ] Add NS record to current DNS location pointing at the Name Servers retrieved from the Cloud Platform Team
2. [ ] Merge Certificate PR and check cert has been issues with below command

    ```bash
    kubectl describe cert domains-cert -n maintenance-pages
    ```

3. [ ] Merge Remove A record PR
4. [ ] Merge Ingress PR

### **Switching Back**

These are the steps that need to be followed when switching back

1. [ ] Remove NS record from original DNS location

### **Links and Information**

- [Maintenance Pages Repository](https://github.com/ministryofjustice/cloud-platform-maintenance-pages)
- [Cloud Platform Environments Repository](https://github.com/ministryofjustice/cloud-platform-environments)
- Cloud Platform Slack: **\#ask-cloud-platform**
- Maintenance Pages Kubernetes Namespace: **maintenance-pages**
