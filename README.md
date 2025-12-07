# Friction - Problem Discovery Search Engine

A comprehensive platform for discovering, validating, and tracking real-world problems and unmet needs. Built with a Perplexity Finance-inspired design aesthetic.

## Overview

Friction is a problem discovery engine that helps founders, researchers, and innovators find validated opportunities, track emerging needs, and solve real problems. The platform aggregates user-submitted problems, tracks validation signals, and provides market intelligence for opportunity discovery.

## Features

### Core Pages

1. **Homepage / Discovery Feed** (`index.html`)
   - Hero section with AI-powered search
   - Trending opportunities with growth metrics
   - Category browsing (8 core domains)
   - Recent signals feed
   - Real-time validation tracking

2. **Opportunity Detail Page** (`index.html#detail`)
   - Validation growth charts
   - Key metrics dashboard
   - Problem description and opportunity analysis
   - Solutions in development tracking
   - Discussion thread with comments
   - Related opportunities sidebar
   - "I Need This Too" validation button

3. **Submit Opportunity Flow** (`index.html#submit`)
   - Multi-step submission form
   - Duplicate detection
   - Category selection
   - Severity/impact rating
   - Privacy settings (anonymous posting)
   - Draft saving capability

4. **Innovation Dashboard** (`index.html#dashboard`)
   - Market opportunity highlights
   - Advanced filtering system
   - Trending opportunities table
   - Statistics overview
   - Watchlist management

5. **Opportunity Deep Dive** (`index.html#deepdive`)
   - Comprehensive market analysis
   - Validation scoring
   - Investment intelligence
   - Willingness-to-pay signals
   - Competitive landscape analysis
   - Export functionality (PDF, CSV)

6. **Pricing Page** (`index.html#pricing`)
   - 4-tier pricing structure (Free, Pro, Business, Enterprise)
   - Feature comparison
   - Value propositions for each tier

### Additional Pages

7. **Search Results** (`search.html`)
   - Full-text search functionality
   - Filter chips for categories and criteria
   - Search result cards with metadata
   - Sidebar with refinement options
   - Related searches suggestions

8. **Category Browse** (`category.html`)
   - Category-specific landing pages
   - Subcategory navigation
   - Category statistics
   - Filtered opportunity listings
   - Sorting options (Trending, Most Validated, Recent, Largest Market)

9. **User Profile** (`profile.html`)
   - User information and badges
   - Activity statistics
   - Activity feed
   - Validated opportunities list
   - Shared problems tracking
   - Watchlist management
   - Impact points system

10. **Settings** (`settings.html`)
    - Profile information editing
    - Notification preferences
    - Privacy settings
    - Account security (password, 2FA)
    - Subscription & billing management
    - Data export
    - Account deletion

11. **Authentication**
    - Sign In (`login.html`)
    - Sign Up (`signup.html`)
    - Password Reset (`reset-password.html`)
    - Social login support (Google, GitHub)

## Design System

### Color Palette
- **Background**: `#F8F9FA` - Light gray background
- **Surface**: `#FFFFFF` - White cards and panels
- **Primary**: `#1A73E8` - Google Blue for CTAs and accents
- **Text**: `#202124` - Near-black for primary text
- **Secondary Text**: `#5F6368` - Medium gray for secondary information
- **Success**: `#0D9488` - Teal for positive indicators
- **Danger**: `#DC2626` - Red for warnings and destructive actions

### Typography
- **Font Family**: Inter, SF Pro Display, Segoe UI, system-ui
- **Headings**: 600-700 weight, varied sizes
- **Body**: 400-500 weight, 14-16px
- **Antialiasing**: Enabled for crisp text rendering

### Components
- **Buttons**: 8px border radius, subtle shadows, hover states
- **Cards**: White background, 1px border, subtle shadows
- **Inputs**: 1.5px border, focus states with blue ring
- **Tabs**: Underline style with 2px bottom border
- **Badges**: Pill-shaped with category colors
- **Charts**: SVG-based with gradients

## Interactive Features

### JavaScript Functionality
- Tab navigation across multi-view pages
- Search with live suggestions
- Category filtering with active states
- Validation button interactions with counters
- Toggle switches for settings
- Form validation and submission
- Card click-through navigation
- Real-time chart rendering

### User Interactions
- "I Need This Too" validation system
- Agree buttons with vote counting
- Category card selection
- Watchlist management
- Comment system
- Share and export options

## Pages Navigation Map

```
index.html (Homepage)
├── login.html (Sign In)
├── signup.html (Sign Up)
│   └── reset-password.html (Password Reset)
├── search.html (Search Results)
├── category.html (Category Browse)
├── profile.html (User Profile)
│   └── settings.html (Account Settings)
└── [Internal Tabs]
    ├── #consumer (Discovery Feed)
    ├── #submit (Submit Problem)
    ├── #detail (Problem Detail)
    ├── #dashboard (Research Dashboard)
    ├── #deepdive (Deep Dive Analysis)
    └── #pricing (Pricing Plans)
```

## Technology Stack

- **Frontend**: Pure HTML5, CSS3, Vanilla JavaScript
- **Design**: Custom CSS with CSS Variables
- **Icons**: Emoji-based (no external dependencies)
- **Charts**: SVG-based custom charts
- **Responsive**: Mobile-first responsive design

## File Structure

```
/
├── index.html              # Main application (6 integrated pages)
├── login.html              # Authentication - Sign in
├── signup.html             # Authentication - Sign up
├── reset-password.html     # Authentication - Password reset
├── search.html             # Search results page
├── category.html           # Category browse page
├── profile.html            # User profile page
├── settings.html           # Account settings page
└── README.md              # This file
```

## Key Metrics Tracked

- **Validations**: User confirmations of problems
- **Growth Rate**: Week-over-week percentage increase
- **Market Size**: Total addressable market estimates
- **Impact Points**: User contribution scoring
- **Engagement**: Comments, shares, watchlist additions

## Categories

1. 💼 Work & Productivity
2. 💰 Money & Finance
3. 🏥 Health & Wellness
4. 🏠 Home & Living
5. 💻 Technology
6. 🚗 Transportation
7. 📚 Education
8. 🛒 Shopping & Services

## Data Model (Conceptual)

### Opportunity
- Title
- Description
- Category
- Severity/Impact
- Validation count
- Growth rate
- Market size estimate
- Submission date
- Author (can be anonymous)

### User
- Name
- Email
- Bio
- Badges
- Statistics (validations, submissions, watchlist)
- Impact points

### Validation
- User
- Opportunity
- Timestamp

### Comment
- User
- Opportunity
- Content
- Timestamp
- Likes

## Future Enhancements

- Backend API integration
- Real-time WebSocket updates
- Machine learning for trend detection
- Advanced analytics dashboard
- API for third-party integrations
- Mobile native applications
- Email notification system
- Payment processing integration
- Data export automation

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

## Getting Started

1. Open `index.html` in a modern web browser
2. Navigate through tabs to explore different sections
3. Click on cards and opportunities to see interactions
4. Test authentication flows through login/signup pages
5. Explore search and category filtering

## Contributing

This is a prototype/MVP demonstrating the core user experience and design system for a problem discovery platform.

## License

Proprietary - All rights reserved

---

**Built with** ❤️ **for innovators, founders, and problem solvers**
