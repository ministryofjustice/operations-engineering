name: Operations Engineering justice.gov.uk Subdomain Request
title: "[DNS] <title>"
description: Template request for adding a new justice.gov.uk subdomain.
labels: dns-request, add-subdomain-request
body:

- type: input
  id: requestor_name
  attributes:
    label: Requestor Name
    description: Enter your full name
  validations:
    required: true
- type: input
  id: moj-service-owner
  attributes:
    label: MoJ Service Owner
    description: Enter the name of the MoJ Service Owner
  validations:
    required: true
- type: input
  id: service-area-name
  attributes:
    label: Service Area Name
    description: Enter the name of the Service Area
  validations:
    required: true
- type: dropdown
  id: business-area-name
  attributes:
    label: Business Area Name
    description: Enter the name of the Business Area
    options:
      - HMPPS
      - HMCTS
      - CJSCP
      - Other
  validations:
    required: true
- type: input
  id: new-domain-name
  attributes:
    label: New Domain Name
    description: Enter the new domain name you wish to add
  validations:
    required: true
- type: input
  id: new-service-description
  attributes:
    label: New Service Description
    description: Enter a brief description of the service that will be using this domain
  validations:
    required: true
- type: input
  id: new-domain-purpose
  attributes:
    label: Purpose of New Domain
    description: Enter the primary purpose of this new domain
  validations:
    required: true
- type: dropdown
  id: type-of-record
  attributes:
    label: DNS Record Type
    description: Enter the type of DNS record required
    options:
      - NS
      - A
      - MX
      - CNAME
      - OTHER
  validations:
    required: true
- type: textarea
  id: ns_details
  attributes:
    label: NS Details (Optional)
    description: If NS record is selected, please provide a brief justification for its delegation
  validations:
    required: false
