# Section Performance Dashboard - Setup & Integration Guide

## Quick Setup

### 1. Add Route to App

Edit `src/routes/AppRoutes.js`:

```javascript
import SectionPerformancePage from '../pages/SectionPerformancePage'

export const routes = [
  // ... existing routes ...
  {
    path: '/section-performance',
    element: <SectionPerformancePage />
  }
]
```

### 2. Install Dependencies (if needed)

All required packages are already in `package.json`:
- ✅ recharts
- ✅ lucide-react
- ✅ tailwindcss

### 3. Run Frontend

```bash
cd frontend
npm run dev
```

Then visit: `http://localhost:5173/section-performance`

---

## Component Tree & Data Flow

```
┌─────────────────────────────────────────────┐
│         SectionPerformancePage              │
│     (Wrapper with Sidebar + Topbar)         │
│                   │                         │
│                   ▼                         │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│       SectionPerformance (Container)        │
│                                             │
│  State:                                     │
│  • data: Array<SectionData>                │
│  • loading: boolean                         │
│  • error: string | null                     │
│  • computedInsights: InsightMetrics         │
│                                             │
│  useEffect: Fetch data on mount             │
│  useMemo: Compute insights                  │
└──────────────────┬──────────────────────────┘
                   │
        ┌──────────┼──────────┬──────────┐
        │          │          │          │
        ▼          ▼          ▼          ▼
   ┌─────────┐ ┌──────────┐ ┌────────┐ ┌───────┐
   │Insights │ │BarChart  │ │Breakdown│ │ Table │
   │ (Cards) │ │ (Bars)   │ │ (Stack)  │ (Rows)│
   └─────────┘ └──────────┘ └────────┘ └───────┘
   Props:     Props:        Props:      Props:
   • insights • data       • data      • data
```

---

## File Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── SectionPerformance.jsx              ← Main container
│   │   ├── SectionBarChart.jsx                 ← Pass % chart
│   │   ├── SectionBreakdownChart.jsx           ← Grade stacked chart
│   │   ├── SectionInsights.jsx                 ← Insight cards
│   │   ├── SectionTable.jsx                    ← Support table
│   │   ├── SECTION_PERFORMANCE_COMPONENTS.md   ← Architecture guide
│   │   ├── SECTION_PERFORMANCE_RENDERING.md    ← Visual guide
│   │   └── [existing components...]
│   │
│   ├── pages/
│   │   ├── SectionPerformancePage.jsx          ← Page wrapper
│   │   └── [existing pages...]
│   │
│   ├── routes/
│   │   └── AppRoutes.js                        ← ADD ROUTE HERE
│   │
│   └── [existing structure...]
```

---

## Props Interface

### SectionPerformance (Container)
**Props**: None (self-contained, fetches own data)

**Internal State**:
```javascript
data: [
  {
    section: string,
    stream: 'Science' | 'Commerce',
    enrolled: number,
    absent: number,
    appeared: number,
    distinction: number,
    first_class: number,
    second_class: number,
    pass_class: number,
    detained: number,
    promoted: number,
    pass_percentage: number
  }
]

computedInsights: {
  avgPassPercentage: string,      // "96.4"
  totalAppeared: number,          // 628
  bestSection: SectionData,       // Full section object
  worstSection: SectionData,      // Full section object
  totalDetained: number,          // 15
  avgDetentionRate: string        // "2.4"
}
```

### SectionBarChart
```javascript
props: {
  data: Array<{
    section: string,
    pass_percentage: number
  }>
}
```

### SectionBreakdownChart
```javascript
props: {
  data: Array<{
    section: string,
    distinction: number,
    first_class: number,
    second_class: number,
    pass_class: number,
    detained: number,
    appeared: number
  }>
}
```

### SectionInsights
```javascript
props: {
  insights: {
    avgPassPercentage: string,
    totalAppeared: number,
    bestSection: SectionData,
    worstSection: SectionData,
    totalDetained: number,
    avgDetentionRate: string
  }
}
```

### SectionTable
```javascript
props: {
  data: Array<SectionData>
}
```

---

## Styling Details

### Tailwind Classes Used

```
Layout:
- grid: Grid layout
- gap-4/6/8: Spacing between items
- col-span-1/2/3: Column spanning
- lg:col-span-2: Large screen columns

Backgrounds:
- bg-gray-50/100: Page backgrounds
- bg-white: Card/table backgrounds
- bg-gradient-to-br: Gradient backgrounds
- from-green-50 to-green-100: Color gradients
- from-blue-50 to-blue-100: Insight card gradients

Text:
- text-3xl: Large titles
- text-lg/xl: Section headers
- font-bold/semibold: Font weights
- text-gray-900/700/600: Text colors
- text-green-700/yellow-700/red-700: Colored text

Borders & Shadows:
- border: Default border
- border-gray-200: Light borders
- rounded-lg: Rounded corners
- shadow-sm/md: Drop shadows
- hover:shadow-md: Hover effects

Responsive:
- md:grid-cols-2: Tablet layout
- lg:grid-cols-3/4: Desktop layout
- lg:col-span-2: Spanning on large screens
- h-screen: Full height
- overflow-auto: Scrollable areas
```

### Color Palette

```
Performance Levels:
#10B981  Green   ≥95% excellent
#F59E0B  Yellow  85-94% good
#EF4444  Red     <85% needs attention

Grade Categories:
#8B5CF6  Purple  Distinction
#3B82F6  Blue    First Class
#10B981  Green   Second Class
#F59E0B  Yellow  Pass Class
#EF4444  Red     Detained

Variants:
#E5E7EB  Gray    Grid lines, borders
#6B7280  Gray    Axis labels
#9CA3AF  Gray    Light text
```

---

## Error Handling

Currently implemented in `SectionPerformance.jsx`:

```javascript
try {
  // Fetch data
  setData(SAMPLE_DATA)
  setError(null)
} catch (err) {
  setError('Failed to load section data')
  console.error(err)
}
```

For API integration, add retry logic:

```javascript
const maxRetries = 3
let retries = 0

const fetchWithRetry = async () => {
  try {
    const response = await fetch(API_URL)
    if (!response.ok) throw new Error(response.statusText)
    return await response.json()
  } catch (err) {
    if (retries < maxRetries) {
      retries++
      await new Promise(r => setTimeout(r, 1000))
      return fetchWithRetry()
    }
    throw err
  }
}
```

---

## Performance Optimization

### Already Implemented:
- ✅ **useMemo for insights**: Prevents recomputation on every render
- ✅ **useMemo for chart data**: Only recompiles if data changes
- ✅ **Recharts optimization**: Built-in memoization
- ✅ **Responsive container**: Dynamic sizing, no layout shift

### Can Add Later:
- React.memo() on child components to prevent unnecessary re-renders
- Pagination on table (if >1000 rows)
- Virtual scrolling on large tables
- Server-side sorting/filtering

---

## API Integration Checklist

When ready to connect to backend:

- [ ] Update `SectionPerformance.jsx` fetch URL
- [ ] Replace hardcoded `SAMPLE_DATA` with actual API call
- [ ] Add error handling for network failures
- [ ] Add retry logic for timeout scenarios
- [ ] Test with real backend data
- [ ] Verify all sections render correctly
- [ ] Confirm color coding matches actual pass %
- [ ] Validate sort order in table
- [ ] Test on slow networks (DevTools throttling)

---

## Frontend API Endpoint Expected

```
GET http://localhost:8000/api/sections/sample/

Response (JSON Array):
[
  {
    "section": "PCMB A",
    "stream": "Science",
    "enrolled": 52,
    "absent": 0,
    "appeared": 52,
    "distinction": 8,
    "first_class": 30,
    "second_class": 12,
    "pass_class": 0,
    "detained": 2,
    "promoted": 50,
    "pass_percentage": 96
  },
  ...12 total sections
]
```

---

## Testing Instructions

### Unit Tests (Optional)

```javascript
// Test: SectionBarChart renders with correct colors
test('renders green bar for 96% pass rate', () => {
  const data = [{ section: 'Test', pass_percentage: 96 }]
  render(<SectionBarChart data={data} />)
  // Assert green color
})

// Test: Insights computes correctly
test('computes average pass percentage', () => {
  const insights = computed({
    data: [
      { pass_percentage: 100 },
      { pass_percentage: 90 }
    ]
  })
  expect(insights.avgPassPercentage).toBe('95.0')
})
```

### Manual Testing

1. **Load page**: `/section-performance`
   - ✅ Loads < 2s
   - ✅ No console errors

2. **Check insights**:
   - ✅ Highest = CEBA G1 (100%)
   - ✅ Lowest = PCME E (94%)
   - ✅ Average ≈ 96.4%
   - ✅ Detention ≈ 2.4%

3. **Check charts**:
   - ✅ 12 bars visible
   - ✅ Color coding accurate
   - ✅ Smooth animations
   - ✅ Tooltips work on hover

4. **Check table**:
   - ✅ All 12 rows visible
   - ✅ Click headers to sort
   - ✅ Color-coded cells
   - ✅ Scrollable on mobile

5. **Responsive**:
   - ✅ Mobile (< 640px): Single column
   - ✅ Tablet (640-1024px): 2 columns
   - ✅ Desktop (> 1024px): 4 columns + 2-column chart

---

## Troubleshooting

### Issue: Components not importing
**Solution**: Ensure files are in `src/components/` directory

### Issue: Tailwind styles not applying
**Solution**: Check `tailwind.config.js` includes necessary content paths:
```javascript
content: ['./src/**/*.{jsx,js}']
```

### Issue: Charts not rendering
**Solution**: Verify Recharts is installed:
```bash
npm install recharts
```

### Issue: Slow performance
**Solution**: 
- Clear browser cache
- Check DevTools Performance tab
- Ensure `useMemo` is used in parent
- Profile with React Developer Tools

### Issue: Data not loading
**Solution**:
- Check browser console for errors
- Verify API endpoint is correct
- Check backend is running on port 8000
- Try direct API call in Postman: `GET http://localhost:8000/api/sections/sample/`

---

## Next Steps

1. ✅ Implement 5 modular components
2. ✅ Test with hardcoded data
3. ⏳ Create **SectionFilters** component
   - Stream dropdown (Science | Commerce | All)
   - Section multi-select
   - Filter button
4. ⏳ Replace hardcoded data with API call
5. ⏳ Add error handling + retry logic
6. ⏳ Deploy to production

---

## File Checklist

- ✅ `SectionPerformance.jsx` (main container)
- ✅ `SectionBarChart.jsx` (pass % chart)
- ✅ `SectionBreakdownChart.jsx` (grade stacked chart)
- ✅ `SectionInsights.jsx` (insight cards)
- ✅ `SectionTable.jsx` (sortable table)
- ✅ `SectionPerformancePage.jsx` (page wrapper)
- ✅ `SECTION_PERFORMANCE_COMPONENTS.md` (architecture)
- ✅ `SECTION_PERFORMANCE_RENDERING.md` (visual guide)
- ✅ `SECTION_PERFORMANCE_SETUP.md` (this file)

**Ready to integrate!**
