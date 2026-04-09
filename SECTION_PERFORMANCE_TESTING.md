# Section Performance Dashboard - Testing & Verification Guide

## Quick Start (5 minutes)

### Step 1: Ensure Backend is Running
```powershell
cd aris_backend
python manage.py runserver
```
Expected output: `Server running at http://127.0.0.1:8000/`

### Step 2: Start Frontend
```powershell
cd frontend
npm run dev
```
Expected output: `VITE v... ready in ... ms`

### Step 3: Access Application
1. Open browser: `http://localhost:5173`
2. Login with your credentials
3. Upload a sample Excel file (if needed)
4. Navigate to **Sections** in sidebar
5. Verify dashboard loads with real data

---

## Verification Checklist

### Upload Selector ✓
- [ ] Upload dropdown shows recent files
- [ ] Files show filename, date, and status
- [ ] Selecting different uploads refreshes the data
- [ ] Default selects most recent upload
- [ ] Disabled state shows when no uploads exist

### Pass Rate Chart ✓
- [ ] Chart displays all sections with bars
- [ ] Green bars: pass rate ≥ 95%
- [ ] Yellow bars: pass rate 85-94%
- [ ] Red bars: pass rate < 85%
- [ ] All sections visible (no overlap)
- [ ] Tooltip shows on hover with section name and percentage
- [ ] Responsive: resizes on window change

### Grade Distribution Chart ✓
- [ ] Stacked bar chart shows all sections
- [ ] Five segments per bar: Distinction, First Class, Second Class, Pass Class, Failed
- [ ] Colors match the legend:
  - Amber (Distinction)
  - Blue (First Class)
  - Orange (Second Class)
  - Pink (Pass Class)
  - Red (Failed)
- [ ] Tooltip shows breakdown on hover
- [ ] Legend explains all grades
- [ ] Y-axis labeled "Number of Students"

### Summary Cards ✓
- [ ] **Total Sections**: Shows count of all sections
- [ ] **Avg Pass Rate**: Shows percentage, green text
- [ ] **Total Students**: Shows total appeared
- [ ] **Distinctions**: Shows count of distinction students
- [ ] All values update when upload changes

### Detailed Metrics Tab ✓
- [ ] Switch to "Detailed Metrics" tab (green)
- [ ] Section filter dropdown shows all sections
- [ ] Default shows "-- All Sections --"
- [ ] Table displays all expected columns:
  - Section, Stream, Enrolled, Absent, Appeared
  - Distinction, First Class, Second Class, Pass Class
  - Detained, Promoted, Pass %
- [ ] Click on column headers to sort
- [ ] Sorting arrows appear correctly (up/down)
- [ ] Filter by section works correctly

### Data Accuracy ✓
- [ ] **Passed count**: distinction + first_class + second_class + pass_class = expected
- [ ] **Promoted count**: appeared - detained (failed)
- [ ] **Pass percentage**: (passed / appeared) × 100 rounded
- [ ] **Stream derivation**:
  - PCMB → Science
  - PCMC → Science
  - PCME → Science
  - CEBA → Commerce
  - CSBA → Commerce
  - SEBA → Commerce
  - PEBA → Commerce
  - MBA → Commerce

### Responsive Design ✓
- [ ] Desktop (1920x1080): All charts visible side-by-side
- [ ] Tablet (768x1024):  Charts stack vertically
- [ ] Mobile (375x812): 
  - Dropdown full width
  - Charts readable
  - Table has horizontal scroll
  - No text overlap

### Error Handling ✓
- [ ] No uploads scenario: Shows "No uploads found" message
- [ ] API failure: Shows error message with description
- [ ] Empty section: Shows appropriate message
- [ ] Loading state: Shows spinner while fetching
- [ ] Invalid upload: Handled gracefully

### Performance ✓
- [ ] Dashboard loads in < 2 seconds
- [ ] Charts render smoothly (no jank)
- [ ] Interactions responsive (< 200ms)
- [ ] Response time shown correctly in ms
- [ ] No console errors

---

## Sample Test Data

You should see approximately:

**Science Stream**:
- PCMB A, B, C, D (~50 students each)
- PCMC F (~40 students)
- PCME E (~35 students)
- Overall pass rate: 94-97%

**Commerce Stream**:
- CEBA G1, G2, G3 (~50-60 students each)
- CSBA G3 (~35 students)
- SEBA G4 (~50 students)
- PEBA G6 (~40 students)
- MSBA/MEBA G5 (~30-35 students)
- Overall pass rate: 91-100%

---

## Troubleshooting

### Issue: Dashboard shows "No uploads found"
**Solution**: 
1. Go to Upload page (`/upload`)
2. Upload an Excel file with student results
3. Wait for processing (shows success/error)
4. Return to Sections page
5. Upload should appear in dropdown

### Issue: Charts don't display
**Solution**:
1. Check browser console (F12) for errors
2. Verify `/api/sections/{uploadId}/` returns data
3. Check if Recharts is installed: `npm list recharts`
4. Restart frontend: `npm run dev`

### Issue: Wrong pass percentages shown
**Solution**:
1. Verify backend computation in views
2. Check data transformation in SectionPerformance.jsx
3. Ensure: passed = distinction + first_class + second_class + pass_class
4. Check: pass_percentage = (passed / appeared) × 100

### Issue: Section names not deriving stream correctly
**Solution**:
1. Update `getStreamFromSection()` function in SectionPerformance.jsx
2. Add section patterns for your institution
3. Example: `if (section.startsWith('XYZ')) return 'NewStream'`

### Issue: API request returns 404
**Solution**:
1. Verify upload ID is valid
2. Check `/api/uploads/` returns non-empty list
3. Check backend logs for errors
4. Ensure upload processing completed successfully

---

## Live Data Inspection

### View API Response
1. Open browser DevTools (F12)
2. Go to Network tab
3. Reload page
4. Look for requests to `/api/uploads/` and `/api/sections/`
5. Click request, go to Response tab
6. Verify JSON structure matches expectations

### Check Console
1. F12 → Console
2. No red errors should appear
3. Should see log messages about fetch and transform
4. Can manually test: 
   ```javascript
   fetch('/api/uploads/')
     .then(r => r.json())
     .then(d => console.log(d))
   ```

---

## Expected Console Output

```
Loading uploads...
Uploads loaded: 2 files
Upload ID 5 selected
Fetching section data...
Section data received: 12 sections
Transform complete: [
  {section: "PCMB A", stream: "Science", appeared: 52, ...},
  ...
]
Response time: 34ms
```

---

## Performance Benchmarks

| Metric | Target | Acceptable |
|--------|--------|-----------|
| Initial load | < 1s | < 2s |
| Chart render | < 100ms | < 300ms |
| Upload selection | < 500ms | < 1s |
| Sort table | < 200ms | < 500ms |
| API response | 27-50ms | < 200ms |

---

## Browser Dev Tools Commands

Query total pass rate:
```javascript
data.reduce((a,b) => a + b.pass_percentage, 0) / data.length
```

Query total students:
```javascript
data.reduce((a,b) => a + b.appeared, 0)
```

Check section mapping:
```javascript
data.map(s => ({section: s.section, stream: s.stream}))
```

---

## Support Resources

- API Docs: See `ANALYTICS_ENGINE_DOCUMENTATION.md`
- Component Guide: See `SECTION_PERFORMANCE_COMPONENTS.md`
- Data Model: See `apps/results/models.py`
- API Endpoints: See `apps/results/api/urls.py`
