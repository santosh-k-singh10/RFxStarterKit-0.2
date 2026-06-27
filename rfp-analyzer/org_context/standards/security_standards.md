# Acme Corp Security Standards

## Version: 3.0
## Last Updated: 2026-04-01
## Classification: Internal Use Only

---

## Executive Summary

This document outlines the mandatory security standards for all systems, applications, and data at Acme Corp. Compliance with these standards is required for all projects and is subject to regular security audits.

## Security Framework

### Compliance Requirements
- **SOC 2 Type II**: Security, availability, confidentiality
- **ISO 27001**: Information security management
- **GDPR**: Data protection and privacy
- **HIPAA**: Healthcare data protection (where applicable)
- **PCI DSS**: Payment card data security (where applicable)

### Security Principles
1. **Defense in Depth**: Multiple layers of security controls
2. **Least Privilege**: Minimum necessary access rights
3. **Zero Trust**: Never trust, always verify
4. **Security by Design**: Build security into systems from the start
5. **Continuous Monitoring**: Real-time threat detection and response

## Authentication & Authorization

### Authentication Standards

#### Multi-Factor Authentication (MFA)
- **Required for**: All production systems, admin access, VPN
- **Methods**: TOTP (preferred), SMS (backup), Hardware tokens
- **Enforcement**: Mandatory for all users, no exceptions

#### Password Policy
```yaml
Requirements:
  - Minimum length: 12 characters
  - Complexity: Upper, lower, number, special character
  - Expiration: 90 days
  - History: Cannot reuse last 12 passwords
  - Lockout: 5 failed attempts, 30-minute lockout
  - Storage: bcrypt with cost factor 12+
```

#### Single Sign-On (SSO)
- **Provider**: Okta (primary), Azure AD (backup)
- **Protocol**: SAML 2.0 or OAuth 2.0 + OpenID Connect
- **Session timeout**: 8 hours (idle), 24 hours (absolute)
- **Re-authentication**: Required for sensitive operations

### Authorization Standards

#### Role-Based Access Control (RBAC)
```yaml
Roles:
  - Admin: Full system access
  - Developer: Code and deployment access
  - Analyst: Read-only data access
  - Support: Limited operational access
  - Auditor: Read-only audit log access

Permissions:
  - Create, Read, Update, Delete (CRUD)
  - Execute, Deploy, Configure
  - Audit, Monitor, Report
```

#### Access Control Matrix
| Role | Production Data | Production Deploy | User Management | Audit Logs |
|------|----------------|-------------------|-----------------|------------|
| Admin | Full | Yes | Yes | Yes |
| Developer | Read | No | No | No |
| Analyst | Read | No | No | No |
| Support | Limited | No | No | Read |
| Auditor | Read | No | No | Yes |

#### Access Review
- **Frequency**: Quarterly
- **Process**: Manager approval required
- **Automation**: Automated access expiration after 90 days of inactivity
- **Documentation**: All access changes must be logged and justified

## Data Security

### Data Classification

#### Classification Levels
1. **Public**: No restrictions (marketing materials, public docs)
2. **Internal**: Internal use only (policies, procedures)
3. **Confidential**: Restricted access (business plans, contracts)
4. **Highly Confidential**: Strict access control (PII, financial data, trade secrets)

#### Handling Requirements
```yaml
Public:
  Encryption: Not required
  Access: Anyone
  Retention: Indefinite
  
Internal:
  Encryption: In transit (TLS 1.3)
  Access: Employees only
  Retention: Per policy
  
Confidential:
  Encryption: At rest (AES-256) and in transit (TLS 1.3)
  Access: Need-to-know basis
  Retention: 7 years
  Disposal: Secure deletion
  
Highly Confidential:
  Encryption: At rest (AES-256) and in transit (TLS 1.3)
  Access: Explicit approval required
  Retention: 7 years minimum
  Disposal: Certified destruction
  Audit: All access logged
```

### Encryption Standards

#### Data at Rest
- **Algorithm**: AES-256-GCM
- **Key Management**: AWS KMS or Azure Key Vault
- **Key Rotation**: Every 90 days
- **Backup Encryption**: Same as production data

#### Data in Transit
- **Protocol**: TLS 1.3 (minimum TLS 1.2)
- **Cipher Suites**: 
  - TLS_AES_256_GCM_SHA384
  - TLS_CHACHA20_POLY1305_SHA256
- **Certificate**: Valid, trusted CA, 2048-bit RSA minimum
- **HSTS**: Enabled with max-age=31536000

#### Key Management
```yaml
Key Lifecycle:
  - Generation: Cryptographically secure random
  - Storage: Hardware Security Module (HSM) or KMS
  - Distribution: Secure channels only
  - Rotation: Every 90 days
  - Revocation: Immediate upon compromise
  - Destruction: Secure deletion with verification
```

### Personal Identifiable Information (PII)

#### PII Definition
- Name, email, phone number
- Social Security Number, passport number
- Financial information (credit cards, bank accounts)
- Health information
- Biometric data
- IP addresses, device IDs

#### PII Protection Requirements
1. **Minimize Collection**: Only collect necessary PII
2. **Encryption**: Always encrypt PII at rest and in transit
3. **Access Control**: Strict need-to-know access
4. **Audit Logging**: Log all PII access
5. **Data Masking**: Mask PII in non-production environments
6. **Retention**: Delete PII when no longer needed
7. **Consent**: Obtain explicit consent for collection and use

#### PII Handling Example
```python
# Good: Masked PII in logs
logger.info(f"User login: {mask_email(user.email)}")
# Output: "User login: j***@example.com"

# Bad: Exposed PII in logs
logger.info(f"User login: {user.email}")
# Output: "User login: john.doe@example.com"
```

## Application Security

### Secure Development Lifecycle (SDL)

#### Phase 1: Requirements
- Security requirements defined
- Threat modeling completed
- Privacy impact assessment

#### Phase 2: Design
- Security architecture review
- Data flow diagrams
- Attack surface analysis

#### Phase 3: Implementation
- Secure coding standards followed
- Code review with security focus
- Static Application Security Testing (SAST)

#### Phase 4: Testing
- Dynamic Application Security Testing (DAST)
- Penetration testing
- Security regression testing

#### Phase 5: Deployment
- Security configuration review
- Vulnerability scanning
- Security monitoring enabled

#### Phase 6: Maintenance
- Security patch management
- Continuous monitoring
- Incident response readiness

### OWASP Top 10 Protection

#### 1. Injection Prevention
```python
# SQL Injection Prevention
# Good: Parameterized query
cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))

# Bad: String concatenation
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
```

#### 2. Broken Authentication Prevention
- Implement MFA
- Use secure session management
- Protect against brute force attacks
- Implement account lockout

#### 3. Sensitive Data Exposure Prevention
- Encrypt sensitive data
- Use HTTPS everywhere
- Disable caching for sensitive pages
- Implement secure headers

#### 4. XML External Entities (XXE) Prevention
```python
# Good: Disable external entities
parser = etree.XMLParser(resolve_entities=False)
tree = etree.parse(xml_file, parser)
```

#### 5. Broken Access Control Prevention
- Implement proper authorization checks
- Deny by default
- Validate permissions on every request
- Log access control failures

#### 6. Security Misconfiguration Prevention
- Remove default accounts
- Disable unnecessary features
- Keep software updated
- Use security headers

#### 7. Cross-Site Scripting (XSS) Prevention
```javascript
// Good: Escape user input
const safeHTML = DOMPurify.sanitize(userInput);

// Bad: Direct HTML insertion
element.innerHTML = userInput;
```

#### 8. Insecure Deserialization Prevention
- Validate serialized data
- Use safe serialization formats (JSON)
- Implement integrity checks
- Restrict deserialization

#### 9. Using Components with Known Vulnerabilities
- Maintain software inventory
- Monitor vulnerability databases
- Automated dependency scanning
- Patch within SLA (Critical: 7 days, High: 30 days)

#### 10. Insufficient Logging & Monitoring
- Log security events
- Monitor for anomalies
- Set up alerts
- Implement incident response

### API Security

#### API Authentication
```yaml
Methods:
  - OAuth 2.0 with JWT tokens
  - API keys (for service-to-service)
  - Mutual TLS (for high-security APIs)

Token Security:
  - Short-lived access tokens (1 hour)
  - Refresh tokens (7 days)
  - Token rotation on use
  - Secure token storage
```

#### API Rate Limiting
```yaml
Limits:
  - Authenticated users: 1000 requests/hour
  - Anonymous users: 100 requests/hour
  - Burst limit: 50 requests/minute
  
Response:
  - Status: 429 Too Many Requests
  - Headers: X-RateLimit-Limit, X-RateLimit-Remaining
  - Retry-After: Time until limit resets
```

#### API Security Headers
```http
Strict-Transport-Security: max-age=31536000; includeSubDomains
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Content-Security-Policy: default-src 'self'
Referrer-Policy: strict-origin-when-cross-origin
```

## Infrastructure Security

### Network Security

#### Network Segmentation
```
┌─────────────────────────────────────────┐
│         DMZ (Public Zone)               │
│  - Load Balancers                       │
│  - Web Application Firewall (WAF)       │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│      Application Zone (Private)         │
│  - Application Servers                  │
│  - API Gateways                         │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│       Data Zone (Restricted)            │
│  - Database Servers                     │
│  - Data Warehouses                      │
└─────────────────────────────────────────┘
```

#### Firewall Rules
- Default deny all traffic
- Explicit allow rules only
- Least privilege access
- Regular rule review and cleanup
- Logging of all denied connections

#### VPN Requirements
- Required for remote access
- Split tunneling disabled
- MFA required
- Session timeout: 8 hours
- Audit logging enabled

### Cloud Security

#### AWS Security Standards
```yaml
IAM:
  - No root account usage
  - MFA for all users
  - Least privilege policies
  - Regular access review
  
S3:
  - Block public access by default
  - Enable versioning
  - Enable encryption (SSE-S3 or SSE-KMS)
  - Enable access logging
  
EC2:
  - Use security groups (not NACLs)
  - Disable public IPs where possible
  - Enable CloudWatch monitoring
  - Automated patching
  
RDS:
  - Enable encryption at rest
  - Enable automated backups
  - Use VPC for network isolation
  - Enable audit logging
```

#### Container Security
```yaml
Docker:
  - Use official base images
  - Scan images for vulnerabilities
  - Run as non-root user
  - Limit container capabilities
  - Use read-only file systems
  
Kubernetes:
  - Enable RBAC
  - Use network policies
  - Enable pod security policies
  - Scan for misconfigurations
  - Regular security updates
```

### Endpoint Security

#### Workstation Requirements
- Full disk encryption (BitLocker/FileVault)
- Antivirus/EDR installed and updated
- Firewall enabled
- Automatic security updates
- Screen lock after 5 minutes idle

#### Mobile Device Management (MDM)
- Company-owned devices only for production access
- MDM enrollment required
- Remote wipe capability
- Encryption required
- App whitelisting

## Incident Response

### Incident Classification

#### Severity Levels
```yaml
Critical (P1):
  - Data breach
  - Ransomware attack
  - Complete system outage
  - Response time: Immediate
  - Escalation: CISO, CEO
  
High (P2):
  - Unauthorized access
  - Malware infection
  - Partial system outage
  - Response time: 1 hour
  - Escalation: Security team, IT management
  
Medium (P3):
  - Failed login attempts
  - Policy violations
  - Minor vulnerabilities
  - Response time: 4 hours
  - Escalation: Security team
  
Low (P4):
  - Security warnings
  - Configuration issues
  - Response time: 24 hours
  - Escalation: IT support
```

### Incident Response Process

#### 1. Detection & Analysis
- Monitor security alerts
- Analyze indicators of compromise
- Determine incident scope and impact
- Document all findings

#### 2. Containment
- Isolate affected systems
- Preserve evidence
- Implement temporary fixes
- Prevent further damage

#### 3. Eradication
- Remove malware/threats
- Close vulnerabilities
- Patch systems
- Verify clean state

#### 4. Recovery
- Restore systems from clean backups
- Verify system integrity
- Monitor for reinfection
- Return to normal operations

#### 5. Post-Incident
- Document lessons learned
- Update security controls
- Conduct root cause analysis
- Improve detection capabilities

### Breach Notification

#### Internal Notification
- Security team: Immediate
- Management: Within 1 hour
- Legal team: Within 2 hours
- Affected users: Within 24 hours

#### External Notification
- Regulatory authorities: Per legal requirements (typically 72 hours)
- Customers: Within 72 hours of confirmation
- Law enforcement: As required
- Public disclosure: As required by law

## Security Monitoring

### Logging Requirements

#### What to Log
```yaml
Authentication Events:
  - Login attempts (success/failure)
  - Logout events
  - Password changes
  - MFA events
  - Session creation/termination
  
Authorization Events:
  - Access granted/denied
  - Permission changes
  - Role assignments
  - Privilege escalation
  
Data Access:
  - PII access
  - Sensitive data queries
  - Data exports
  - Data modifications
  
System Events:
  - Configuration changes
  - Software installations
  - Service starts/stops
  - Error conditions
```

#### Log Format
```json
{
  "timestamp": "2026-04-01T10:00:00Z",
  "event_type": "authentication",
  "severity": "info",
  "user_id": "user123",
  "ip_address": "192.168.1.100",
  "action": "login_success",
  "resource": "/api/v1/users",
  "correlation_id": "abc-123-def-456"
}
```

#### Log Retention
- Security logs: 1 year minimum
- Audit logs: 7 years
- Application logs: 90 days
- Debug logs: 30 days

### Security Monitoring Tools

#### Required Tools
```yaml
SIEM:
  - Tool: Splunk or ELK Stack
  - Purpose: Centralized log analysis
  - Alerts: Real-time security alerts
  
Vulnerability Scanner:
  - Tool: Nessus or Qualys
  - Frequency: Weekly
  - Scope: All systems
  
Intrusion Detection:
  - Tool: Snort or Suricata
  - Deployment: Network and host-based
  - Updates: Daily
  
Endpoint Detection:
  - Tool: CrowdStrike or Carbon Black
  - Coverage: All endpoints
  - Response: Automated containment
```

## Compliance & Audit

### Security Audits

#### Internal Audits
- **Frequency**: Quarterly
- **Scope**: All systems and processes
- **Findings**: Tracked and remediated
- **Report**: To security committee

#### External Audits
- **Frequency**: Annually
- **Auditor**: Independent third party
- **Standards**: SOC 2, ISO 27001
- **Report**: To board of directors

### Compliance Reporting

#### Required Reports
```yaml
Monthly:
  - Security metrics dashboard
  - Vulnerability status
  - Incident summary
  - Compliance status
  
Quarterly:
  - Risk assessment
  - Audit findings
  - Training completion
  - Policy updates
  
Annually:
  - Security program review
  - Penetration test results
  - Disaster recovery test
  - Business continuity plan
```

## Security Training

### Required Training

#### All Employees
- Security awareness: Annually
- Phishing simulation: Quarterly
- Data protection: Annually
- Incident reporting: Annually

#### Developers
- Secure coding: Annually
- OWASP Top 10: Annually
- Security testing: Annually
- Threat modeling: Annually

#### Security Team
- Advanced security training: Quarterly
- Certifications: CISSP, CEH, OSCP
- Conference attendance: Annually
- Threat intelligence: Ongoing

## Exceptions & Waivers

### Exception Process
1. Submit exception request with business justification
2. Risk assessment by security team
3. Compensating controls identified
4. Approval by CISO required
5. Regular review (quarterly)
6. Automatic expiration after 1 year

### Waiver Criteria
- Business critical requirement
- No viable alternative
- Acceptable risk level
- Compensating controls in place
- Time-limited (maximum 1 year)

---

## Enforcement

Violations of these security standards may result in:
1. Access revocation
2. Disciplinary action
3. Termination of employment
4. Legal action

## Contact

For security questions or to report incidents:
- **Security Team**: security@acme.com
- **24/7 Hotline**: +1-555-SECURITY
- **Incident Portal**: https://security.acme.com/incident

## Document Control

- **Owner**: Chief Information Security Officer (CISO)
- **Review Cycle**: Quarterly
- **Next Review**: 2026-07-01
- **Version History**: Maintained in security wiki