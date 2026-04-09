# IMPLEMENTATION CHECKLIST

## Before First Upload (Local Testing)

### 1. Environment Setup
- [ ] Python 3.10+ installed
- [ ] Virtual environment created: `python -m venv venv`
- [ ] Virtual environment activated
- [ ] Dependencies installed: `pip install -r requirements.txt`

### 2. Database
- [ ] Clear old DB: `rm db.sqlite3` (if migrating from old code)
- [ ] Run migrations: `python manage.py makemigrations`
- [ ] Run migrations: `python manage.py migrate`
- [ ] Create superuser: `python manage.py createsuperuser`

### 3. Local Testing
- [ ] Start server: `python manage.py runserver`
- [ ] Access admin: http://localhost:8000/admin
- [ ] Login with superuser
- [ ] Check models appear (StudentResult, UploadLog)
- [ ] Check new fields exist (result_class, retention_rate, etc.)

### 4. Test Upload Flow
- [ ] Create test Excel file with SCIENCE and COMMERCE sheets
- [ ] Use standard column names: "REG NO", "Grand Total", "Percentage"
- [ ] Upload via API or admin
- [ ] Check response includes quality_report
- [ ] Verify retention_rate > 80%
- [ ] Check records in StudentResult
- [ ] Verify result_class values assigned

### 5. Verify Defensive Patterns

#### Test Column Variation Detection
- [ ] Rename "REG NO" to "Register Number" in Excel
- [ ] Upload should still work ✓
- [ ] Rename "Grand Total" to "Total Marks"
- [ ] Upload should still work ✓

#### Test Duplicate Handling
- [ ] Add same student twice with different totals
- [ ] Upload should remove duplicate, keep higher score
- [ ] Check duplicates_removed count in response

#### Test Missing Data Handling
- [ ] Delete percentage column
- [ ] Upload should calculate percentages
- [ ] Check missing_percentage_filled count

#### Test Result Classification
- [ ] Verify students with 90% show "DISTINCTION"
- [ ] Verify students with 45% show "SECOND_CLASS"
- [ ] Check result_class values in admin

---

## Before Staging Deployment

### 6. Configuration
- [ ] `.env` configured with production values
- [ ] `SECRET_KEY` set to strong value
- [ ] `DEBUG=False` in production settings
- [ ] `ALLOWED_HOSTS` set correctly
- [ ] `FRONTEND_URL` matches frontend domain

### 7. Data Validation
- [ ] Backup current database
- [ ] Test with real college Excel file
- [ ] Check retention_rate makes sense
- [ ] Check quality metrics for anomalies
- [ ] Verify no "INCOMPLETE" result_class issues

### 8. API Testing
- [ ] Test `/api/upload/` endpoint
- [ ] Test `/api/results/` with filters
- [ ] Test `/api/stats/` endpoint
- [ ] Test `/api/uploads/` logs
- [ ] Verify JSON responses valid
- [ ] Check CORS headers correct

### 9. Admin Testing
- [ ] StudentResult list displays quality fields
- [ ] Can filter by result_class
- [ ] Can search by reg_no
- [ ] UploadLog shows all quality metrics
- [ ] Can view error messages
- [ ] Pagination works

### 10. Documentation
- [ ] Team read QUICK_START.md
- [ ] Team understands column mapping
- [ ] Team knows how to troubleshoot
- [ ] DATA_QUALITY.md available to team
- [ ] TROUBLESHOOTING.md bookmarked

---

## Before Production Deployment

### 11. Security Audit
- [ ] Secrets not in code (using .env)
- [ ] CSRF protection enabled
- [ ] CORS properly configured
- [ ] File upload validation working
- [ ] SQL injection prevention (ORM used)
- [ ] XSS prevention (JSON responses)

### 12. Performance Testing
- [ ] Upload 1000-record file - takes < 10 seconds
- [ ] Query 1000 results - takes < 1 second
- [ ] Filter by result_class - responsive
- [ ] Admin list page loads quickly
- [ ] No N+1 queries in Django debug toolbar

### 13. Error Handling
- [ ] Test with corrupt Excel file
- [ ] Test with missing sheets
- [ ] Test with huge file (> 100MB)
- [ ] Test with invalid column names
- [ ] All returns proper error with details

### 14. Monitoring Setup
- [ ] Logging configured
- [ ] Errors sent to monitoring (Sentry/etc)
- [ ] Database backups automated
- [ ] Disk space monitoring
- [ ] Error alerts configured

### 15. Deployment Script
- [ ] Django migrations automated
- [ ] Static files collected
- [ ] Media directory created
- [ ] Permissions set correctly
- [ ] Gunicorn/uWSGI configured

---

## First Week in Production

### 16. Monitoring
- [ ] Check `/api/uploads/` daily
- [ ] Monitor retention_rate trends
- [ ] Watch for errors in logs
- [ ] Check database size growth
- [ ] Monitor API response times

### 17. Data Quality
- [ ] Review quality metrics for each upload
- [ ] Alert if retention_rate < 70%
- [ ] Check for unexpected duplicates
- [ ] Verify result_class distribution
- [ ] Compare with expected grades

### 18. User Feedback
- [ ] Get feedback from admin users
- [ ] Ask about quality metrics usefulness
- [ ] Verify they understand report
- [ ] Adjust if column mappings need tweaking
- [ ] Document any school-specific patterns

### 19. Backup Verification
- [ ] Verify database backups created
- [ ] Test restore from backup
- [ ] Check backup size reasonable
- [ ] Verify backup frequency
- [ ] Document backup procedure

### 20. Update Runbook
- [ ] Document deployment process
- [ ] Document migration procedure
- [ ] Document common troubleshooting
- [ ] Document quality metrics targets
- [ ] Document on-call procedures

---

## Column Mapping Customization (If Needed)

### Identify Custom Columns
- [ ] Get Excel file from each college
- [ ] Document column names used
- [ ] Check if match COLUMN_MAPPINGS
- [ ] Note any unique naming

### Add Custom Mappings
- [ ] Edit `apps/results/services/config.py`
- [ ] Add college-specific column names to COLUMN_MAPPINGS
- [ ] Add reserved columns if subjects appear strange
- [ ] Test with sample file from that college
- [ ] Document in runbook

### Example
```python
# For College X that uses "Student Roll No"
COLUMN_MAPPINGS["reg_no"] = [
    "reg no",
    "student roll no",  # ← Added for College X
    ...
]
```

---

## Result Classification Customization (If Needed)

### Verify Thresholds Match School
- [ ] Get grading criteria from school
- [ ] Check if matches RESULT_CLASSIFICATION
- [ ] Confirm percentage cutoffs

### Adjust If Different
- [ ] Edit `apps/results/services/config.py`
- [ ] Update RESULT_CLASSIFICATION thresholds
- [ ] Restart Django
- [ ] Re-classify existing students (shell script)
- [ ] Verify results match school grading

### Example
```python
# If school uses different thresholds
RESULT_CLASSIFICATION = {
    "DISTINCTION": 90,      # Not 85
    "FIRST_CLASS": 70,      # Not 60
    "SECOND_CLASS": 55,     # Not 50
    "PASS": 40,             # Not 35
}
```

---

## Troubleshooting During Deployment

### If migrations fail
- [ ] See MIGRATION_GUIDE.md
- [ ] Check database permissions
- [ ] Verify Django version
- [ ] Try rollback: `manage.py migrate results 0001`

### If uploads fail
- [ ] Check column names in Excel
- [ ] Verify sheet names (SCIENCE, COMMERCE)
- [ ] See TROUBLESHOOTING.md
- [ ] Check retention_rate

### If admin errors
- [ ] Restart Django
- [ ] Verify migrations applied
- [ ] Check fieldsets in admin.py
- [ ] Verify model has fields

### If retention_rate low
- [ ] Review quality_report in API response
- [ ] Check which metrics are high
- [ ] Adjust column mappings if needed
- [ ] Validate Excel file format

---

## Post-Deployment (First Month)

### 21. Fine-Tuning
- [ ] Gather feedback on quality metrics
- [ ] Adjust column mappings based on schools
- [ ] Potentially adjust grade thresholds
- [ ] Optimize database if slow
- [ ] Document custom configurations

### 22. Team Training
- [ ] Train support team on quality reports
- [ ] Train data team on troubleshooting
- [ ] Document how to debug issues
- [ ] Create internal knowledge base
- [ ] Record training session

### 23. Documentation Updates
- [ ] Update README with production URL
- [ ] Document school-specific settings
- [ ] Document runbook procedures
- [ ] Create FAQ based on support tickets
- [ ] Archive old documentation

### 24. Metrics & Targets
- [ ] Set retention_rate target (typically > 85%)
- [ ] Set upload success rate target (> 95%)
- [ ] Set response time targets (< 2s)
- [ ] Create dashboard if possible
- [ ] Set up alerts for anomalies

---

## Sign-Off Checklist

Before calling it "complete":

- [ ] All tests pass locally
- [ ] All tests pass on staging
- [ ] Migrations verified on production-like DB
- [ ] Documentation complete and reviewed
- [ ] Team trained on system
- [ ] Monitoring configured
- [ ] Backups working
- [ ] Security audit passed
- [ ] Performance acceptable
- [ ] Quality metrics understood by stakeholders

---

## Monthly Maintenance

After launch, keep doing:

- [ ] Review upload quality metrics
- [ ] Check error logs for patterns
- [ ] Verify backups run successfully
- [ ] Monitor database growth
- [ ] Update documentation if needed
- [ ] Review performance metrics
- [ ] Collect user feedback
- [ ] Plan for improvements

---

## Emergency Procedures

If something breaks:

### Immediate (Emergency Page)
```bash
# 1. Stop application
systemctl stop aris-backend

# 2. Check logs
tail -100 /var/log/aris/django.log

# 3. Rollback if needed
git rollback previous-tag
python manage.py migrate

# 4. Restart
systemctl start aris-backend
```

### Quick Fixes
- [ ] Column mapping issue: Update config.py
- [ ] Result class wrong: Update thresholds
- [ ] Database locked: Restart Django
- [ ] High retention rate: Check data quality

### When to Contact Engineering
- [ ] Database corruption
- [ ] Migrations failing
- [ ] Cascading errors
- [ ] Performance degradation
- [ ] Security issues

---

**Print this checklist and mark off items as you go!**

Total items: ~100
Estimated time: 
- Local testing: 2-3 hours
- Staging: 1-3 hours  
- Production: 1 hour
- First week: 10-15 minutes daily
