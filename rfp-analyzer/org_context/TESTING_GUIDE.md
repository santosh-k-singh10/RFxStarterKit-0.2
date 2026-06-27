 more risks identified

---

### Scenario 8: Remote Context Loading (SharePoint/OneDrive)

**Purpose**: Test loading organizational context from cloud storage

**Prerequisites**:
- SharePoint or OneDrive access
- Appropriate credentials configured

**Steps**:

1. **Upload Config to SharePoint**:
   - Upload `org_config.yaml` to SharePoint document library
   - Note the full URL

2. **Set Environment Variables**:
```bash
export SHAREPOINT_CLIENT_ID="your-client-id"
export SHAREPOINT_CLIENT_SECRET="your-client-secret"
export SHAREPOINT_TENANT_ID="your-tenant-id"
```

3. **Run Analysis**:
```bash
python main.py analyze org_context/examples/past_rfps/sample_healthcare_portal_rfp.txt \
  --org-context "https://company.sharepoint.com/sites/team/Shared Documents/org_config.yaml" \
  --output-dir ./test_results/remote \
  --title "Remote Context Test"
```

**Expected Results**:
- Context loaded from remote location
- Same analysis quality as local context
- Caching for performance

---

## Comparison Matrix

Create a comparison matrix to track differences:

| Aspect | Baseline | Healthcare | Python Stack | Finance | Custom Naming |
|--------|----------|------------|--------------|---------|---------------|
| Req ID Format | REQ-001 | FR-HC-001 | FR-PY-001 | FR-FIN-001 | FUNC_0001 |
| Compliance Focus | Generic | HIPAA | HIPAA | PCI-DSS | SOC2 |
| Tech Stack | Generic | Java/Spring | Python/Django | Java/Spring | Python/Django |
| Priority Detection | Standard | Healthcare | Standard | Financial | Custom |
| Risk Assessment | Generic | Healthcare | Tech-focused | Financial | Custom |

## Automated Testing Script

Create a script to run all scenarios:

```bash
#!/bin/bash
# test_all_scenarios.sh

RFP_FILE="org_context/examples/past_rfps/sample_healthcare_portal_rfp.txt"
OUTPUT_BASE="./test_results"

echo "Running all test scenarios..."

# Scenario 1: Baseline
echo "1. Baseline test..."
python main.py analyze "$RFP_FILE" \
  --output-dir "$OUTPUT_BASE/baseline" \
  --title "Baseline"

# Scenario 2: Healthcare
echo "2. Healthcare context..."
python main.py analyze "$RFP_FILE" \
  --org-context ./org_context/config/org_config.yaml \
  --output-dir "$OUTPUT_BASE/healthcare" \
  --title "Healthcare"

# Scenario 3: Python Stack
echo "3. Python stack..."
python main.py analyze "$RFP_FILE" \
  --org-context ./org_context/config/org_config_python.yaml \
  --output-dir "$OUTPUT_BASE/python_stack" \
  --title "Python Stack"

# Scenario 4: Finance
echo "4. Finance context..."
python main.py analyze "$RFP_FILE" \
  --org-context ./org_context/config/org_config_finance.yaml \
  --output-dir "$OUTPUT_BASE/finance" \
  --title "Finance"

# Scenario 5: Custom Naming
echo "5. Custom naming..."
python main.py analyze "$RFP_FILE" \
  --org-context ./org_context/config/org_config_custom_naming.yaml \
  --output-dir "$OUTPUT_BASE/custom_naming" \
  --title "Custom Naming"

echo "All tests complete! Results in $OUTPUT_BASE/"
```

## Analysis Checklist

Use this checklist to verify each test:

### Requirement Extraction
- [ ] All functional requirements extracted
- [ ] All non-functional requirements extracted
- [ ] All compliance requirements extracted
- [ ] Ambiguities identified
- [ ] Risks assessed

### Organizational Context Application
- [ ] Correct requirement ID format used
- [ ] Priority keywords correctly mapped
- [ ] Compliance frameworks recognized
- [ ] Tech stack preferences reflected
- [ ] Risk thresholds applied

### Output Quality
- [ ] Markdown report generated
- [ ] Excel workbook created (if enabled)
- [ ] Traceability matrix complete
- [ ] Confidence scores present
- [ ] Source references included

### Performance
- [ ] Analysis completed within expected time
- [ ] No errors in logs
- [ ] Checkpoints created successfully
- [ ] Memory usage acceptable

## Troubleshooting

### Issue: Context Not Loading

**Symptoms**:
- Warning message about context loading failure
- Generic requirement IDs used
- No org-specific customization

**Solutions**:
1. Check file path is correct
2. Verify YAML syntax is valid
3. Check file permissions
4. Review logs for specific error

```bash
# Validate YAML
python -c "import yaml; yaml.safe_load(open('org_context/config/org_config.yaml'))"

# Check logs
tail -f logs/rfp_analyzer.log
```

### Issue: Remote Context Loading Fails

**Symptoms**:
- Error loading from SharePoint/OneDrive
- Authentication failures
- Timeout errors

**Solutions**:
1. Verify credentials are set correctly
2. Check network connectivity
3. Verify URL is accessible
4. Test with local file first

```bash
# Test credentials
python -c "from org_context.remote_loaders import SharePointLoader; print('OK')"
```

### Issue: Unexpected Requirement Categorization

**Symptoms**:
- Requirements in wrong category
- Missing requirements
- Incorrect priorities

**Solutions**:
1. Review priority keywords in config
2. Check compliance framework mapping
3. Verify tech stack preferences
4. Examine agent prompts

### Issue: Performance Problems

**Symptoms**:
- Analysis takes too long
- High memory usage
- Timeout errors

**Solutions**:
1. Reduce document size
2. Increase timeout settings
3. Check API rate limits
4. Review checkpoint database size

```bash
# Clean checkpoint database
python -c "from core.state import cleanup_checkpoint_db; cleanup_checkpoint_db()"
```

## Best Practices

### 1. Version Control Your Configs
```bash
git add org_context/config/
git commit -m "Update org context for Q2 2026"
```

### 2. Document Changes
Keep a changelog for your org_context:
```markdown
## 2026-04-01
- Added PCI-DSS to compliance frameworks
- Updated tech stack to include FastAPI
- Modified risk thresholds for microservices
```

### 3. Test Before Production
Always test config changes with sample RFPs before using on real proposals.

### 4. Use Descriptive Names
Name your configs clearly:
- `org_config_healthcare.yaml`
- `org_config_finance.yaml`
- `org_config_startup.yaml`

### 5. Regular Reviews
Review and update your org_context quarterly to keep it current.

## Advanced Testing

### A/B Testing Different Configs

Compare two configurations side-by-side:

```bash
# Test Config A
python main.py analyze "$RFP" \
  --org-context config_a.yaml \
  --output-dir results/config_a

# Test Config B
python main.py analyze "$RFP" \
  --org-context config_b.yaml \
  --output-dir results/config_b

# Compare results
diff results/config_a/analysis.md results/config_b/analysis.md
```

### Batch Testing Multiple RFPs

Test consistency across multiple RFPs:

```bash
for rfp in org_context/examples/past_rfps/*.txt; do
  basename=$(basename "$rfp" .txt)
  python main.py analyze "$rfp" \
    --org-context org_context/config/org_config.yaml \
    --output-dir "test_results/batch/$basename"
done
```

### Performance Benchmarking

Measure analysis time with different configs:

```bash
#!/bin/bash
for config in org_context/config/*.yaml; do
  echo "Testing $config..."
  time python main.py analyze "$RFP" \
    --org-context "$config" \
    --output-dir "test_results/perf/$(basename $config .yaml)"
done
```

## Validation Criteria

### Functional Validation
- ✓ All SHALL requirements marked as MUST
- ✓ All SHOULD requirements marked as SHOULD
- ✓ All MAY requirements marked as COULD
- ✓ Compliance requirements correctly categorized
- ✓ Tech stack preferences reflected in recommendations

### Quality Validation
- ✓ Confidence scores > 0.7 for clear requirements
- ✓ Ambiguities flagged for vague language
- ✓ Risks identified for complex requirements
- ✓ Source references accurate
- ✓ No duplicate requirements

### Performance Validation
- ✓ Analysis completes in < 5 minutes
- ✓ Memory usage < 2GB
- ✓ No errors in logs
- ✓ Checkpoints created successfully

## Example Test Report

```markdown
# Test Report: Healthcare Context

**Date**: 2026-04-12
**RFP**: sample_healthcare_portal_rfp.txt
**Config**: org_config.yaml (Healthcare)

## Results Summary
- Total Requirements: 87
- Functional: 45
- Non-Functional: 25
- Compliance: 12
- Ambiguities: 3
- Risks: 2

## Context Application
✓ HIPAA requirements identified (12 instances)
✓ Healthcare terminology recognized (EHR, HL7, FHIR)
✓ Requirement IDs follow FR-HC-XXX format
✓ Security requirements aligned with healthcare standards
✓ Risk assessment considers healthcare factors

## Quality Metrics
- Average confidence: 0.82
- High confidence (>0.8): 75%
- Medium confidence (0.6-0.8): 20%
- Low confidence (<0.6): 5%

## Issues Found
- None

## Recommendations
- Config working as expected
- Consider adding more healthcare-specific risk indicators
- Update tech stack preferences for cloud-native architectures
```

## Next Steps

After completing these tests:

1. **Review Results**: Analyze how different contexts affect extraction
2. **Refine Config**: Adjust based on test results
3. **Document Findings**: Create a summary of what works best
4. **Share with Team**: Distribute learnings to stakeholders
5. **Iterate**: Continuously improve based on real-world usage

## Support

For questions or issues:
- Check logs: `./logs/rfp_analyzer.log`
- Review documentation: `README.md`, `INTEGRATION_GUIDE.md`
- Contact: support@acme.com

---

**Happy Testing!** 🚀

Remember: The goal is to find the configuration that best represents your organization's needs and produces the most accurate, relevant analysis results.