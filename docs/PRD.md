# AWS Object and Relationship Ontology Development - Product Requirements Document

**Document Version:** 2.4
**Date:** November 2026

> **Requirement identifiers.** Every testable requirement in this document carries a stable
> `REQ-NNN` identifier, referenced from tests and changelog entries. IDs are never renumbered;
> retired requirements are marked **RETIRED** in place.

## 1. Introduction

This document outlines the requirements for an ontology of Amazon Web Services (AWS) objects and
their interrelationships. The goal is a machine-readable model that ensures consistent data
representation, facilitates advanced querying, and enables comprehensive analysis of AWS
configurations.

## 2. Objective

Define a comprehensive and semantically rich ontology of AWS resources and their operational,
structural, and logical connections, serving as a foundational knowledge base for understanding
complex AWS environments.

## 3. Scope

The ontology primarily covers core and widely used AWS services:

- **Compute:** EC2 (Instances, AMIs, Security Groups, Load Balancers, Auto Scaling Groups), Lambda
- **Containers:** ECS, EKS, Fargate, ECR
- **Storage:** S3 (Buckets, Objects), EBS (Volumes, Snapshots), EFS, RDS (Instances, Databases)
- **Networking:** VPC (Subnets, Route Tables, Internet Gateways, NAT Gateways), Security Groups,
  Network ACLs, CloudFront; Transit Gateway (attachments, route tables); Direct Connect (gateways,
  connections, virtual interfaces)
- **DNS:** Amazon Route 53 (hosted zones, record sets, health checks)
- **Identity & Access Management (IAM):** Users, Roles, Policies, Groups
- **Databases:** DynamoDB, Aurora (as part of RDS), DocumentDB, Redshift; ElastiCache (Redis/
  Memcached clusters, replication groups)
- **Integration:** API Gateway, Step Functions, EventBridge, SNS, SQS
- **Security:** KMS, Secrets Manager; AWS WAF (web ACLs, rule groups, IP sets)
- **Monitoring & Logging:** CloudWatch, CloudTrail; Systems Manager (parameters, documents, patch
  baselines); AWS Config (rules, configuration recorder, conformance packs)
- **Deployment & CI/CD:** AWS CloudFormation (stacks, StackSets, change sets); AWS CodePipeline
  (pipelines, stages)
- **AI/Generative AI:** Amazon Bedrock (foundation models, agents, knowledge bases, guardrails);
  Amazon SageMaker (notebooks, training jobs, models, endpoints)
- **Workforce Identity:** IAM Identity Center (instances, permission sets, account assignments)
- **Consumer Identity:** Amazon Cognito (user pools, user pool clients, identity pools); identity
  providers (SAML, OIDC, social) configured within a user pool; IAM SAML/OIDC providers federated
  directly into an identity pool
- **Governance:** AWS Organizations (Organization, Organizational Units), Control Tower
  (Landing Zones)
- **Detective Security:** GuardDuty (detectors, findings), Security Hub (hub, standards
  subscriptions)
- **Analytics:** AWS Glue (databases, tables, crawlers, jobs); Amazon Athena (workgroups, data
  catalogs, query executions); Amazon Kinesis (streams, Firehose, analytics applications); Amazon
  EMR (clusters, steps, notebooks); Amazon OpenSearch Service (domains, indexes)

## 4. Key Entities (Classes)

| ID | Requirement |
|----|-------------|
| REQ-001 | Infrastructure classes MUST exist: `AWSAccount`, `AWSRegion`, `AvailabilityZone` |
| REQ-002 | Compute classes MUST exist: `EC2Instance`, `EC2AMI`, `EC2SecurityGroup`, `EC2LoadBalancer`, `LambdaFunction` |
| REQ-003 | Storage classes MUST exist: `S3Bucket`, `S3Object`, `EBSVolume`, `EBSSnapshot`, `RDSInstance`, `RDSDatabase` |
| REQ-004 | Identity classes MUST exist: `IAMUser`, `IAMRole`, `IAMPolicy`, `IAMGroup` |
| REQ-005 | Networking classes MUST exist: `VPC`, `Subnet`, `RouteTable`, `InternetGateway`, `NATGateway` |
| REQ-006 | Monitoring classes MUST exist: `CloudWatchMetric`, `CloudWatchAlarm`, `CloudTrailLog` |
| REQ-007 | Database classes MUST cover DynamoDB (`DynamoDBTable`) and Aurora (as part of the RDS class family) |
| REQ-022 | AI/GenAI classes MUST exist: `FoundationModel`, `BedrockAgent`, `BedrockKnowledgeBase`, `BedrockGuardrail`, `ModelInvocation` |
| REQ-023 | Identity Center classes MUST exist: `IdentityCenterInstance`, `PermissionSet`, `AccountAssignment` |
| REQ-028 | Governance classes MUST exist: `Organization`, `OrganizationalUnit`, `ControlTowerLandingZone` |
| REQ-029 | Cognito classes MUST exist: `CognitoUserPool`, `CognitoUserPoolClient`, `CognitoIdentityPool` |
| REQ-030 | Detective security classes MUST exist: `GuardDutyDetector`, `GuardDutyFinding`, `SecurityHubHub`, `SecurityHubStandardsSubscription` |
| REQ-031 | SageMaker classes MUST exist: `SageMakerNotebookInstance`, `SageMakerModel`, `SageMakerEndpoint`, `SageMakerTrainingJob` |
| REQ-033 | Route 53 classes MUST exist: `Route53HostedZone`, `Route53RecordSet`, `Route53HealthCheck` |
| REQ-034 | Transit Gateway classes MUST exist: `TransitGateway`, `TransitGatewayAttachment`, `TransitGatewayRouteTable` |
| REQ-035 | ElastiCache classes MUST exist: `ElastiCacheCluster`, `ElastiCacheReplicationGroup` |
| REQ-036 | Systems Manager classes MUST exist: `SSMParameter`, `SSMDocument`, `SSMPatchBaseline` |
| REQ-037 | Analytics classes MUST exist: `GlueDatabase`, `GlueTable`, `GlueCrawler`, `GlueJob`, `AthenaWorkGroup`, `AthenaDataCatalog`, `AthenaQueryExecution`, `KinesisStream`, `KinesisFirehoseDeliveryStream`, `KinesisAnalyticsApplication`, `EMRCluster`, `EMRStep`, `EMRNotebook`, `OpenSearchDomain`, `OpenSearchIndex` |
| REQ-038 | Deployment/security/monitoring/networking classes MUST exist: `WAFWebACL`, `WAFRuleGroup`, `WAFIPSet`, `ConfigRule`, `ConfigurationRecorder`, `ConfigConformancePack`, `CloudFormationStack`, `CloudFormationStackSet`, `CloudFormationChangeSet`, `CodePipelinePipeline`, `CodePipelineStage`, `DirectConnectGateway`, `DirectConnectConnection`, `DirectConnectVirtualInterface` |
| REQ-039 | Cognito federation classes MUST exist: `CognitoIdentityProvider`, `IAMSAMLProvider`, `IAMOIDCProvider` |
| REQ-043 | A `Tag` class MUST model AWS resource tags as key-value metadata (`tagKey`, `tagValue`), disjoint with `AWSResource` because tags have no ARN of their own |

Additional classes may be added as necessary to represent the AWS ecosystem accurately; the
implemented ontology may exceed this list.

## 5. Relationships (Properties)

| ID | Requirement |
|----|-------------|
| REQ-008 | Structural/compositional properties MUST exist: `hasRegion`, `hasAvailabilityZone`, `contains`, `attachedTo`, `belongsToVPC` |
| REQ-009 | `canAssumeRole` MUST relate IAM principals (users/roles) to IAM roles they may assume |
| REQ-010 | `hasPolicy` MUST relate IAM entities (users/roles/groups) to attached policies (the equivalent `hasPolicyAttachment` satisfies this via an `owl:equivalentProperty` axiom) |
| REQ-011 | `appliesTo` MUST relate security groups to the resources they protect |
| REQ-012 | Operational/functional properties MUST exist: `uses`, `manages`, `monitors`, `logsActivityOf`, `routesTrafficThrough` |
| REQ-013 | Dependency properties MUST exist: `dependsOn` (general), `isSourceFor` (e.g., snapshot → volume) |
| REQ-014 | Inverse properties MUST be defined where semantically meaningful |
| REQ-024 | Specific relationships that are semantically special cases of a generic cross-cutting property (REQ-016's exemption list) MUST be declared `rdfs:subPropertyOf` that generic property, so transitive/general-purpose queries over the generic property also match the specific ones |
| REQ-042 | Security-analysis relationships MUST exist: `hasExecutionRole` relating a resource to the IAM role the resource itself uses to call AWS services (sub-property of `uses`; e.g. a Lambda function's execution role, a Step Functions state machine's role, or an ECS task definition's task role), not a role an AWS service uses only to operate the resource on its behalf, such as the ECS task execution role; `hasTaskExecutionRole` relating an ECS task definition to that task execution role (sub-property of `uses`), so it stays distinguishable from the task's own role; `hasInstanceProfile` relating an EC2 instance to its IAM instance profile (sub-property of `attachedTo`); `hasTag` relating a resource to its tags (REQ-043); `accessLevel` on API actions using AWS's five access levels (List, Read, Write, Permissions management, Tagging); and `isPubliclyAccessible` on resources |
| REQ-045 | Derived access relationships MUST exist for recording the results of IAM policy evaluation, which are computed facts rather than AWS attributes: `hasEffectiveAccess` from a principal to a resource, with one sub-property per AWS access level (`canList`, `canRead`, `canWrite`, `canManagePermissions`, `canTag`), and a functional boolean `isAdministrator` on IAM users and roles. Data MUST assert `hasEffectiveAccess` alongside each specific access level, so consumers that don't apply RDFS reasoning still find the access |

## 6. Output Format

| ID | Requirement |
|----|-------------|
| REQ-015 | The ontology MUST adhere to OWL 2 DL, and the ontology together with its example instances MUST be consistent with no unsatisfiable classes, as verified by an OWL 2 DL reasoner (HermiT) in CI |
| REQ-016 | Properties MUST specify `rdfs:domain` and `rdfs:range`, EXCEPT deliberately generic properties (`contains`, `uses`, `dependsOn`, and similar cross-cutting relations) where broad applicability is intended |
| REQ-017 | Every class and property MUST have an `rdfs:label` and `rdfs:comment` |
| REQ-018 | The ontology MUST ship with at least 50 example instances spanning all major service categories |
| REQ-019 | The ontology MUST be published in two synchronized serializations: Turtle, the editing source, and RDF/XML generated from it deterministically, so the committed RDF/XML is byte-identical to the generator's output and changes only where the ontology does. Both MUST be verified semantically identical |
| REQ-025 | The ontology MUST ship SHACL shapes (`ontology/aws.shapes.ttl`) providing closed-world validation of instance data where OWL's open-world semantics cannot flag a specific individual as non-conforming |
| REQ-044 | SHACL shapes MUST enforce the AWS limits behind REQ-042 and REQ-043: at most one execution role per Lambda function (warning when none), at most one instance profile per EC2 instance, at most one role per instance profile, at most 50 user-applied tags per resource (system tags, whose keys start with `aws:`, don't count), tag keys of 1-128 and values of 0-256 characters, access levels from the five-level set, and a single boolean `isPubliclyAccessible` |
| REQ-026 | The ontology MUST align with PROV-O (`AWSResource rdfs:subClassOf prov:Entity`, model-invocation-style events as `prov:Activity`) to support provenance-chain queries, without importing PROV-O's full axiomatization (avoids a network-fetch dependency at load time) |
| REQ-027 | The ontology MUST provide a SKOS concept scheme grouping the top-level resource categories, as a browsable taxonomy orthogonal to the strict OWL disjoint-class partitioning |
| REQ-040 | The ontology MUST declare its own provenance on the `owl:Ontology` header (`dcterms:source`, `dcterms:creator`, `dcterms:created`/`modified`) plus a machine-readable `:provenanceMethod` and `:verificationMethod`, distinguishing content authored from domain knowledge and independently verified (this ontology) from content extracted from a document corpus with per-claim citations |
| REQ-041 | The ontology MUST use the persistent namespace `https://w3id.org/arango-solutions/aws-ontology#`, declare an `owl:versionIRI` of the form `https://w3id.org/arango-solutions/aws-ontology/<version>` for each release, and publish example instances as a separate ontology that imports the main ontology by IRI |

## 7. Data Sources

AWS Service Documentation, AWS Whitepapers, and AWS API Reference documentation
(publicly available information only).

## 8. Quality Criteria

Consistency (no contradictions), completeness (coverage of specified scope), accuracy
(faithful to AWS behavior), expressiveness (effective OWL constructs), usability
(querying/reasoning/integration), modularity (structured for extension).

## 9. Integration and Performance

| ID | Requirement |
|----|-------------|
| REQ-020 | The ontology MUST be transformable into at least one graph database (ArangoDB via ArangoRDF), with a working import tool |
| REQ-021 | Performance budgets: complete ontology loads in <5s in standard tools; common SPARQL/AQL queries respond in <1s; ArangoDB transformation completes in <30s; reasoning stays under 500MB RAM |
| REQ-032 | The project MUST provide automated tooling that periodically checks for new AWS services/features and proposes ontology extensions for human review, supporting the §10 quarterly-review commitment |

### Coverage targets (informational)

- Service coverage: >90% of the services listed in §3
- Relationship coverage: >80% of critical service relationships
- IAM coverage: 100% of core IAM concepts (Users, Roles, Policies, Groups)
- Tool compatibility: minimum 3 major ontology tools (Protégé, Apache Jena, rdflib)

## 10. Maintenance and Versioning Strategy

### Version Control
- **Semantic Versioning:** MAJOR (breaking structure changes) / MINOR (new services,
  non-breaking additions) / PATCH (bug fixes, documentation, examples)
- `owl:versionInfo` MUST match the latest CHANGELOG release

### Update Schedule
- **Quarterly Reviews:** assessment of new AWS services and features
- **Annual Major Updates:** comprehensive review and potential restructuring
- **On-Demand Updates:** critical security-related updates as needed

### Backward Compatibility
- Maintain backward compatibility for existing relationships and classes
- 6-month notice period for deprecated concepts (mark with `owl:deprecated`)
- Provide transformation scripts for major version updates

### Change Management
- All modifications documented in CHANGELOG with rationale
- All changes validated against the test suite and example instances
- Major changes reviewed by project stakeholders before implementation

## 11. Security and Privacy Considerations

- **Public information only:** based exclusively on publicly available AWS documentation;
  no proprietary AWS architecture or internal information
- **Sanitized examples:** fictional or anonymized data only; no PII; generic resource names
- **License compliance:** all dependencies and tools comply with project licensing
- **No credentials in code:** database and service credentials come from environment
  variables, never hardcoded defaults

## 12. Constraints and Assumptions

- Based on publicly available information only
- Represents a conceptual model of AWS resources
- Prioritizes common and general relationships over edge cases
- No access to internal AWS system diagrams or proprietary information
