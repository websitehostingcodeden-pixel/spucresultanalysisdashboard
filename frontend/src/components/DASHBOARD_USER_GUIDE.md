# Section Performance Dashboard - User Guide

## Overview
The Section Performance Dashboard displays academic performance metrics organized by section, showing pass rates and grade breakdowns.

## Accessing the Dashboard

1. Login to the ARIS application
2. Navigate to **Sections** from the sidebar menu
3. The dashboard will load with the most recent upload selected

## Features

### 1. Upload Selector
- **Location**: Top of the dashboard
- **Function**: Select which data upload to analyze
- **Usage**: Click the dropdown and choose a date/filename to switch between different result batches

### 2. Performance Charts Tab (📈 Pass Rates & Grades)
This tab shows visual representations of section performance:

#### Summary Metrics Cards (4 cards)
- **Total Sections**: Number of academic sections in the selected upload
- **Avg Pass Rate**: Average passing percentage across all sections
- **Total Students**: Total number of students who appeared
- **Distinctions**: Total number of distinction holders

#### Pass Rate Chart
- Horizontal bar chart showing pass rate percentage for each section
- **Green bars**: ≥95% pass rate (excellent)
- **Yellow bars**: 85-94% pass rate (good)
- **Red bars**: <85% pass rate (needs attention)

#### Grade Distribution Chart
- Stacked bar chart showing how many students achieved each grade in each section
- **Categories**: 
  - Distinction (≥85%) - Yellow
  - First Class (60-84%) - Blue
  - Second Class (50-59%) - Orange
  - Pass Class (35-49%) - Pink
  - Failed (<35%) - Red

#### Grade Distribution Legend
Reference card explaining the color coding and grade ranges

### 3. Detailed Metrics Tab (📋 Detailed Metrics)
Shows comprehensive data in tabular format:

#### Section Filter
- Optional dropdown to focus on a specific section
- Default: Shows all sections
- Use to drill down into one section's complete data

#### Metrics Table
Displays all sections with columns including:
- Section name
- Stream (Science/Commerce)
- Enrolled students
- Appeared students
- Distinctions count
- First Class count
- Second Class count
- Pass Class count
- Failed count
- Pass percentage
- And more...

## Reading the Data

### Understanding Pass Rate Percentages
- Pass Rate % = (Number of students who passed / Number of students who appeared) × 100
- Passing grades include: Distinction, First Class, Second Class, Pass Class
- Failed students do not count toward pass rate

### Understanding Grade Distribution
- Each bar represents one section
- Segments show how many students fell into each grade category
- Hover over segments to see exact numbers

### Response Time
- A small indicator shows API response time (in milliseconds)
- Typical response: 27-50ms when cached

## Troubleshooting

### No Data Displayed
- **Reason**: Selected upload may not have section-level data
- **Solution**: Select a different upload from the dropdown

### Dashboard Loading Slowly
- **Reason**: Large dataset or network delay
- **Solution**: Wait for response or select smaller upload

### Charts Not Showing
- **Reason**: Browser cache or JavaScript issue
- **Solution**: Refresh the page (F5)

## Technical Details

### Data Source
- Fetches from backend API endpoints
- Real-time data from uploaded result files
- Automatically refreshes when upload is selected

### Browser Compatibility
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

### Performance
- Load time: <2 seconds
- Chart rendering: <200ms
- API response: 27-50ms (cached)

## Contact
For issues or questions, contact the system administrator.
